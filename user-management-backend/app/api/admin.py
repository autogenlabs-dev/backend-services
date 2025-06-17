from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, TokenUsageLog, SubscriptionPlan, UserSubscription
from ..services.stripe_service import StripeService
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json

router = APIRouter(prefix="/admin", tags=["Admin"], include_in_schema=True)

def require_admin(current_user: User = Depends(get_current_user)):
    # RBAC: allow admin and superadmin roles (admin has all access)
    if getattr(current_user, "role", "user") not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/users")
def list_all_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> List[dict]:
    users = db.query(User).all()
    return [
        {"id": str(u.id), "email": u.email, "is_active": u.is_active, "created_at": u.created_at} for u in users
    ]

@router.get("/usage-stats")
async def usage_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: Optional[str] = Query("day", description="Group by: day, week, month, provider, model"),
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    """
    Get detailed token usage statistics with flexible grouping and filtering options.
    
    Returns comprehensive analytics on token usage across the platform.
    """
    try:
        # Parse date filters
        date_filters = []
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            date_filters.append(TokenUsageLog.created_at >= start_dt)
        else:
            # Default to last 30 days
            start_dt = datetime.now() - timedelta(days=30)
            date_filters.append(TokenUsageLog.created_at >= start_dt)
            
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            date_filters.append(TokenUsageLog.created_at <= end_dt)
        
        # Base query for stats
        total_tokens_query = (
            await db.execute(
                select(func.sum(TokenUsageLog.tokens_used))
                .where(and_(*date_filters))
            )
        )
        total_tokens = total_tokens_query.scalar() or 0
        
        # Total cost
        total_cost_query = (
            await db.execute(
                select(func.sum(TokenUsageLog.cost_usd))
                .where(and_(*date_filters))
            )
        )
        total_cost = total_cost_query.scalar() or 0.0
        
        # Active users query
        active_users_query = (
            await db.execute(
                select(func.count(func.distinct(TokenUsageLog.user_id)))
                .where(and_(*date_filters))
            )
        )
        active_users = active_users_query.scalar() or 0
        
        # Group by requested dimension
        grouped_data = []
        
        if group_by == "day":
            # Group by day
            date_trunc = func.date(TokenUsageLog.created_at)
            group_query = (
                await db.execute(
                    select(
                        date_trunc.label("date"),
                        func.sum(TokenUsageLog.tokens_used).label("tokens"),
                        func.sum(TokenUsageLog.cost_usd).label("cost"),
                        func.count(func.distinct(TokenUsageLog.user_id)).label("users")
                    )
                    .where(and_(*date_filters))
                    .group_by(date_trunc)
                    .order_by(date_trunc)
                )
            )
            
            for row in group_query.all():
                grouped_data.append({
                    "date": row.date.strftime("%Y-%m-%d"),
                    "tokens": row.tokens,
                    "cost_usd": float(row.cost) if row.cost else 0.0,
                    "unique_users": row.users
                })
                
        elif group_by == "provider":
            # Group by LLM provider
            group_query = (
                await db.execute(
                    select(
                        TokenUsageLog.provider,
                        func.sum(TokenUsageLog.tokens_used).label("tokens"),
                        func.sum(TokenUsageLog.cost_usd).label("cost"),
                        func.count(func.distinct(TokenUsageLog.user_id)).label("users")
                    )
                    .where(and_(*date_filters))
                    .group_by(TokenUsageLog.provider)
                    .order_by(desc("tokens"))
                )
            )
            
            for row in group_query.all():
                grouped_data.append({
                    "provider": row.provider,
                    "tokens": row.tokens,
                    "cost_usd": float(row.cost) if row.cost else 0.0,
                    "unique_users": row.users
                })
                
        elif group_by == "model":
            # Group by model
            group_query = (
                await db.execute(
                    select(
                        TokenUsageLog.model_name,
                        func.sum(TokenUsageLog.tokens_used).label("tokens"),
                        func.sum(TokenUsageLog.cost_usd).label("cost"),
                        func.count(func.distinct(TokenUsageLog.user_id)).label("users")
                    )
                    .where(and_(*date_filters))
                    .group_by(TokenUsageLog.model_name)
                    .order_by(desc("tokens"))
                )
            )
            
            for row in group_query.all():
                grouped_data.append({
                    "model": row.model_name,
                    "tokens": row.tokens,
                    "cost_usd": float(row.cost) if row.cost else 0.0,
                    "unique_users": row.users
                })
                
        return {
            "summary": {
                "total_tokens": total_tokens,
                "total_cost_usd": float(total_cost),
                "active_users": active_users,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": (end_dt if end_date else datetime.now()).strftime("%Y-%m-%d"),
            },
            "grouped_by": group_by,
            "data": grouped_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate usage statistics: {str(e)}")

@router.get("/revenue")
async def revenue_stats(
    period: str = Query("month", description="Period: month, quarter, year, all"),
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    """
    Get revenue statistics from Stripe with subscription analytics.
    
    Returns MRR, growth, churn rate, and other key business metrics.
    """
    try:
        # Initialize Stripe service
        stripe_service = StripeService()
        
        # Get current date for calculating periods
        now = datetime.now()
        
        # Set time period for query
        if period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:  # all
            start_date = now - timedelta(days=3650)  # 10 years back
        
        # Get subscription data from Stripe
        stripe_data = await stripe_service.get_subscription_analytics(period)
        
        # Query local subscription data
        active_subs_query = (
            await db.execute(
                select(
                    UserSubscription.status, 
                    func.count(UserSubscription.id).label("count"),
                    SubscriptionPlan.name
                )
                .join(SubscriptionPlan)
                .group_by(UserSubscription.status, SubscriptionPlan.name)
            )
        )
        
        # Process subscription data
        subscription_status = {}
        for status, count, plan_name in active_subs_query:
            if plan_name not in subscription_status:
                subscription_status[plan_name] = {}
            subscription_status[plan_name][status] = count
        
        # Get revenue from token usage
        revenue_from_usage_query = (
            await db.execute(
                select(func.sum(TokenUsageLog.cost_usd))
                .where(TokenUsageLog.created_at >= start_date)
            )
        )
        usage_revenue = revenue_from_usage_query.scalar() or 0.0
        
        # Combine data
        return {
            "period": period,
            "summary": {
                "mrr_usd": stripe_data.get("mrr_usd", 0.0),
                "total_revenue_usd": stripe_data.get("total_revenue_usd", 0.0),
                "usage_revenue_usd": float(usage_revenue),
                "subscription_count": stripe_data.get("subscription_count", 0),
                "churn_rate": stripe_data.get("churn_rate", 0.0),
                "growth_rate": stripe_data.get("growth_rate", 0.0),
            },
            "subscription_status": subscription_status,
            "stripe_data": stripe_data
        }
        
    except Exception as e:
        # Fallback to database-only stats if Stripe integration fails
        try:
            active_subs_query = (
                await db.execute(
                    select(
                        UserSubscription.status, 
                        func.count(UserSubscription.id).label("count")
                    )
                    .group_by(UserSubscription.status)
                )
            )
            
            subscription_status = {status: count for status, count in active_subs_query.all()}
            
            return {
                "period": period,
                "summary": {
                    "mrr_usd": 0.0,
                    "total_revenue_usd": 0.0,
                    "subscription_count": sum(subscription_status.values()),
                    "churn_rate": 0.0,
                    "growth_rate": 0.0,
                    "stripe_integration_error": str(e)
                },
                "subscription_status": subscription_status
            }
            
        except Exception as inner_e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve revenue statistics: {str(inner_e)}"
            )

@router.put("/users/{user_id}/plan")
async def change_user_plan(
    user_id: str, 
    plan_name: str, 
    update_stripe: bool = Query(True, description="Update Stripe subscription if applicable"),
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    """
    Change a user's subscription plan with administrative privileges.
    
    Optionally updates the corresponding Stripe subscription if the user has one.
    """
    try:
        # Find the plan
        plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == plan_name))
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Find the user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find the user's subscription
        sub_result = await db.execute(select(UserSubscription).where(UserSubscription.user_id == user_id))
        sub = sub_result.scalar_one_or_none()
        
        if not sub:
            # Create a new subscription
            sub = UserSubscription(user_id=user_id, plan_id=plan.id, status="active")
            db.add(sub)
        else:
            # Update existing subscription
            sub.plan_id = plan.id
            sub.status = "active"
        
        # Update user's subscription level
        user.subscription = plan_name
        user.monthly_limit = plan.monthly_tokens
        
        # Reset token usage to give full allocation for new plan
        user.tokens_remaining = plan.monthly_tokens
        user.reset_date = datetime.now() + timedelta(days=30)
        
        await db.commit()
        
        # Update Stripe subscription if requested
        stripe_result = {}
        if update_stripe and user.stripe_customer_id:
            try:
                stripe_service = StripeService()
                stripe_result = await stripe_service.change_subscription_plan(
                    customer_id=user.stripe_customer_id,
                    plan_name=plan_name
                )
            except Exception as stripe_error:
                # Log the error but don't fail the function
                stripe_result = {"stripe_error": str(stripe_error)}
        
        return {
            "message": f"User {user_id} set to plan {plan_name}",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "subscription": user.subscription,
                "tokens_remaining": user.tokens_remaining
            },
            "stripe": stripe_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user plan: {str(e)}")

