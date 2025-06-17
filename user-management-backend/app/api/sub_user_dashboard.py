from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..auth.jwt_auth import get_current_user
from ..services.sub_user_service import SubUserService
from ..services.token_service import TokenService
from ..models.user import User, TokenUsageLog, ApiKey
from ..schemas.sub_user import SubUserUsageStats
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/dashboard/sub-users", tags=["sub-user-dashboard"])

class DashboardStats(BaseModel):
    total_sub_users: int
    active_sub_users: int
    total_tokens_used: int
    total_api_keys: int
    monthly_usage_percentage: float
    top_consumers: List[Dict[str, Any]]

class SubUserActivity(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    tokens_used_today: int
    requests_today: int
    last_active: Optional[datetime]
    status: str

@router.get("/overview", response_model=DashboardStats)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics for all sub-users"""
    
    service = SubUserService(db)
    token_service = TokenService(db)
    
    # Get all sub-users
    sub_users = service.get_sub_users(current_user.id)
    
    # Calculate stats
    total_sub_users = len(sub_users)
    active_sub_users = len([u for u in sub_users if u.is_active])
    total_tokens_used = sum(u.tokens_used for u in sub_users)
    
    # Get API keys count
    total_api_keys = 0
    for sub_user in sub_users:
        keys_count = db.query(ApiKey).filter(
            ApiKey.user_id == sub_user.id,
            ApiKey.is_active == True
        ).count()
        total_api_keys += keys_count
    
    # Calculate usage percentage
    total_monthly_limit = sum(u.monthly_limit for u in sub_users)
    monthly_usage_percentage = (total_tokens_used / total_monthly_limit * 100) if total_monthly_limit > 0 else 0
    
    # Get top consumers (top 5)
    top_consumers = []
    sorted_users = sorted(sub_users, key=lambda u: u.tokens_used, reverse=True)[:5]
    
    for user in sorted_users:
        usage_percentage = (user.tokens_used / user.monthly_limit * 100) if user.monthly_limit > 0 else 0
        top_consumers.append({
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "tokens_used": user.tokens_used,
            "monthly_limit": user.monthly_limit,
            "usage_percentage": round(usage_percentage, 2)
        })
    
    return DashboardStats(
        total_sub_users=total_sub_users,
        active_sub_users=active_sub_users,
        total_tokens_used=total_tokens_used,
        total_api_keys=total_api_keys,
        monthly_usage_percentage=round(monthly_usage_percentage, 2),
        top_consumers=top_consumers
    )

@router.get("/activity", response_model=List[SubUserActivity])
async def get_sub_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get recent activity for all sub-users"""
    
    service = SubUserService(db)
    sub_users = service.get_sub_users(current_user.id)
    
    from_date = datetime.utcnow() - timedelta(days=days)
    today = datetime.utcnow().date()
    
    activities = []
    
    for sub_user in sub_users:
        # Get today's usage
        today_logs = db.query(TokenUsageLog).filter(
            TokenUsageLog.user_id == sub_user.id,
            TokenUsageLog.timestamp >= datetime.combine(today, datetime.min.time())
        ).all()
        
        tokens_used_today = sum(log.tokens_used for log in today_logs)
        requests_today = len(today_logs)
        
        # Get last activity
        last_log = db.query(TokenUsageLog).filter(
            TokenUsageLog.user_id == sub_user.id
        ).order_by(TokenUsageLog.timestamp.desc()).first()
        
        last_active = last_log.timestamp if last_log else sub_user.last_login_at
        
        # Determine status
        status = "active" if sub_user.is_active else "inactive"
        if sub_user.is_active and last_active:
            hours_since_active = (datetime.utcnow() - last_active).total_seconds() / 3600
            if hours_since_active > 24:
                status = "idle"
        
        activities.append(SubUserActivity(
            user_id=str(sub_user.id),
            user_name=sub_user.name,
            user_email=sub_user.email,
            tokens_used_today=tokens_used_today,
            requests_today=requests_today,
            last_active=last_active,
            status=status
        ))
    
    # Sort by last active (most recent first)
    activities.sort(key=lambda x: x.last_active or datetime.min, reverse=True)
    
    return activities

@router.get("/usage-trends")
async def get_usage_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=90)
):
    """Get usage trends for sub-users over time"""
    
    service = SubUserService(db)
    sub_users = service.get_sub_users(current_user.id)
    sub_user_ids = [str(u.id) for u in sub_users]
    
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get usage logs for all sub-users
    usage_logs = db.query(TokenUsageLog).filter(
        TokenUsageLog.user_id.in_(sub_user_ids),
        TokenUsageLog.timestamp >= from_date
    ).all()
    
    # Group by date
    daily_usage = {}
    for log in usage_logs:
        date_str = log.timestamp.date().isoformat()
        if date_str not in daily_usage:
            daily_usage[date_str] = {
                "date": date_str,
                "total_tokens": 0,
                "total_requests": 0,
                "unique_users": set()
            }
        daily_usage[date_str]["total_tokens"] += log.tokens_used
        daily_usage[date_str]["total_requests"] += 1
        daily_usage[date_str]["unique_users"].add(str(log.user_id))
    
    # Convert to list and add unique user counts
    trends = []
    for date_str in sorted(daily_usage.keys()):
        data = daily_usage[date_str]
        trends.append({
            "date": data["date"],
            "total_tokens": data["total_tokens"],
            "total_requests": data["total_requests"],
            "unique_users": len(data["unique_users"]),
            "avg_tokens_per_request": data["total_tokens"] / data["total_requests"] if data["total_requests"] > 0 else 0
        })
    
    return {
        "period_days": days,
        "trends": trends,
        "summary": {
            "total_tokens": sum(t["total_tokens"] for t in trends),
            "total_requests": sum(t["total_requests"] for t in trends),
            "peak_day": max(trends, key=lambda x: x["total_tokens"])["date"] if trends else None,
            "average_daily_tokens": sum(t["total_tokens"] for t in trends) / len(trends) if trends else 0
        }
    }

