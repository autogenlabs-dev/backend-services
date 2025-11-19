"""
Developer Earnings and Payout Endpoints
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.developer_earnings import DeveloperEarnings, PayoutRequest, PayoutStatus, PayoutMethod
from app.models.item_purchase import ItemPurchase, PurchaseStatus
from app.middleware.auth import require_auth, require_admin, require_creator_or_admin
from app.utils.audit_logger import log_audit_event, ActionType


router = APIRouter()


# Request/Response Models
class PayoutRequestCreate(BaseModel):
    requested_amount_inr: int = Field(..., ge=100, description="Amount to request (minimum 100 INR)")
    payout_method: PayoutMethod = Field(..., description="Preferred payout method")
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    bank_ifsc_code: Optional[str] = Field(None, description="Bank IFSC code")
    bank_account_name: Optional[str] = Field(None, description="Account holder name")
    upi_id: Optional[str] = Field(None, description="UPI ID")
    paypal_email: Optional[str] = Field(None, description="PayPal email")


class PayoutRequestUpdate(BaseModel):
    status: PayoutStatus = Field(..., description="New status")
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")


class EarningsResponse(BaseModel):
    success: bool
    earnings: Optional[Dict[str, Any]] = None
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PayoutRequestResponse(BaseModel):
    success: bool
    payout_request: Optional[Dict[str, Any]] = None
    message: str = ""
    error: Optional[str] = None


# Developer Earnings Endpoints
@router.get("/developer/earnings", response_model=EarningsResponse)
async def get_developer_earnings(
    current_user: User = Depends(require_creator_or_admin)
):
    """Get developer's earnings dashboard with analytics"""
    try:
        
        # Get or create earnings record
        earnings = await DeveloperEarnings.find_one({"developer_id": current_user.id})
        if not earnings:
            earnings = DeveloperEarnings(
                developer_id=current_user.id,
                developer_username=current_user.username
            )
            await earnings.insert()
        
        # Get detailed analytics
        analytics = earnings.get_analytics_summary()
        
        # Get recent sales
        recent_sales = await ItemPurchase.find({
            "developer_id": current_user.id,
            "status": PurchaseStatus.COMPLETED
        }).sort([("payment_completed_at", -1)]).limit(10).to_list()
        
        analytics["recent_sales"] = [
            {
                "item_title": sale.item_title,
                "item_type": sale.item_type,
                "amount_inr": sale.paid_amount_inr,
                "developer_earnings_inr": sale.developer_earnings_inr,
                "payment_date": sale.payment_completed_at.isoformat() if sale.payment_completed_at else None,
                "buyer_username": "Anonymous"  # Keep buyer privacy
            }
            for sale in recent_sales
        ]
        
        # Get pending payout requests
        pending_payouts = await PayoutRequest.find({
            "developer_id": current_user.id,
            "status": {"$in": [PayoutStatus.PENDING, PayoutStatus.APPROVED, PayoutStatus.PROCESSING]}
        }).sort([("created_at", -1)]).to_list()
        
        analytics["pending_payouts"] = [payout.to_dict() for payout in pending_payouts]
        
        return EarningsResponse(
            success=True,
            earnings=earnings.to_dict(),
            analytics=analytics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return EarningsResponse(
            success=False,
            error=f"Failed to get earnings: {str(e)}"
        )


@router.post("/developer/payout-request", response_model=PayoutRequestResponse)
async def create_payout_request(
    request: PayoutRequestCreate,
    current_user: User = Depends(require_creator_or_admin)
):
    """Request earnings payout"""
    try:
        # Access controlled by dependency: creator or admin
        
        # Get earnings record
        earnings = await DeveloperEarnings.find_one({"developer_id": current_user.id})
        if not earnings:
            raise HTTPException(status_code=404, detail="No earnings record found")
        
        # Validate request amount
        if request.requested_amount_inr > earnings.available_balance_inr:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Available: ₹{earnings.available_balance_inr}"
            )
        
        if request.requested_amount_inr < earnings.minimum_payout_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum payout amount is ₹{earnings.minimum_payout_amount}"
            )
        
        # Validate payment method details
        if request.payout_method == PayoutMethod.BANK_TRANSFER:
            if not all([request.bank_account_number, request.bank_ifsc_code, request.bank_account_name]):
                raise HTTPException(status_code=400, detail="Bank details required for bank transfer")
        elif request.payout_method == PayoutMethod.UPI:
            if not request.upi_id:
                raise HTTPException(status_code=400, detail="UPI ID required for UPI transfer")
        elif request.payout_method == PayoutMethod.PAYPAL:
            if not request.paypal_email:
                raise HTTPException(status_code=400, detail="PayPal email required for PayPal transfer")
        
        # Check for existing pending requests
        existing_pending = await PayoutRequest.find_one({
            "developer_id": current_user.id,
            "status": {"$in": [PayoutStatus.PENDING, PayoutStatus.APPROVED, PayoutStatus.PROCESSING]}
        })
        
        if existing_pending:
            raise HTTPException(status_code=400, detail="You have a pending payout request")
        
        # Create payout request
        request_id = f"PAYOUT_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:8]}"
        
        payout_request = PayoutRequest(
            request_id=request_id,
            developer_id=current_user.id,
            developer_username=current_user.username,
            requested_amount_inr=request.requested_amount_inr,
            payout_method=request.payout_method,
            bank_account_number=request.bank_account_number,
            bank_ifsc_code=request.bank_ifsc_code,
            bank_account_name=request.bank_account_name,
            upi_id=request.upi_id,
            paypal_email=request.paypal_email
        )
        
        await payout_request.insert()
        
        # Update earnings (move from available to pending)
        earnings.process_payout_request(request.requested_amount_inr)
        await earnings.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action_type=ActionType.PAYOUT_REQUESTED,
            action_description=f"Developer {current_user.username} requested payout of ₹{request.requested_amount_inr}",
            resource_type="payout_request",
            resource_id=str(payout_request.id),
            details={
                "amount_inr": request.requested_amount_inr,
                "payout_method": request.payout_method,
                "request_id": request_id
            }
        )
        
        return PayoutRequestResponse(
            success=True,
            message="Payout request created successfully",
            payout_request=payout_request.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return PayoutRequestResponse(
            success=False,
            error=f"Failed to create payout request: {str(e)}"
        )


@router.get("/developer/payout-requests")
async def get_payout_requests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[PayoutStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_creator_or_admin)
):
    """Get developer's payout request history"""
    try:
        # Access controlled by dependency: creator or admin
        
        # Build query
        query = {"developer_id": current_user.id}
        if status:
            query["status"] = status
        
        # Get total count
        total_count = await PayoutRequest.count(query)
        
        # Get payout requests
        skip = (page - 1) * page_size
        payout_requests = await PayoutRequest.find(query)\
            .sort([("created_at", -1)])\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        return {
            "success": True,
            "payout_requests": [req.to_dict() for req in payout_requests],
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payout requests: {str(e)}")


@router.put("/developer/earnings/settings")
async def update_earnings_settings(
    auto_payout_enabled: Optional[bool] = None,
    minimum_payout_amount: Optional[int] = None,
    preferred_payout_method: Optional[PayoutMethod] = None,
    bank_account_number: Optional[str] = None,
    bank_ifsc_code: Optional[str] = None,
    bank_account_name: Optional[str] = None,
    upi_id: Optional[str] = None,
    paypal_email: Optional[str] = None,
    current_user: User = Depends(require_creator_or_admin)
):
    """Update developer earnings settings"""
    try:
        # Access controlled by dependency: creator or admin
        
        # Get earnings record
        earnings = await DeveloperEarnings.find_one({"developer_id": current_user.id})
        if not earnings:
            earnings = DeveloperEarnings(
                developer_id=current_user.id,
                developer_username=current_user.username
            )
        
        # Update settings
        update_data = {}
        if auto_payout_enabled is not None:
            update_data["auto_payout_enabled"] = auto_payout_enabled
        if minimum_payout_amount is not None:
            if minimum_payout_amount < 100:
                raise HTTPException(status_code=400, detail="Minimum payout amount must be at least ₹100")
            update_data["minimum_payout_amount"] = minimum_payout_amount
        if preferred_payout_method is not None:
            update_data["preferred_payout_method"] = preferred_payout_method
        if bank_account_number is not None:
            update_data["bank_account_number"] = bank_account_number
        if bank_ifsc_code is not None:
            update_data["bank_ifsc_code"] = bank_ifsc_code
        if bank_account_name is not None:
            update_data["bank_account_name"] = bank_account_name
        if upi_id is not None:
            update_data["upi_id"] = upi_id
        if paypal_email is not None:
            update_data["paypal_email"] = paypal_email
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await earnings.update({"$set": update_data})
        
        return {
            "success": True,
            "message": "Earnings settings updated successfully",
            "settings": earnings.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


# Admin Payout Management Endpoints
@router.get("/admin/payout-requests")
async def admin_get_payout_requests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[PayoutStatus] = Query(None, description="Filter by status"),
    developer_id: Optional[str] = Query(None, description="Filter by developer"),
    current_user: User = Depends(require_admin)
):
    """Get all payout requests for admin review"""
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        if developer_id:
            query["developer_id"] = developer_id
        
        # Get total count
        total_count = await PayoutRequest.count(query)
        
        # Get payout requests
        skip = (page - 1) * page_size
        payout_requests = await PayoutRequest.find(query)\
            .sort([("created_at", -1)])\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        # Get statistics
        stats = await PayoutRequest.aggregate([
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$requested_amount_inr"}
            }}
        ]).to_list()
        
        statistics = {stat["_id"]: {"count": stat["count"], "total_amount": stat["total_amount"]} for stat in stats}
        
        return {
            "success": True,
            "payout_requests": [req.to_dict() for req in payout_requests],
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            },
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payout requests: {str(e)}")


