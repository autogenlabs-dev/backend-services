"""
Developer Earnings and Payout System
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from beanie import Document
from pydantic import Field, BaseModel
from bson import ObjectId

# Use PydanticObjectId for consistency
try:
    from beanie import PydanticObjectId
except ImportError:
    from bson import ObjectId as PydanticObjectId


class PayoutStatus(str, Enum):
    """Payout request status"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PayoutMethod(str, Enum):
    """Available payout methods"""
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    PAYPAL = "paypal"
    RAZORPAY_ACCOUNT = "razorpay_account"


class EarningsBreakdown(BaseModel):
    """Earnings breakdown by item"""
    item_id: PydanticObjectId
    item_type: str  # template or component
    item_title: str
    sales_count: int
    total_earnings_inr: int
    average_sale_price_inr: int
    first_sale_date: datetime
    last_sale_date: Optional[datetime]


class DeveloperEarnings(Document):
    """Developer earnings tracking and analytics"""
    
    # Developer Information
    developer_id: PydanticObjectId = Field(..., description="Developer user ID")
    developer_username: str = Field(..., description="Developer username")
    
    # Earnings Summary
    total_earnings_inr: int = Field(default=0, description="Total lifetime earnings in INR")
    available_balance_inr: int = Field(default=0, description="Available for payout")
    pending_balance_inr: int = Field(default=0, description="Pending in payout requests")
    withdrawn_total_inr: int = Field(default=0, description="Total amount withdrawn")
    
    # Sales Statistics
    total_sales_count: int = Field(default=0, description="Total number of sales")
    template_sales_count: int = Field(default=0, description="Template sales")
    component_sales_count: int = Field(default=0, description="Component sales")
    
    # Performance Metrics
    average_sale_amount_inr: int = Field(default=0, description="Average sale amount")
    best_selling_item_id: Optional[PydanticObjectId] = Field(None, description="Best selling item")
    best_selling_item_type: Optional[str] = Field(None, description="Best selling item type")
    
    # Monthly Analytics (Last 12 months)
    monthly_earnings: Dict[str, int] = Field(default_factory=dict, description="Monthly earnings breakdown")
    monthly_sales: Dict[str, int] = Field(default_factory=dict, description="Monthly sales count")
    
    # Bank/Payment Information
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    bank_ifsc_code: Optional[str] = Field(None, description="Bank IFSC code")
    bank_account_name: Optional[str] = Field(None, description="Account holder name")
    upi_id: Optional[str] = Field(None, description="UPI ID")
    paypal_email: Optional[str] = Field(None, description="PayPal email")
    preferred_payout_method: PayoutMethod = Field(default=PayoutMethod.BANK_TRANSFER)
    
    # Tax Information
    pan_number: Optional[str] = Field(None, description="PAN number for tax purposes")
    gst_number: Optional[str] = Field(None, description="GST number if applicable")
    tax_exemption_certificate: Optional[str] = Field(None, description="Tax exemption certificate")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_payout_date: Optional[datetime] = Field(None, description="Last successful payout")
    
    # Platform Settings
    auto_payout_enabled: bool = Field(default=False, description="Enable automatic payouts")
    minimum_payout_amount: int = Field(default=1000, description="Minimum payout amount in INR")
    
    class Settings:
        name = "developer_earnings"
        indexes = [
            [("developer_id", 1)],  # One record per developer
            [("total_earnings_inr", -1)],
            [("available_balance_inr", -1)],
            [("total_sales_count", -1)],
            [("updated_at", -1)]
        ]
        use_state_management = True

    def add_sale_earnings(self, sale_amount: int, item_id: str, item_type: str):
        """Add earnings from a new sale"""
        earnings = int(sale_amount * 0.70)  # 70% to developer
        
        self.total_earnings_inr += earnings
        self.available_balance_inr += earnings
        self.total_sales_count += 1
        
        if item_type == "template":
            self.template_sales_count += 1
        else:
            self.component_sales_count += 1
        
        # Update average
        if self.total_sales_count > 0:
            self.average_sale_amount_inr = self.total_earnings_inr // self.total_sales_count
        
        # Update monthly stats
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        self.monthly_earnings[current_month] = self.monthly_earnings.get(current_month, 0) + earnings
        self.monthly_sales[current_month] = self.monthly_sales.get(current_month, 0) + 1
        
        self.updated_at = datetime.now(timezone.utc)

    def process_payout_request(self, amount: int) -> bool:
        """Process a payout request (move from available to pending)"""
        if amount <= self.available_balance_inr:
            self.available_balance_inr -= amount
            self.pending_balance_inr += amount
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def complete_payout(self, amount: int):
        """Complete a payout (move from pending to withdrawn)"""
        if amount <= self.pending_balance_inr:
            self.pending_balance_inr -= amount
            self.withdrawn_total_inr += amount
            self.last_payout_date = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

    def cancel_payout_request(self, amount: int):
        """Cancel a payout request (move from pending back to available)"""
        if amount <= self.pending_balance_inr:
            self.pending_balance_inr -= amount
            self.available_balance_inr += amount
            self.updated_at = datetime.now(timezone.utc)

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        return {
            "total_earnings_inr": self.total_earnings_inr,
            "available_balance_inr": self.available_balance_inr,
            "pending_balance_inr": self.pending_balance_inr,
            "withdrawn_total_inr": self.withdrawn_total_inr,
            "total_sales_count": self.total_sales_count,
            "template_sales_count": self.template_sales_count,
            "component_sales_count": self.component_sales_count,
            "average_sale_amount_inr": self.average_sale_amount_inr,
            "monthly_earnings": self.monthly_earnings,
            "monthly_sales": self.monthly_sales,
            "conversion_rate": round((self.total_sales_count / max(1, self.total_sales_count)) * 100, 2),
            "last_payout_date": self.last_payout_date.isoformat() if self.last_payout_date else None
        }

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "developer_id": str(self.developer_id),
            "developer_username": self.developer_username,
            "total_earnings_inr": self.total_earnings_inr,
            "available_balance_inr": self.available_balance_inr,
            "pending_balance_inr": self.pending_balance_inr,
            "withdrawn_total_inr": self.withdrawn_total_inr,
            "total_sales_count": self.total_sales_count,
            "template_sales_count": self.template_sales_count,
            "component_sales_count": self.component_sales_count,
            "average_sale_amount_inr": self.average_sale_amount_inr,
            "preferred_payout_method": self.preferred_payout_method,
            "minimum_payout_amount": self.minimum_payout_amount,
            "auto_payout_enabled": self.auto_payout_enabled,
            "bank_account_configured": bool(self.bank_account_number and self.bank_ifsc_code),
            "upi_configured": bool(self.upi_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_payout_date": self.last_payout_date.isoformat() if self.last_payout_date else None
        }


