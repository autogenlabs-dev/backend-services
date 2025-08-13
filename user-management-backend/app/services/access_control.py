"""
Content Access Control Service for Marketplace
"""

from typing import Optional, Dict, Any, Tuple
from enum import Enum
from app.models.user import User
from app.models.template import Template
from app.models.component import Component
from app.models.item_purchase import ItemPurchase, PurchaseStatus
from bson import ObjectId


class AccessLevel(str, Enum):
    """Content access levels"""
    NO_ACCESS = "no_access"
    LIMITED_ACCESS = "limited_access"  # Preview only
    FULL_ACCESS = "full_access"       # Complete access including code
    OWNER_ACCESS = "owner_access"     # Owner with edit permissions


class ContentAccessService:
    """Service for determining user access levels to content"""
    
    @staticmethod
    async def get_content_access_level(user: Optional[User], item: Any) -> Tuple[AccessLevel, Dict[str, Any]]:
        """
        Determine user's access level to a content item (template or component).
        
        Returns:
            Tuple of (AccessLevel, access_info_dict)
        """
        access_info = {
            "can_view_code": False,
            "can_download": False,
            "can_edit": False,
            "can_delete": False,
            "purchase_required": False,
            "is_owner": False,
            "has_purchased": False,
            "price_inr": getattr(item, 'pricing_inr', 0),
            "price_usd": getattr(item, 'pricing_usd', 0),
            "plan_type": getattr(item, 'plan_type', 'Free'),
            "access_reason": ""
        }
        
        # If user is not authenticated
        if not user:
            if item.plan_type.lower() == "free":
                access_info.update({
                    "can_view_code": True,
                    "can_download": True,
                    "access_reason": "Free content - public access"
                })
                return AccessLevel.FULL_ACCESS, access_info
            else:
                access_info.update({
                    "purchase_required": True,
                    "access_reason": "Authentication required for paid content"
                })
                return AccessLevel.LIMITED_ACCESS, access_info
        
        # Check if user is the owner
        if hasattr(item, 'user_id') and str(item.user_id) == str(user.id):
            access_info.update({
                "can_view_code": True,
                "can_download": True,
                "can_edit": True,
                "can_delete": True,
                "is_owner": True,
                "access_reason": "Content owner - full access"
            })
            return AccessLevel.OWNER_ACCESS, access_info
        
        # Check if user is admin/superadmin (full access to everything)
        if user.role in ["admin", "superadmin"]:
            access_info.update({
                "can_view_code": True,
                "can_download": True,
                "can_edit": True,
                "can_delete": True,
                "access_reason": "Admin access - full permissions"
            })
            return AccessLevel.FULL_ACCESS, access_info
        
        # For free content, everyone gets full access
        if item.plan_type.lower() == "free":
            access_info.update({
                "can_view_code": True,
                "can_download": True,
                "access_reason": "Free content - public access"
            })
            return AccessLevel.FULL_ACCESS, access_info
        
        # For paid content, check if user has purchased
        item_type = "template" if isinstance(item, Template) else "component"
        purchase = await ItemPurchase.find_one({
            "user_id": user.id,
            "item_id": item.id,
            "item_type": item_type,
            "status": PurchaseStatus.COMPLETED,
            "access_granted": True
        })
        
        if purchase:
            access_info.update({
                "can_view_code": True,
                "can_download": True,
                "has_purchased": True,
                "access_reason": "Purchased content - full access",
                "purchase_date": purchase.payment_completed_at.isoformat() if purchase.payment_completed_at else None,
                "purchase_id": purchase.purchase_id
            })
            return AccessLevel.FULL_ACCESS, access_info
        
        # Paid content without purchase - limited access
        access_info.update({
            "purchase_required": True,
            "access_reason": "Paid content - purchase required for full access"
        })
        return AccessLevel.LIMITED_ACCESS, access_info
    
    @staticmethod
    def filter_content_by_access_level(content_data: Dict[str, Any], access_level: AccessLevel) -> Dict[str, Any]:
        """
        Filter content data based on access level.
        Removes sensitive information for users without appropriate access.
        """
        filtered_data = content_data.copy()
        
        if access_level in [AccessLevel.NO_ACCESS]:
            # Remove almost everything except basic info
            allowed_fields = [
                "id", "title", "category", "type", "language", "difficulty_level",
                "plan_type", "pricing_inr", "pricing_usd", "short_description",
                "developer_name", "developer_experience", "featured", "popular",
                "rating", "downloads", "views", "likes", "tags", "created_at"
            ]
            filtered_data = {k: v for k, v in filtered_data.items() if k in allowed_fields}
        
        elif access_level == AccessLevel.LIMITED_ACCESS:
            # Remove code, readme, and other premium content
            restricted_fields = [
                "code", "readme_content", "git_repo_url", "dependencies"
            ]
            for field in restricted_fields:
                if field in filtered_data:
                    if field == "code":
                        # Provide a teaser/preview
                        filtered_data[field] = "// Code preview available after purchase\n// This template contains premium code content"
                    elif field == "readme_content":
                        filtered_data[field] = "Full documentation available after purchase"
                    elif field == "git_repo_url":
                        filtered_data[field] = None
                    elif field == "dependencies":
                        # Show only first 3 dependencies
                        if isinstance(filtered_data[field], list) and len(filtered_data[field]) > 3:
                            filtered_data[field] = filtered_data[field][:3] + ["... (more available after purchase)"]
        
        elif access_level in [AccessLevel.FULL_ACCESS, AccessLevel.OWNER_ACCESS]:
            # No filtering - full access
            pass
        
        return filtered_data
    
    @staticmethod
    async def check_bulk_purchase_access(user: User, item_ids: list, item_type: str) -> Dict[str, bool]:
        """
        Check purchase access for multiple items at once.
        Returns dict mapping item_id to purchase status.
        """
        if not user:
            return {str(item_id): False for item_id in item_ids}
        
        # Admin gets access to everything
        if user.role in ["admin", "superadmin"]:
            return {str(item_id): True for item_id in item_ids}
        
        # Convert to ObjectId for query
        object_ids = []
        for item_id in item_ids:
            try:
                if isinstance(item_id, str):
                    object_ids.append(ObjectId(item_id))
                else:
                    object_ids.append(item_id)
            except:
                continue
        
        # Query purchases
        purchases = await ItemPurchase.find({
            "user_id": user.id,
            "item_id": {"$in": object_ids},
            "item_type": item_type,
            "status": PurchaseStatus.COMPLETED,
            "access_granted": True
        }).to_list()
        
        # Build result dict
        purchased_items = {str(purchase.item_id) for purchase in purchases}
        return {str(item_id): str(item_id) in purchased_items for item_id in item_ids}
    
    @staticmethod
    async def get_user_purchased_items(user: User, item_type: Optional[str] = None) -> list:
        """
        Get all items purchased by a user.
        """
        query = {
            "user_id": user.id,
            "status": PurchaseStatus.COMPLETED,
            "access_granted": True
        }
        
        if item_type:
            query["item_type"] = item_type
        
        purchases = await ItemPurchase.find(query).sort([("payment_completed_at", -1)]).to_list()
        return [purchase.to_dict() for purchase in purchases]
    
    @staticmethod
    async def increment_download_count(user: User, item_id: str, item_type: str):
        """
        Increment download count for purchased item.
        """
        purchase = await ItemPurchase.find_one({
            "user_id": user.id,
            "item_id": ObjectId(item_id),
            "item_type": item_type,
            "status": PurchaseStatus.COMPLETED,
            "access_granted": True
        })
        
        if purchase:
            from datetime import datetime
            await purchase.update({
                "$inc": {"download_count": 1},
                "$set": {"last_accessed_at": datetime.utcnow()}
            })
            return True
        return False
    
    @staticmethod
    def get_content_preview_data(content_data: Dict[str, Any], access_level: AccessLevel) -> Dict[str, Any]:
        """
        Get preview data for content listing pages.
        Optimized for performance with minimal data.
        """
        preview_fields = [
            "id", "title", "category", "type", "language", "difficulty_level",
            "plan_type", "pricing_inr", "pricing_usd", "short_description",
            "developer_name", "rating", "downloads", "views", "likes",
            "featured", "popular", "created_at", "preview_images", "tags"
        ]
        
        preview_data = {k: v for k, v in content_data.items() if k in preview_fields}
        
        # Add access indicators
        preview_data["access_level"] = access_level
        preview_data["requires_purchase"] = access_level == AccessLevel.LIMITED_ACCESS
        preview_data["is_free"] = content_data.get("plan_type", "").lower() == "free"
        
        # Limit preview images for limited access
        if access_level == AccessLevel.LIMITED_ACCESS and "preview_images" in preview_data:
            if isinstance(preview_data["preview_images"], list) and len(preview_data["preview_images"]) > 2:
                preview_data["preview_images"] = preview_data["preview_images"][:2]
        
        return preview_data
