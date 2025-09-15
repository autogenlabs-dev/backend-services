"""
Shopping Cart Model for Marketplace
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field, BaseModel
from bson import ObjectId

# Use PydanticObjectId for consistency
try:
    from beanie import PydanticObjectId
except ImportError:
    from bson import ObjectId as PydanticObjectId


class CartItemType(str, Enum):
    """Type of item in cart"""
    TEMPLATE = "template"
    COMPONENT = "component"


class CartItem(BaseModel):
    """Individual cart item"""
    item_id: PydanticObjectId = Field(..., description="Template/Component ID")
    item_type: CartItemType = Field(..., description="Type of item")
    item_title: str = Field(..., description="Item title")
    developer_username: str = Field(..., description="Developer username")
    price_inr: int = Field(..., description="Price in INR")
    price_usd: int = Field(..., description="Price in USD")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "item_id": str(self.item_id),
            "item_type": self.item_type,
            "item_title": self.item_title,
            "developer_username": self.developer_username,
            "price_inr": self.price_inr,
            "price_usd": self.price_usd,
            "added_at": self.added_at.isoformat()
        }


class ShoppingCart(Document):
    """Shopping cart model for users"""
    
    # User Information
    user_id: PydanticObjectId = Field(..., description="User ID")
    
    # Cart Items
    items: List[CartItem] = Field(default_factory=list, description="Items in cart")
    
    # Cart Statistics
    total_items: int = Field(default=0, description="Number of items in cart")
    total_amount_inr: int = Field(default=0, description="Total amount in INR")
    total_amount_usd: int = Field(default=0, description="Total amount in USD")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Cart Settings
    currency_preference: str = Field(default="INR", description="User's preferred currency")
    save_for_later: List[CartItem] = Field(default_factory=list, description="Saved items")
    
    class Settings:
        name = "shopping_carts"
        indexes = [
            [("user_id", 1)],  # Each user has one cart
            [("updated_at", -1)],
            [("last_accessed_at", -1)]
        ]
        use_state_management = True

    def add_item(self, item: CartItem) -> bool:
        """Add item to cart, return True if added, False if already exists"""
        # Check if item already exists
        for existing_item in self.items:
            if (existing_item.item_id == item.item_id and 
                existing_item.item_type == item.item_type):
                return False  # Item already in cart
        
        # Add item
        self.items.append(item)
        self.update_totals()
        self.updated_at = datetime.now(timezone.utc)
        return True

    def remove_item(self, item_id: str, item_type: CartItemType) -> bool:
        """Remove item from cart"""
        original_length = len(self.items)
        self.items = [
            item for item in self.items 
            if not (str(item.item_id) == item_id and item.item_type == item_type)
        ]
        
        if len(self.items) < original_length:
            self.update_totals()
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def clear_cart(self):
        """Clear all items from cart"""
        self.items = []
        self.update_totals()
        self.updated_at = datetime.now(timezone.utc)

    def update_totals(self):
        """Update cart totals"""
        self.total_items = len(self.items)
        self.total_amount_inr = sum(item.price_inr for item in self.items)
        self.total_amount_usd = sum(item.price_usd for item in self.items)

    def move_to_saved(self, item_id: str, item_type: CartItemType) -> bool:
        """Move item from cart to saved for later"""
        for i, item in enumerate(self.items):
            if str(item.item_id) == item_id and item.item_type == item_type:
                saved_item = self.items.pop(i)
                self.save_for_later.append(saved_item)
                self.update_totals()
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def move_to_cart(self, item_id: str, item_type: CartItemType) -> bool:
        """Move item from saved to cart"""
        for i, item in enumerate(self.save_for_later):
            if str(item.item_id) == item_id and item.item_type == item_type:
                cart_item = self.save_for_later.pop(i)
                return self.add_item(cart_item)
        return False

    def get_checkout_summary(self) -> Dict[str, Any]:
        """Get checkout summary"""
        return {
            "total_items": self.total_items,
            "total_amount_inr": self.total_amount_inr,
            "total_amount_usd": self.total_amount_usd,
            "currency_preference": self.currency_preference,
            "items": [item.to_dict() for item in self.items],
            "estimated_platform_fee_inr": int(self.total_amount_inr * 0.30),
            "estimated_developer_earnings_inr": int(self.total_amount_inr * 0.70)
        }

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "items": [item.to_dict() for item in self.items],
            "save_for_later": [item.to_dict() for item in self.save_for_later],
            "total_items": self.total_items,
            "total_amount_inr": self.total_amount_inr,
            "total_amount_usd": self.total_amount_usd,
            "currency_preference": self.currency_preference,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat()
        }

    def __repr__(self):
        return f"<ShoppingCart(user_id='{self.user_id}', items={self.total_items}, total_inr={self.total_amount_inr})>"