@router.put("/admin/payout-requests/{request_id}")
async def admin_update_payout_request(
    request_id: str,
    update: PayoutRequestUpdate,
    current_user: User = Depends(require_admin)
):
    """Update payout request status (admin only)"""
    try:
        # Get payout request
        payout_request = await PayoutRequest.find_one({"request_id": request_id})
        if not payout_request:
            raise HTTPException(status_code=404, detail="Payout request not found")
        
        # Update status based on action
        if update.status == PayoutStatus.APPROVED:
            payout_request.approve_request(current_user.id, update.admin_notes or "")
        elif update.status == PayoutStatus.REJECTED:
            if not update.rejection_reason:
                raise HTTPException(status_code=400, detail="Rejection reason required")
            
            payout_request.reject_request(current_user.id, update.rejection_reason)
            
            # Return money to developer's available balance
            earnings = await DeveloperEarnings.find_one({"developer_id": payout_request.developer_id})
            if earnings:
                earnings.cancel_payout_request(payout_request.requested_amount_inr)
                await earnings.save()
        
        await payout_request.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action_type=ActionType.PAYOUT_APPROVED if update.status == PayoutStatus.APPROVED else ActionType.SETTINGS_UPDATED,
            action_description=f"Admin {current_user.username} {update.status} payout request {request_id}",
            resource_type="payout_request",
            resource_id=str(payout_request.id),
            details={
                "new_status": update.status,
                "amount_inr": payout_request.requested_amount_inr,
                "developer_id": str(payout_request.developer_id),
                "admin_notes": update.admin_notes,
                "rejection_reason": update.rejection_reason
            }
        )
        
        return {
            "success": True,
            "message": f"Payout request {update.status} successfully",
            "payout_request": payout_request.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payout request: {str(e)}")


@router.post("/admin/payout-requests/{request_id}/complete")
async def admin_complete_payout(
    request_id: str,
    transaction_id: str,
    final_amount_paid: int,
    processing_fee: int = 0,
    current_user: User = Depends(require_admin)
):
    """Mark payout as completed (admin only)"""
    try:
        # Get payout request
        payout_request = await PayoutRequest.find_one({"request_id": request_id})
        if not payout_request:
            raise HTTPException(status_code=404, detail="Payout request not found")
        
        if payout_request.status != PayoutStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Payout request must be approved first")
        
        # Mark as processing first
        payout_request.start_processing(transaction_id)
        await payout_request.save()
        
        # Complete payout
        payout_request.complete_payout(final_amount_paid, processing_fee)
        await payout_request.save()
        
        # Update developer earnings
        earnings = await DeveloperEarnings.find_one({"developer_id": payout_request.developer_id})
        if earnings:
            earnings.complete_payout(payout_request.requested_amount_inr)
            await earnings.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action_type=ActionType.PAYOUT_APPROVED,
            action_description=f"Admin {current_user.username} completed payout {request_id}",
            resource_type="payout_request",
            resource_id=str(payout_request.id),
            details={
                "transaction_id": transaction_id,
                "final_amount_paid": final_amount_paid,
                "processing_fee": processing_fee,
                "developer_id": str(payout_request.developer_id)
            }
        )
        
        return {
            "success": True,
            "message": "Payout completed successfully",
            "payout_request": payout_request.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete payout: {str(e)}")