@router.get("/system-stats")
async def system_stats(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    """
    Get system statistics for monitoring the platform.
    
    Returns user counts, subscription breakdowns, and token usage metrics.
    """
    try:
        # Total users
        users_count_query = await db.execute(select(func.count(User.id)))
        total_users = users_count_query.scalar() or 0
        
        # Users by subscription tier
        users_by_plan_query = await db.execute(
            select(
                User.subscription,
                func.count(User.id).label("count")
            )
            .group_by(User.subscription)
        )
        users_by_plan = {plan: count for plan, count in users_by_plan_query.all()}
        
        # Active users (logged in last 30 days)
        active_users_query = await db.execute(
            select(func.count(User.id))
            .where(User.last_login_at >= datetime.now() - timedelta(days=30))
        )
        active_users = active_users_query.scalar() or 0
        
        # Monthly token usage
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_token_usage_query = await db.execute(
            select(func.sum(TokenUsageLog.tokens_used))
            .where(TokenUsageLog.created_at >= current_month_start)
        )
        monthly_tokens = monthly_token_usage_query.scalar() or 0
        
        # Total token usage all time
        all_time_token_usage_query = await db.execute(select(func.sum(TokenUsageLog.tokens_used)))
        all_time_tokens = all_time_token_usage_query.scalar() or 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "users": {
                "total": total_users,
                "active_last_30d": active_users,
                "by_tier": users_by_plan
            },
            "tokens": {
                "current_month": monthly_tokens,
                "all_time": all_time_tokens
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system statistics: {str(e)}")