@router.get("/limits-analysis")
async def get_limits_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze sub-user limits and suggest optimizations"""
    
    service = SubUserService(db)
    sub_users = service.get_sub_users(current_user.id)
    
    analysis = {
        "over_utilized": [],  # Users using >90% of limits
        "under_utilized": [],  # Users using <10% of limits
        "optimal": [],  # Users using 10-90% of limits
        "recommendations": []
    }
    
    for sub_user in sub_users:
        usage_percentage = (sub_user.tokens_used / sub_user.monthly_limit * 100) if sub_user.monthly_limit > 0 else 0
        
        user_data = {
            "user_id": str(sub_user.id),
            "name": sub_user.name,
            "email": sub_user.email,
            "usage_percentage": round(usage_percentage, 2),
            "tokens_used": sub_user.tokens_used,
            "monthly_limit": sub_user.monthly_limit
        }
        
        if usage_percentage > 90:
            analysis["over_utilized"].append(user_data)
            analysis["recommendations"].append({
                "user_id": str(sub_user.id),
                "type": "increase_limit",
                "message": f"Consider increasing limit for {sub_user.name} (currently at {usage_percentage:.1f}%)"
            })
        elif usage_percentage < 10:
            analysis["under_utilized"].append(user_data)
            analysis["recommendations"].append({
                "user_id": str(sub_user.id),
                "type": "decrease_limit",
                "message": f"Consider decreasing limit for {sub_user.name} (only using {usage_percentage:.1f}%)"
            })
        else:
            analysis["optimal"].append(user_data)
    
    # Add general recommendations
    total_allocated = sum(u.monthly_limit for u in sub_users)
    total_used = sum(u.tokens_used for u in sub_users)
    overall_efficiency = (total_used / total_allocated * 100) if total_allocated > 0 else 0
    
    if overall_efficiency < 50:
        analysis["recommendations"].append({
            "type": "general",
            "message": f"Overall token efficiency is {overall_efficiency:.1f}%. Consider reallocating limits."
        })
    
    analysis["summary"] = {
        "total_sub_users": len(sub_users),
        "over_utilized_count": len(analysis["over_utilized"]),
        "under_utilized_count": len(analysis["under_utilized"]),
        "optimal_count": len(analysis["optimal"]),
        "overall_efficiency": round(overall_efficiency, 2)
    }
    
    return analysis
