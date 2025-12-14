"""
Background jobs for subscription management.
Run these jobs daily via cron or a scheduler like APScheduler.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from app.models.user import User
from app.services.subscription_service import PlanSubscriptionService
from app.utils.email_service import email_service

logger = logging.getLogger(__name__)


async def check_expiring_subscriptions(days_before: int = 3) -> int:
    """
    Find users whose subscriptions are expiring soon and send reminder emails.
    
    Args:
        days_before: Days before expiry to send reminder (default: 3)
    
    Returns:
        Number of reminder emails sent
    """
    now = datetime.now(timezone.utc)
    expiry_threshold = now + timedelta(days=days_before)
    
    # Find users expiring within the threshold
    expiring_users = await User.find({
        "subscription_end_date": {
            "$gt": now,
            "$lt": expiry_threshold
        },
        "subscription": {"$in": ["pro", "ultra"]}
    }).to_list()
    
    sent_count = 0
    for user in expiring_users:
        try:
            days_remaining = (user.subscription_end_date - now).days
            await email_service.send_subscription_expiring_email(user, days_remaining)
            sent_count += 1
            logger.info(f"Sent expiry reminder to {user.email} ({days_remaining} days remaining)")
        except Exception as e:
            logger.error(f"Failed to send expiry reminder to {user.email}: {e}")
    
    logger.info(f"Sent {sent_count} subscription expiry reminders")
    return sent_count


async def check_expired_subscriptions(db=None) -> int:
    """
    Find users with expired subscriptions, downgrade them, and send notifications.
    
    Returns:
        Number of users downgraded
    """
    now = datetime.now(timezone.utc)
    
    # Find expired users
    expired_users = await User.find({
        "subscription_end_date": {"$lt": now},
        "subscription": {"$in": ["pro", "ultra"]}
    }).to_list()
    
    if not expired_users:
        logger.info("No expired subscriptions found")
        return 0
    
    downgraded_count = 0
    plan_service = PlanSubscriptionService(db)
    
    for user in expired_users:
        try:
            # Downgrade user
            await plan_service.downgrade_user(user)
            
            # Send expiry notification
            await email_service.send_subscription_expired_email(user)
            
            downgraded_count += 1
            logger.info(f"Downgraded expired user: {user.email}")
        except Exception as e:
            logger.error(f"Failed to downgrade user {user.email}: {e}")
    
    logger.info(f"Downgraded {downgraded_count} expired subscriptions")
    return downgraded_count


async def run_daily_subscription_jobs(db=None) -> dict:
    """
    Run all daily subscription maintenance jobs.
    Call this function daily via cron or scheduler.
    
    Returns:
        Summary of job results
    """
    logger.info("Starting daily subscription jobs...")
    
    results = {
        "expiring_reminders_sent": 0,
        "expired_downgraded": 0,
        "run_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Send expiry reminders (3 days before)
        results["expiring_reminders_sent"] = await check_expiring_subscriptions(days_before=3)
    except Exception as e:
        logger.error(f"Failed to check expiring subscriptions: {e}")
        results["expiring_error"] = str(e)
    
    try:
        # Downgrade expired subscriptions
        results["expired_downgraded"] = await check_expired_subscriptions(db)
    except Exception as e:
        logger.error(f"Failed to check expired subscriptions: {e}")
        results["expired_error"] = str(e)
    
    logger.info(f"Daily subscription jobs completed: {results}")
    return results


# Admin endpoint helper for manual triggering
async def get_subscription_stats() -> dict:
    """
    Get subscription statistics for admin dashboard.
    """
    now = datetime.now(timezone.utc)
    
    # Count users by subscription type
    free_count = await User.find({"subscription": "free"}).count()
    pro_count = await User.find({"subscription": "pro"}).count()
    ultra_count = await User.find({"subscription": "ultra"}).count()
    
    # Count PAYG users
    payg_count = await User.find({"subscription_plan": "payg"}).count()
    
    # Count expiring soon (next 7 days)
    expiring_threshold = now + timedelta(days=7)
    expiring_count = await User.find({
        "subscription_end_date": {"$gt": now, "$lt": expiring_threshold},
        "subscription": {"$in": ["pro", "ultra"]}
    }).count()
    
    # Calculate revenue (total_spent_inr)
    all_users = await User.find({"total_spent_inr": {"$gt": 0}}).to_list()
    total_revenue = sum(u.total_spent_inr for u in all_users)
    
    return {
        "subscriptions": {
            "free": free_count,
            "payg": payg_count,
            "pro": pro_count,
            "ultra": ultra_count,
            "total_paid": pro_count + ultra_count + payg_count
        },
        "expiring_soon": expiring_count,
        "total_revenue_inr": total_revenue,
        "as_of": now.isoformat()
    }
