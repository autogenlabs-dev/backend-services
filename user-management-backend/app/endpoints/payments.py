"""
Payment Endpoints for Individual Item Purchases and Cart Checkout
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.models.user import User
from app.models.item_purchase import ItemPurchase, PurchaseStatus
from app.models.shopping_cart import ShoppingCart, CartItem, CartItemType
from app.services.payment_service import payment_service
from app.middleware.auth import require_auth, get_current_user_from_token
from app.utils.audit_logger import log_audit_event


router = APIRouter()
security = HTTPBearer()


# Request/Response Models
class CreateItemOrderRequest(BaseModel):
    item_id: str = Field(..., description="Template or Component ID")
    item_type: str = Field(..., description="'template' or 'component'")


class VerifyItemPurchaseRequest(BaseModel):
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_signature: str = Field(..., description="Razorpay signature")


class AddToCartRequest(BaseModel):
    item_id: str = Field(..., description="Template or Component ID")
    item_type: CartItemType = Field(..., description="Item type")


class CartResponse(BaseModel):
    success: bool
    cart: Optional[Dict[str, Any]] = None
    message: str = ""


class PurchaseHistoryResponse(BaseModel):
    success: bool
    purchases: List[Dict[str, Any]] = Field(default_factory=list)
    pagination: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# Payment Endpoints
@router.post("/payments/create-item-order")
async def create_item_order(
    request: CreateItemOrderRequest,
    current_user: User = Depends(require_auth)
):
    """Create Razorpay order for individual template/component purchase"""
    try:
        result = await payment_service.create_item_order(
            user=current_user,
            item_id=request.item_id,
            item_type=request.item_type
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Payment order created successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.post("/payments/verify-item-purchase")
async def verify_item_purchase(
    request: VerifyItemPurchaseRequest,
    current_user: User = Depends(require_auth)
):
    """Verify Razorpay payment and grant access to purchased item"""
    try:
        result = await payment_service.verify_item_purchase(
            user=current_user,
            payment_data=request.dict()
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Payment verified and access granted",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")


@router.get("/user/purchased-items", response_model=PurchaseHistoryResponse)
async def get_user_purchased_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    item_type: Optional[str] = Query(None, description="Filter by item type"),
    current_user: User = Depends(require_auth)
):
    """Get user's purchase history with pagination"""
    try:
        result = await payment_service.get_user_purchase_history(
            user=current_user,
            page=page,
            page_size=page_size
        )
        
        if item_type:
            # Filter by item type if specified
            filtered_purchases = [
                p for p in result.get("purchases", [])
                if p.get("item_type") == item_type
            ]
            result["purchases"] = filtered_purchases
            result["pagination"]["total_items"] = len(filtered_purchases)
            result["pagination"]["total_pages"] = (len(filtered_purchases) + page_size - 1) // page_size
        
        return PurchaseHistoryResponse(**result)
        
    except Exception as e:
        return PurchaseHistoryResponse(
            success=False,
            error=f"Failed to get purchase history: {str(e)}"
        )