class PayoutRequest(Document):
    """Developer payout request model"""
    
    # Request Information
    request_id: str = Field(..., description="Unique payout request ID")
    developer_id: PydanticObjectId = Field(..., description="Developer user ID")
    developer_username: str = Field(..., description="Developer username")
    
    # Payout Details
    requested_amount_inr: int = Field(..., description="Requested amount in INR")
    payout_method: PayoutMethod = Field(..., description="Preferred payout method")
    
    # Bank/Payment Details (snapshot at time of request)
    bank_account_number: Optional[str] = Field(None)
    bank_ifsc_code: Optional[str] = Field(None)
    bank_account_name: Optional[str] = Field(None)
    upi_id: Optional[str] = Field(None)
    paypal_email: Optional[str] = Field(None)
    
    # Request Status
    status: PayoutStatus = Field(default=PayoutStatus.PENDING)
    
    # Admin Processing
    reviewed_by: Optional[PydanticObjectId] = Field(None, description="Admin who reviewed")
    admin_notes: Optional[str] = Field(None, description="Admin review notes")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    
    # Processing Information
    transaction_id: Optional[str] = Field(None, description="Bank/Gateway transaction ID")
    processing_fee: int = Field(default=0, description="Processing fee charged")
    final_amount_paid: Optional[int] = Field(None, description="Final amount after fees")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(None)
    processed_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Tax and Compliance
    tds_deducted: int = Field(default=0, description="TDS amount deducted")
    tax_certificate_url: Optional[str] = Field(None, description="TDS certificate URL")
    
    class Settings:
        name = "payout_requests"
        indexes = [
            [("developer_id", 1)],
            [("status", 1)],
            [("created_at", -1)],
            [("request_id", 1)],
            [("developer_id", 1), ("status", 1)],
            [("reviewed_by", 1)],
            [("completed_at", -1)]
        ]
        use_state_management = True

    def approve_request(self, admin_id: PydanticObjectId, admin_notes: str = ""):
        """Approve payout request"""
        self.status = PayoutStatus.APPROVED
        self.reviewed_by = admin_id
        self.admin_notes = admin_notes
        self.reviewed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def reject_request(self, admin_id: PydanticObjectId, rejection_reason: str):
        """Reject payout request"""
        self.status = PayoutStatus.REJECTED
        self.reviewed_by = admin_id
        self.rejection_reason = rejection_reason
        self.reviewed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def start_processing(self, transaction_id: str):
        """Start processing payout"""
        self.status = PayoutStatus.PROCESSING
        self.transaction_id = transaction_id
        self.processed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def complete_payout(self, final_amount: int, processing_fee: int = 0):
        """Complete payout processing"""
        self.status = PayoutStatus.COMPLETED
        self.final_amount_paid = final_amount
        self.processing_fee = processing_fee
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "request_id": self.request_id,
            "developer_id": str(self.developer_id),
            "developer_username": self.developer_username,
            "requested_amount_inr": self.requested_amount_inr,
            "payout_method": self.payout_method,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "rejection_reason": self.rejection_reason,
            "transaction_id": self.transaction_id,
            "processing_fee": self.processing_fee,
            "final_amount_paid": self.final_amount_paid,
            "tds_deducted": self.tds_deducted,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "bank_details_configured": bool(self.bank_account_number and self.bank_ifsc_code),
            "payment_method_configured": bool(
                (self.payout_method == PayoutMethod.BANK_TRANSFER and self.bank_account_number) or
                (self.payout_method == PayoutMethod.UPI and self.upi_id) or
                (self.payout_method == PayoutMethod.PAYPAL and self.paypal_email)
            )
        }

    def __repr__(self):
        return f"<PayoutRequest(request_id='{self.request_id}', amount={self.requested_amount_inr}, status='{self.status}')>"
