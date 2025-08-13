"""
Enhanced User Dashboard Endpoints with Purchase History and Recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.models.user import User
from app.models.item_purchase import ItemPurchase, PurchaseStatus
from app.models.template import Template
from app.models.component import Component
from app.services.access_control import ContentAccessService
from app.middleware.auth import require_auth


router = APIRouter()


@router.get("/user/dashboard")
async def get_user_dashboard(current_user: User = Depends(require_auth)):
    """Get comprehensive user dashboard with purchase history, recommendations, and analytics"""
    try:
        # Get purchase statistics
        purchase_stats = await get_purchase_statistics(current_user)
        
        # Get recent purchases
        recent_purchases = await ItemPurchase.find({
            "user_id": current_user.id,
            "status": PurchaseStatus.COMPLETED
        }).sort([("payment_completed_at", -1)]).limit(5).to_list()
        
        # Get owned content (user's own templates/components)
        owned_templates = await Template.find({"user_id": current_user.id}).limit(5).to_list()
        owned_components = await Component.find({"user_id": current_user.id}).limit(5).to_list()
        
        # Get recommendations
        recommendations = await get_user_recommendations(current_user)
        
        # Get usage analytics
        usage_analytics = await get_usage_analytics(current_user)
        
        return {
            "success": True,
            "dashboard": {
                "user_info": {
                    "id": str(current_user.id),
                    "username": current_user.username,
                    "email": current_user.email,
                    "role": current_user.role,
                    "wallet_balance": getattr(current_user, 'wallet_balance', 0),
                    "profile_image": getattr(current_user, 'profile_image', None)
                },
                "purchase_statistics": purchase_stats,
                "recent_purchases": [purchase.to_dict() for purchase in recent_purchases],
                "owned_content": {
                    "templates": [template.to_dict() for template in owned_templates],
                    "components": [component.to_dict() for component in owned_components]
                },
                "recommendations": recommendations,
                "usage_analytics": usage_analytics
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@router.get("/user/purchased-content")
async def get_purchased_content(
    item_type: Optional[str] = Query(None, description="Filter by 'template' or 'component'"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_auth)
):
    """Get user's purchased content with download links and access status"""
    try:
        # Build query
        query = {
            "user_id": current_user.id,
            "status": PurchaseStatus.COMPLETED,
            "access_granted": True
        }
        
        if item_type:
            query["item_type"] = item_type
        
        # Get total count
        total_count = await ItemPurchase.count(query)
        
        # Get purchases with pagination
        skip = (page - 1) * page_size
        purchases = await ItemPurchase.find(query)\
            .sort([("payment_completed_at", -1)])\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        # Enrich with current item details
        enriched_purchases = []
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            
            # Get current item details
            if purchase.item_type == "template":
                current_item = await Template.get(purchase.item_id)
            else:
                current_item = await Component.get(purchase.item_id)
            
            if current_item:
                purchase_data["current_item"] = {
                    "title": current_item.title,
                    "category": current_item.category,
                    "type": current_item.type,
                    "live_demo_url": getattr(current_item, 'live_demo_url', None),
                    "git_repo_url": getattr(current_item, 'git_repo_url', None),
                    "is_active": current_item.is_active,
                    "code_available": bool(getattr(current_item, 'code', None)),
                    "readme_available": bool(getattr(current_item, 'readme_content', None))
                }
            else:
                purchase_data["current_item"] = None
                purchase_data["item_status"] = "Item no longer available"
            
            enriched_purchases.append(purchase_data)
        
        return {
            "success": True,
            "purchased_content": enriched_purchases,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "filters": {
                "item_type": item_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get purchased content: {str(e)}")


@router.get("/user/recommendations")
async def get_user_recommendations_endpoint(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    current_user: User = Depends(require_auth)
):
    """Get personalized content recommendations for user"""
    try:
        recommendations = await get_user_recommendations(current_user, limit)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "recommendation_count": len(recommendations["templates"]) + len(recommendations["components"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


async def get_purchase_statistics(user: User) -> Dict[str, Any]:
    """Get comprehensive purchase statistics for user"""
    try:
        # Total purchases and spending
        total_purchases = await ItemPurchase.count({
            "user_id": user.id,
            "status": PurchaseStatus.COMPLETED
        })
        
        # Spending breakdown
        spending_stats = await ItemPurchase.aggregate([
            {"$match": {"user_id": user.id, "status": PurchaseStatus.COMPLETED}},
            {"$group": {
                "_id": None,
                "total_spent": {"$sum": "$paid_amount_inr"},
                "template_spent": {
                    "$sum": {"$cond": [{"$eq": ["$item_type", "template"]}, "$paid_amount_inr", 0]}
                },
                "component_spent": {
                    "$sum": {"$cond": [{"$eq": ["$item_type", "component"]}, "$paid_amount_inr", 0]}
                }
            }}
        ]).to_list()
        
        spending_data = spending_stats[0] if spending_stats else {
            "total_spent": 0, "template_spent": 0, "component_spent": 0
        }
        
        # Monthly spending (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        monthly_spending = await ItemPurchase.aggregate([
            {
                "$match": {
                    "user_id": user.id,
                    "status": PurchaseStatus.COMPLETED,
                    "payment_completed_at": {"$gte": twelve_months_ago}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$payment_completed_at"},
                        "month": {"$month": "$payment_completed_at"}
                    },
                    "amount": {"$sum": "$paid_amount_inr"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]).to_list()
        
        return {
            "total_purchases": total_purchases,
            "total_spent_inr": spending_data["total_spent"],
            "template_spent_inr": spending_data["template_spent"],
            "component_spent_inr": spending_data["component_spent"],
            "average_purchase_amount": spending_data["total_spent"] // max(1, total_purchases),
            "monthly_spending": monthly_spending
        }
        
    except Exception as e:
        print(f"Error getting purchase statistics: {e}")
        return {
            "total_purchases": 0,
            "total_spent_inr": 0,
            "template_spent_inr": 0,
            "component_spent_inr": 0,
            "average_purchase_amount": 0,
            "monthly_spending": []
        }


async def get_user_recommendations(user: User, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """Get personalized recommendations based on user's purchase history and preferences"""
    try:
        # Get user's purchase history to understand preferences
        user_purchases = await ItemPurchase.find({
            "user_id": user.id,
            "status": PurchaseStatus.COMPLETED
        }).to_list()
        
        # Extract categories and types from purchases
        purchased_categories = set()
        purchased_types = set()
        purchased_item_ids = set()
        
        for purchase in user_purchases:
            # Get item details
            if purchase.item_type == "template":
                item = await Template.get(purchase.item_id)
            else:
                item = await Component.get(purchase.item_id)
            
            if item:
                purchased_categories.add(item.category)
                purchased_types.add(item.type)
                purchased_item_ids.add(str(purchase.item_id))
        
        # If no purchase history, recommend popular/featured items
        if not purchased_categories:
            recommended_templates = await Template.find({
                "is_active": True,
                "approval_status": "approved",
                "$or": [{"featured": True}, {"popular": True}]
            }).limit(limit // 2).to_list()
            
            recommended_components = await Component.find({
                "is_active": True,
                "approval_status": "approved",
                "$or": [{"featured": True}, {"popular": True}]
            }).limit(limit // 2).to_list()
        else:
            # Recommend based on purchased categories and types
            template_query = {
                "is_active": True,
                "approval_status": "approved",
                "id": {"$nin": [purchase.item_id for purchase in user_purchases if purchase.item_type == "template"]},
                "$or": [
                    {"category": {"$in": list(purchased_categories)}},
                    {"type": {"$in": list(purchased_types)}},
                    {"featured": True}
                ]
            }
            
            component_query = {
                "is_active": True,
                "approval_status": "approved",
                "id": {"$nin": [purchase.item_id for purchase in user_purchases if purchase.item_type == "component"]},
                "$or": [
                    {"category": {"$in": list(purchased_categories)}},
                    {"type": {"$in": list(purchased_types)}},
                    {"featured": True}
                ]
            }
            
            recommended_templates = await Template.find(template_query)\
                .sort([("rating", -1), ("downloads", -1)])\
                .limit(limit // 2).to_list()
                
            recommended_components = await Component.find(component_query)\
                .sort([("rating", -1), ("downloads", -1)])\
                .limit(limit // 2).to_list()
        
        # Apply access control and get preview data
        template_recommendations = []
        for template in recommended_templates:
            access_level, access_info = await ContentAccessService.get_content_access_level(user, template)
            preview_data = ContentAccessService.get_content_preview_data(template.to_dict(), access_level)
            preview_data["recommendation_reason"] = get_recommendation_reason(template, purchased_categories, purchased_types)
            template_recommendations.append(preview_data)
        
        component_recommendations = []
        for component in recommended_components:
            access_level, access_info = await ContentAccessService.get_content_access_level(user, component)
            preview_data = ContentAccessService.get_content_preview_data(component.to_dict(), access_level)
            preview_data["recommendation_reason"] = get_recommendation_reason(component, purchased_categories, purchased_types)
            component_recommendations.append(preview_data)
        
        return {
            "templates": template_recommendations,
            "components": component_recommendations
        }
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return {"templates": [], "components": []}


async def get_usage_analytics(user: User) -> Dict[str, Any]:
    """Get user's usage analytics"""
    try:
        # Download counts from purchases
        download_stats = await ItemPurchase.aggregate([
            {"$match": {"user_id": user.id, "status": PurchaseStatus.COMPLETED}},
            {"$group": {
                "_id": None,
                "total_downloads": {"$sum": "$download_count"},
                "items_with_downloads": {"$sum": {"$cond": [{"$gt": ["$download_count", 0]}, 1, 0]}},
                "avg_downloads_per_item": {"$avg": "$download_count"}
            }}
        ]).to_list()
        
        download_data = download_stats[0] if download_stats else {
            "total_downloads": 0,
            "items_with_downloads": 0,
            "avg_downloads_per_item": 0
        }
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activity = await ItemPurchase.count({
            "user_id": user.id,
            "last_accessed_at": {"$gte": thirty_days_ago}
        })
        
        return {
            "total_downloads": download_data["total_downloads"],
            "items_with_downloads": download_data["items_with_downloads"],
            "average_downloads_per_item": round(download_data["avg_downloads_per_item"], 1),
            "recent_activity_count": recent_activity,
            "engagement_score": calculate_engagement_score(download_data, recent_activity)
        }
        
    except Exception as e:
        print(f"Error getting usage analytics: {e}")
        return {
            "total_downloads": 0,
            "items_with_downloads": 0,
            "average_downloads_per_item": 0,
            "recent_activity_count": 0,
            "engagement_score": 0
        }


def get_recommendation_reason(item, purchased_categories: set, purchased_types: set) -> str:
    """Generate recommendation reason"""
    if item.featured:
        return "Featured content"
    elif item.popular:
        return "Popular content"
    elif item.category in purchased_categories:
        return f"Similar to your {item.category} purchases"
    elif item.type in purchased_types:
        return f"Matches your {item.type} preferences"
    else:
        return "Recommended for you"


def calculate_engagement_score(download_data: Dict, recent_activity: int) -> int:
    """Calculate user engagement score (0-100)"""
    try:
        # Base score from downloads
        download_score = min(download_data["total_downloads"] * 2, 50)
        
        # Activity score from recent usage
        activity_score = min(recent_activity * 10, 30)
        
        # Consistency score from using downloaded items
        if download_data["total_downloads"] > 0:
            consistency_score = (download_data["items_with_downloads"] / max(1, download_data["total_downloads"])) * 20
        else:
            consistency_score = 0
        
        return min(int(download_score + activity_score + consistency_score), 100)
        
    except Exception:
        return 0
