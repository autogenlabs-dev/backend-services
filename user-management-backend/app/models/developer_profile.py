from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field, EmailStr
from beanie import Document, PydanticObjectId
from enum import Enum

class PayoutMethod(str, Enum):
    """Payout method enumeration"""
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    PAYPAL = "paypal"
    RAZORPAY_WALLET = "razorpay_wallet"

class DeveloperProfile(Document):
    """Developer profile model for MongoDB"""
    user_id: PydanticObjectId = Field(index=True)
    
    # Professional Information
    profession: Optional[str] = None
    experience_years: Optional[int] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    
    # Payment Details
    payment_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    bank_account: Optional[str] = None
    tax_id: Optional[str] = None
    payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    
    # Additional Information
    company: Optional[str] = None
    location: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Verification Status
    is_verified: bool = False
    verification_documents: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "developer_profiles"
        indexes = [
            "user_id",
            "is_verified",
            "is_active",
            "created_at"
        ]

    def __repr__(self):
        return f"<DeveloperProfile(user_id='{self.user_id}')>"

    def __str__(self):
        return f"Developer Profile for {self.user_id}"
