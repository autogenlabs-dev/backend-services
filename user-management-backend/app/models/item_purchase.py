"""
Enhanced Item Purchase Model for Individual Marketplace Purchases
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field
from bson import ObjectId

# Use PydanticObjectId for consistency
try:
    from beanie import PydanticObjectId
except ImportError:
    from bson import ObjectId as PydanticObjectId


class PurchaseStatus(str, Enum):
    """Purchase status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class ItemType(str, Enum):
    """Item type enumeration"""
    TEMPLATE = "template"
    COMPONENT = "component"


class ItemPurchase(Document):
    """Individual item purchase model with Razorpay integration"""
    
    # Purchase Identification
    purchase_id: str = Field(..., description="Unique purchase ID")
    user_id: PydanticObjectId = Field(..., description="Buyer user ID")
    
    # Item Information
    item_id: PydanticObjectId = Field(..., description="Template/Component ID")
    item_type: ItemType = Field(..., description="Type of item purchased")
    item_title: str = Field(..., description="Item title at time of purchase")
    
    # Developer Information
    developer_id: PydanticObjectId = Field(..., description="Developer/Creator user ID")
    developer_username: str = Field(..., description="Developer username")
    
    # Pricing Information
    original_price_inr: int = Field(..., description="Original price in INR")
    original_price_usd: int = Field(..., description="Original price in USD")
    paid_amount_inr: int = Field(..., description="Amount paid in INR")
    paid_currency: str = Field(default="INR", description="Payment currency")
    
    # Revenue Split (70/30)
    developer_earnings_inr: int = Field(..., description="Developer's 70% share")
    platform_fee_inr: int = Field(..., description="Platform's 30% share")
    
    # Payment Gateway Integration
    razorpay_order_id: Optional[str] = Field(None, description="Razorpay order ID")
    razorpay_payment_id: Optional[str] = Field(None, description="Razorpay payment ID")
    razorpay_signature: Optional[str] = Field(None, description="Razorpay signature")
    
    # Purchase Status and Timestamps
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING)
    payment_method: Optional[str] = Field(None, description="Payment method used")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_completed_at: Optional[datetime] = Field(None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Access Information
    download_count: int = Field(default=0, description="Number of times downloaded")
    last_accessed_at: Optional[datetime] = Field(None)
    access_granted: bool = Field(default=False, description="Whether access is granted")
    
    # Transaction Metadata
    payment_gateway_response: Optional[Dict[str, Any]] = Field(None, description="Full gateway response")
    refund_info: Optional[Dict[str, Any]] = Field(None, description="Refund details if applicable")
    
    # Admin and Audit
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    is_verified: bool = Field(default=False, description="Manual verification status")
    
    class Settings:
        name = "item_purchases"
        indexes = [
            [("user_id", 1)],
            [("developer_id", 1)],
            [("item_id", 1), ("item_type", 1)],
            [("status", 1)],
            [("razorpay_order_id", 1)],
            [("razorpay_payment_id", 1)],
            [("created_at", -1)],
            [("user_id", 1), ("item_id", 1), ("item_type", 1)],  # Prevent duplicate purchases
            [("developer_id", 1), ("status", 1)],  # For earnings calculation
            [("payment_completed_at", -1)],
        ]
        use_state_management = True

    def calculate_revenue_split(self):
        """Calculate 70/30 revenue split"""
        self.developer_earnings_inr = int(self.paid_amount_inr * 0.70)
        self.platform_fee_inr = self.paid_amount_inr - self.developer_earnings_inr

    def mark_completed(self, razorpay_payment_id: str, razorpay_signature: str):
        """Mark purchase as completed"""
        self.status = PurchaseStatus.COMPLETED
        self.razorpay_payment_id = razorpay_payment_id
        self.razorpay_signature = razorpay_signature
        self.payment_completed_at = datetime.now(timezone.utc)
        self.access_granted = True
        self.updated_at = datetime.now(timezone.utc)
        self.calculate_revenue_split()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "purchase_id": self.purchase_id,
            "user_id": str(self.user_id),
            "item_id": str(self.item_id),
            "item_type": self.item_type,
            "item_title": self.item_title,
            "developer_id": str(self.developer_id),
            "developer_username": self.developer_username,
            "original_price_inr": self.original_price_inr,
            "original_price_usd": self.original_price_usd,
            "paid_amount_inr": self.paid_amount_inr,
            "paid_currency": self.paid_currency,
            "developer_earnings_inr": self.developer_earnings_inr,
            "platform_fee_inr": self.platform_fee_inr,
            "status": self.status,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat(),
            "payment_completed_at": self.payment_completed_at.isoformat() if self.payment_completed_at else None,
            "download_count": self.download_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "access_granted": self.access_granted,
            "is_verified": self.is_verified
        }

    def __repr__(self):
        return f"<ItemPurchase(purchase_id='{self.purchase_id}', item_type='{self.item_type}', status='{self.status}')>"
