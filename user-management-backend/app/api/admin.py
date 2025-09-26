from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
from beanie import PydanticObjectId
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User, UserRole, TokenUsageLog, UserSubscription, SubscriptionPlan
from ..models.template import Template
from ..models.component import Component
import logging
from app.database import get_database

# Temporary imports to avoid import errors - these need to be replaced with MongoDB aggregations
try:
    from sqlalchemy import select, func, and_, desc, or_
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    # Create dummy functions to avoid import errors
    def select(*args, **kwargs): pass
    def func(*args, **kwargs): 
        class DummyFunc:
            def sum(self, *args): return self
            def count(self, *args): return self
            def distinct(self, *args): return self
            def date(self, *args): return self
            def label(self, *args): return self
            def scalar(self): return 0
        return DummyFunc()
    def and_(*args, **kwargs): pass
    def desc(*args, **kwargs): pass
    def or_(*args, **kwargs): pass
    class AsyncSession: pass

# Temporary dummy service to avoid import errors
try:
    from ..services.stripe_service import StripeService
except ImportError:
    class StripeService:
        def __init__(self): pass
        async def get_revenue_stats(self, *args, **kwargs): return {"error": "Service not available"}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"], include_in_schema=True)

def require_admin(current_user: User = Depends(get_current_user_unified)):
    """Require admin role for access"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/users")
async def get_users(
    limit: int = Query(100, description="Maximum number of users to return"),
    skip: int = Query(0, description="Number of users to skip"),
    admin: User = Depends(require_admin)
):
    """Get all users with pagination"""
    try:
        # Get users with pagination
        users = await User.find().skip(skip).limit(limit).to_list()
        
        # Convert to dict format expected by frontend
        users_data = []
        for user in users:
            user_dict = {
                "id": str(user.id),
                "name": user.name or user.full_name or "Unknown",
                "email": user.email,
                "role": user.role,
                "status": "active" if user.is_active else "inactive",
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "subscription": user.subscription,
                "tokens_remaining": user.tokens_remaining,
                "wallet_balance": user.wallet_balance
            }
            users_data.append(user_dict)
        
        # Get total count
        total_count = await User.find().count()
        
        return {
            "users": users_data,
            "total": total_count,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@router.get("/content")
async def get_content(
    limit: int = Query(100, description="Maximum number of items to return"),
    skip: int = Query(0, description="Number of items to skip"),
    content_type: Optional[str] = Query(None, description="Filter by content type: template or component"),
    status: Optional[str] = Query(None, description="Filter by status"),
    admin: User = Depends(require_admin)
):
    """Get all content (templates and components) for admin review"""
    try:
        content_items = []
        
        # Get templates
        if not content_type or content_type == "template":
            # Build template query
            template_query = {}
            if status:
                template_query["approval_status"] = status
            
            templates = await Template.find(template_query).skip(skip if not content_type else 0).limit(limit if not content_type else limit//2).to_list()
            for template in templates:
                # Get developer info
                developer = await User.get(template.user_id)
                
                template_dict = {
                    "id": str(template.id),
                    "title": template.title,
                    "description": template.short_description,  
                    "category": template.category,
                    "status": template.approval_status,  # Use approval_status mapped to status
                    "price_inr": template.pricing_inr,  
                    "developer_name": developer.name if developer else "Unknown",
                    "developer_email": developer.email if developer else "Unknown",
                    "created_at": template.created_at.isoformat(),
                    "download_count": template.downloads,
                    "like_count": template.likes,
                    "average_rating": template.average_rating,
                    "content_type": "template"
                }
                content_items.append(template_dict)
        
        # Get components  
        if not content_type or content_type == "component":
            # Build component query
            component_query = {}
            if status:
                component_query["approval_status"] = status
                
            components = await Component.find(component_query).skip(skip if not content_type else 0).limit(limit if not content_type else limit//2).to_list()
            for component in components:
                # Get developer info
                developer = await User.get(component.user_id)
                
                component_dict = {
                    "id": str(component.id),
                    "title": component.title,
                    "description": component.short_description,  
                    "category": component.category,
                    "status": component.approval_status,  # Use approval_status mapped to status
                    "price_inr": component.pricing_inr,  
                    "developer_name": developer.name if developer else "Unknown",
                    "developer_email": developer.email if developer else "Unknown",
                    "created_at": component.created_at.isoformat(),
                    "download_count": component.downloads,
                    "like_count": component.likes,
                    "average_rating": component.average_rating,
                    "content_type": "component"
                }
                content_items.append(component_dict)
        
        # Don't filter by status here if we want all content - filtering is done in queries above
        # Sort by creation date (newest first)
        content_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply pagination manually if we fetched all content
        if not status:
            content_items = content_items[skip:skip + limit]
        
        return {
            "content": content_items,
            "total": len(content_items),
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")

@router.get("/analytics")
async def get_analytics(admin: User = Depends(require_admin)):
    """Get platform analytics for admin dashboard"""
    try:
        # Get user statistics
        total_users = await User.find().count()
        active_users = await User.find(User.is_active == True).count()
        admin_users = await User.find(User.role == UserRole.ADMIN).count()
        developer_users = await User.find(User.role == UserRole.DEVELOPER).count()
        regular_users = await User.find(User.role == UserRole.USER).count()
        
        # Get content statistics
        total_templates = await Template.find().count()
        total_components = await Component.find().count()
        total_content = total_templates + total_components
        
        # Get pending content count
        pending_templates = await Template.find(Template.approval_status == "pending_approval").count()
        pending_components = await Component.find(Component.approval_status == "pending_approval").count()
        pending_content = pending_templates + pending_components
        
        # Calculate platform revenue (mock data for now)
        platform_revenue_inr = 50000  # This should be calculated from actual transactions
        
        # Get recent activity (mock data for now)
        recent_activity = [
            {
                "description": "New user registered",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "description": "Template uploaded for review",
                "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
            },
            {
                "description": "Purchase completed",
                "timestamp": (datetime.now() - timedelta(hours=8)).isoformat()
            }
        ]
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_content": total_content,
            "platform_revenue_inr": platform_revenue_inr,
            "pending_content": pending_content,  # Use calculated pending content
            "user_reports": 0,     # This should be calculated from reports
            "user_growth": 15.2,   # Mock percentage growth
            "content_growth": 8.7, # Mock percentage growth  
            "revenue_growth": 23.1, # Mock percentage growth
            "recent_activity": recent_activity,
            "user_breakdown": {
                "admin": admin_users,
                "developer": developer_users,
                "user": regular_users
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: str,
    content_type: str = Query(..., description="Type of content: template or component"),
    approval_data: dict = None,
    admin: User = Depends(require_admin)
):
    """Approve a template or component"""
    try:
        if content_type == "template":
            template = await Template.get(PydanticObjectId(content_id))
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Update template approval_status (correct field name)
            if hasattr(template, 'approval_status'):
                template.approval_status = "approved"
                template.updated_at = datetime.now(timezone.utc)
                await template.save()
            
            return {"message": "Template approved successfully"}
            
        elif content_type == "component":
            component = await Component.get(PydanticObjectId(content_id))
            if not component:
                raise HTTPException(status_code=404, detail="Component not found")
            
            # Update component approval_status (correct field name)
            if hasattr(component, 'approval_status'):
                component.approval_status = "approved"
                component.updated_at = datetime.now(timezone.utc)
                await component.save()
            
            return {"message": "Component approved successfully"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
            
    except Exception as e:
        logger.error(f"Failed to approve content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to approve content: {str(e)}")

@router.post("/users/{user_id}/manage")
async def manage_user(
    user_id: str,
    action_data: dict,
    admin: User = Depends(require_admin)
):
    """Manage user (suspend, activate, etc.)"""
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        action = action_data.get("action")
        
        if action == "suspend":
            user.is_active = False
        elif action == "activate":
            user.is_active = True
        elif action == "delete":
            # Soft delete - just deactivate
            user.is_active = False
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        user.updated_at = datetime.now()
        await user.save()
        
        return {"message": f"User {action}d successfully"}
        
    except Exception as e:
        logger.error(f"Failed to manage user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to manage user: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: dict,
    admin: User = Depends(require_admin)
):
    """Update user details (name, email, role, status)"""
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        if "name" in update_data:
            user.name = update_data["name"]
        if "email" in update_data:
            user.email = update_data["email"]
        if "role" in update_data:
            user.role = update_data["role"]
        if "is_active" in update_data:
            user.is_active = update_data["is_active"]
        
        user.updated_at = datetime.now()
        await user.save()
        
        return {"message": "User updated successfully", "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }}
        
    except Exception as e:
        logger.error(f"Failed to update user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.get("/usage-stats")
async def usage_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: Optional[str] = Query("day", description="Group by: day, week, month, provider, model"),
    db: Any = Depends(get_database), 
    admin: User = Depends(require_admin)
):
    """
    Get detailed token usage statistics with flexible grouping and filtering options.
    
    Returns comprehensive analytics on token usage across the platform.
    """
    try:
        # TODO: Implement MongoDB aggregation queries to replace SQLAlchemy queries
        # This is a temporary fix to get the server running
        return {
            "message": "Token usage statistics temporarily unavailable - needs MongoDB aggregation implementation",
            "total_tokens": 0,
            "total_cost": 0,
            "unique_users": 0,
            "daily_breakdown": [],
            "provider_breakdown": [],
            "model_breakdown": []
        }
        
        # The following SQLAlchemy code needs to be converted to MongoDB aggregation:
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
    db: Any = Depends(get_database), 
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
    db: Any = Depends(get_database), 
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
async def system_stats(db: Any = Depends(get_database), admin: User = Depends(require_admin)):
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