# Shopping Cart Endpoints
@router.post("/cart/add", response_model=CartResponse)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(require_auth)
):
    """Add item to shopping cart"""
    try:
        # Get item details
        if request.item_type == CartItemType.TEMPLATE:
            from app.models.template import Template
            item = await Template.get(request.item_id)
        else:
            from app.models.component import Component
            item = await Component.get(request.item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Check if item is free
        if item.plan_type.lower() == "free":
            raise HTTPException(status_code=400, detail="Cannot add free items to cart")
        
        # Check if user already purchased this item
        existing_purchase = await ItemPurchase.find_one({
            "user_id": current_user.id,
            "item_id": item.id,
            "item_type": request.item_type,
            "status": PurchaseStatus.COMPLETED
        })
        
        if existing_purchase:
            raise HTTPException(status_code=400, detail="Item already purchased")
        
        # Get or create cart
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        if not cart:
            cart = ShoppingCart(user_id=current_user.id)
        
        # Get developer info
        developer = await User.get(item.user_id)
        developer_username = developer.username if developer else "Unknown"
        
        # Create cart item
        cart_item = CartItem(
            item_id=item.id,
            item_type=request.item_type,
            item_title=item.title,
            developer_username=developer_username,
            price_inr=item.pricing_inr,
            price_usd=item.pricing_usd
        )
        
        # Add to cart
        if cart.add_item(cart_item):
            await cart.save()
            
            # Log audit event
            await log_audit_event(
                user_id=str(current_user.id),
                action="ADD_TO_CART",
                resource_type="shopping_cart",
                resource_id=str(cart.id),
                details={
                    "item_id": request.item_id,
                    "item_type": request.item_type,
                    "item_title": item.title
                }
            )
            
            return CartResponse(
                success=True,
                message="Item added to cart successfully",
                cart=cart.to_dict()
            )
        else:
            return CartResponse(
                success=False,
                message="Item already in cart"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add item to cart: {str(e)}")


@router.get("/cart", response_model=CartResponse)
async def get_cart(current_user: User = Depends(require_auth)):
    """Get user's shopping cart"""
    try:
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        
        if not cart:
            # Create empty cart
            cart = ShoppingCart(user_id=current_user.id)
            await cart.insert()
        
        # Update last accessed
        cart.last_accessed_at = datetime.now(timezone.utc)
        await cart.save()
        
        return CartResponse(
            success=True,
            message="Cart retrieved successfully",
            cart=cart.to_dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cart: {str(e)}")


@router.delete("/cart/item/{item_id}")
async def remove_from_cart(
    item_id: str,
    item_type: CartItemType,
    current_user: User = Depends(require_auth)
):
    """Remove item from shopping cart"""
    try:
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        if cart.remove_item(item_id, item_type):
            await cart.save()
            
            # Log audit event
            await log_audit_event(
                user_id=str(current_user.id),
                action="REMOVE_FROM_CART",
                resource_type="shopping_cart",
                resource_id=str(cart.id),
                details={
                    "item_id": item_id,
                    "item_type": item_type
                }
            )
            
            return {
                "success": True,
                "message": "Item removed from cart successfully",
                "cart": cart.to_dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found in cart")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove item from cart: {str(e)}")


@router.post("/cart/checkout")
async def checkout_cart(current_user: User = Depends(require_auth)):
    """Process multiple item purchase from cart"""
    try:
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Check for already purchased items
        purchased_items = []
        valid_items = []
        
        for cart_item in cart.items:
            existing_purchase = await ItemPurchase.find_one({
                "user_id": current_user.id,
                "item_id": cart_item.item_id,
                "item_type": cart_item.item_type,
                "status": PurchaseStatus.COMPLETED
            })
            
            if existing_purchase:
                purchased_items.append(cart_item.item_title)
            else:
                valid_items.append(cart_item)
        
        if not valid_items:
            raise HTTPException(status_code=400, detail="All items in cart are already purchased")
        
        # Create cart order
        result = await payment_service.create_cart_order(
            user=current_user,
            cart_items=valid_items
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Clear valid items from cart
        cart.items = [item for item in cart.items if item not in valid_items]
        cart.update_totals()
        await cart.save()
        
        response_data = {
            "success": True,
            "message": "Cart checkout order created successfully",
            "data": result
        }
        
        if purchased_items:
            response_data["warnings"] = [
                f"Skipped already purchased items: {', '.join(purchased_items)}"
            ]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to checkout cart: {str(e)}")


@router.post("/cart/verify-purchase")
async def verify_cart_purchase(
    request: VerifyItemPurchaseRequest,
    current_user: User = Depends(require_auth)
):
    """Verify cart purchase payment"""
    try:
        result = await payment_service.verify_cart_purchase(
            user=current_user,
            payment_data=request.dict()
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Cart purchase verified successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify cart purchase: {str(e)}")


@router.post("/cart/clear")
async def clear_cart(current_user: User = Depends(require_auth)):
    """Clear all items from cart"""
    try:
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        
        if cart:
            cart.clear_cart()
            await cart.save()
            
            # Log audit event
            await log_audit_event(
                user_id=str(current_user.id),
                action="CLEAR_CART",
                resource_type="shopping_cart",
                resource_id=str(cart.id),
                details={"items_cleared": len(cart.items)}
            )
        
        return {
            "success": True,
            "message": "Cart cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")


@router.get("/cart/summary")
async def get_cart_summary(current_user: User = Depends(require_auth)):
    """Get cart checkout summary"""
    try:
        cart = await ShoppingCart.find_one({"user_id": current_user.id})
        
        if not cart:
            return {
                "success": True,
                "summary": {
                    "total_items": 0,
                    "total_amount_inr": 0,
                    "total_amount_usd": 0,
                    "currency_preference": "INR",
                    "items": [],
                    "estimated_platform_fee_inr": 0,
                    "estimated_developer_earnings_inr": 0
                }
            }
        
        summary = cart.get_checkout_summary()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cart summary: {str(e)}")
