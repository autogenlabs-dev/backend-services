from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from enum import Enum

class ItemType(str, Enum):
    """Item type enumeration"""
    TEMPLATE = "template"
    COMPONENT = "component"

class AccessLevel(str, Enum):
    """Access level enumeration"""
    FULL = "full_access"
    LIMITED = "limited_access"
    PREVIEW = "preview_only"

class PurchasedItem(Document):
    """Purchased item model for tracking user purchases"""
    user_id: PydanticObjectId = Field(index=True)
    item_id: PydanticObjectId = Field(index=True)
    item_type: ItemType
    
    # Purchase Details
    price_paid: float
    currency: str = "INR"
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    transaction_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    
    # Access Control
    access_level: AccessLevel = AccessLevel.FULL
    access_granted_at: datetime = Field(default_factory=datetime.utcnow)
    access_expires_at: Optional[datetime] = None
    
    # Usage Tracking
    download_count: int = 0
    first_download_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "purchased_items"
        indexes = [
            "user_id",
            "item_id",
            "item_type",
            "purchase_date",
            "transaction_id",
            [("user_id", 1), ("item_id", 1)],  # Compound index
            "created_at"
        ]

    def __repr__(self):
        return f"<PurchasedItem(user_id='{self.user_id}', item_id='{self.item_id}')>"

    def __str__(self):
        return f"Purchase: {self.item_type} {self.item_id} by {self.user_id}"
