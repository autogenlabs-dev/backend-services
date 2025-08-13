from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field
from beanie import Document, PydanticObjectId
from enum import Enum

class TransactionType(str, Enum):
    """Transaction type enumeration"""
    PURCHASE = "purchase"
    PAYOUT = "payout"
    SUBSCRIPTION = "subscription"
    REFUND = "refund"
    COMMISSION = "commission"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"

class PaymentTransaction(Document):
    """Payment transaction model for tracking all payments and payouts"""
    user_id: PydanticObjectId = Field(index=True)
    
    # Transaction Details
    type: TransactionType
    amount: float
    currency: str = "INR"
    status: TransactionStatus = TransactionStatus.PENDING
    
    # Payment Gateway Details
    payment_method: PaymentMethod
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Related Items
    item_id: Optional[PydanticObjectId] = None  # For purchases
    item_type: Optional[str] = None  # template or component
    
    # Commission and Fees
    platform_fee: float = 0.0
    developer_share: float = 0.0
    tax_amount: float = 0.0
    
    # Recipient (for payouts)
    recipient_user_id: Optional[PydanticObjectId] = None
    
    # Transaction References
    reference_id: Optional[str] = None
    parent_transaction_id: Optional[PydanticObjectId] = None  # For refunds
    
    # Additional Metadata
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Timestamps
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    # Error Handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "payment_transactions"
        indexes = [
            "user_id",
            "type",
            "status",
            "payment_method",
            "razorpay_payment_id",
            "razorpay_order_id",
            "item_id",
            "recipient_user_id",
            "initiated_at",
            "completed_at",
            [("user_id", 1), ("type", 1)],  # Compound index
            [("status", 1), ("type", 1)],   # Compound index
            "created_at"
        ]

    def __repr__(self):
        return f"<PaymentTransaction(id='{self.id}', type='{self.type}', amount='{self.amount}')>"

    def __str__(self):
        return f"Transaction: {self.type} - {self.amount} {self.currency} - {self.status}"
