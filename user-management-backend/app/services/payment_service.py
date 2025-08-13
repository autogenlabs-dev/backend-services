"""
Enhanced Payment Service with Razorpay Integration for Individual Item Purchases
"""

import os
import uuid
import hashlib
import hmac
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.item_purchase import ItemPurchase, PurchaseStatus, ItemType
from app.models.shopping_cart import ShoppingCart, CartItem
from app.models.developer_earnings import DeveloperEarnings
from app.models.template import Template
from app.models.component import Component
from app.models.user import User
from app.utils.audit_logger import log_audit_event
from bson import ObjectId

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    print("Warning: razorpay package not installed. Payment functionality will be limited.")


class PaymentService:
    """Enhanced payment service for individual item purchases"""
    
    def __init__(self):
        # Razorpay configuration
        self.razorpay_key_id = os.getenv("RAZORPAY_KEY_ID", "rzp_test_your_key_id")
        self.razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET", "your_key_secret")
        
        # Initialize Razorpay client if available
        if RAZORPAY_AVAILABLE:
            try:
                self.razorpay_client = razorpay.Client(auth=(self.razorpay_key_id, self.razorpay_key_secret))
            except Exception as e:
                print(f"Failed to initialize Razorpay client: {e}")
                self.razorpay_client = None
        else:
            self.razorpay_client = None
    
    async def create_item_order(self, user: User, item_id: str, item_type: str) -> Dict[str, Any]:
        """
        Create Razorpay order for individual item purchase
        """
        try:
            # Validate item exists and get item details
            if item_type == "template":
                item = await Template.get(item_id)
                ItemModel = Template
            elif item_type == "component":
                item = await Component.get(item_id)
                ItemModel = Component
            else:
                raise ValueError("Invalid item type")
            
            if not item:
                raise ValueError("Item not found")
            
            # Check if user already purchased this item
            existing_purchase = await ItemPurchase.find_one({
                "user_id": user.id,
                "item_id": ObjectId(item_id),
                "item_type": item_type,
                "status": PurchaseStatus.COMPLETED
            })
            
            if existing_purchase:
                raise ValueError("Item already purchased")
            
            # Check if item is free
            if item.plan_type.lower() == "free":
                raise ValueError("Cannot create payment order for free item")
            
            # Get developer information
            developer = await User.get(item.user_id)
            if not developer:
                raise ValueError("Developer not found")
            
            # Create unique purchase ID
            purchase_id = f"PUR_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Prepare order data
            amount_inr = item.pricing_inr * 100  # Razorpay expects amount in paisa
            
            order_data = {
                "amount": amount_inr,
                "currency": "INR",
                "receipt": purchase_id,
                "notes": {
                    "user_id": str(user.id),
                    "item_id": item_id,
                    "item_type": item_type,
                    "item_title": item.title,
                    "developer_id": str(developer.id),
                    "developer_username": developer.username
                }
            }
            
            # Create Razorpay order
            razorpay_order = None
            if self.razorpay_client:
                try:
                    razorpay_order = self.razorpay_client.order.create(data=order_data)
                except Exception as e:
                    print(f"Razorpay order creation failed: {e}")
                    # Continue with mock order for development
            
            # Create purchase record
            purchase = ItemPurchase(
                purchase_id=purchase_id,
                user_id=user.id,
                item_id=ObjectId(item_id),
                item_type=ItemType(item_type),
                item_title=item.title,
                developer_id=developer.id,
                developer_username=developer.username,
                original_price_inr=item.pricing_inr,
                original_price_usd=item.pricing_usd,
                paid_amount_inr=item.pricing_inr,
                paid_currency="INR",
                razorpay_order_id=razorpay_order["id"] if razorpay_order else f"mock_order_{purchase_id}",
                status=PurchaseStatus.PENDING
            )
            
            # Calculate revenue split
            purchase.calculate_revenue_split()
            
            # Save purchase
            await purchase.insert()
            
            # Log audit event
            await log_audit_event(
                user_id=str(user.id),
                action="CREATE_ITEM_ORDER",
                resource_type="item_purchase",
                resource_id=str(purchase.id),
                details={
                    "item_id": item_id,
                    "item_type": item_type,
                    "amount_inr": item.pricing_inr,
                    "razorpay_order_id": purchase.razorpay_order_id
                }
            )
            
            return {
                "success": True,
                "purchase_id": purchase_id,
                "razorpay_order_id": purchase.razorpay_order_id,
                "amount_inr": item.pricing_inr,
                "amount_paisa": amount_inr,
                "currency": "INR",
                "item_details": {
                    "id": item_id,
                    "title": item.title,
                    "type": item_type,
                    "developer": developer.username
                },
                "razorpay_key_id": self.razorpay_key_id
            }
            
        except Exception as e:
            print(f"Create item order error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_item_purchase(self, user: User, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify Razorpay payment and grant access to item
        """
        try:
            razorpay_payment_id = payment_data.get("razorpay_payment_id")
            razorpay_order_id = payment_data.get("razorpay_order_id")
            razorpay_signature = payment_data.get("razorpay_signature")
            
            if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
                raise ValueError("Missing payment verification data")
            
            # Find purchase record
            purchase = await ItemPurchase.find_one({
                "razorpay_order_id": razorpay_order_id,
                "user_id": user.id,
                "status": PurchaseStatus.PENDING
            })
            
            if not purchase:
                raise ValueError("Purchase record not found")
            
            # Verify Razorpay signature
            if self.razorpay_client and not razorpay_order_id.startswith("mock_"):
                try:
                    # Verify signature
                    params_dict = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_payment_id': razorpay_payment_id,
                        'razorpay_signature': razorpay_signature
                    }
                    self.razorpay_client.utility.verify_payment_signature(params_dict)
                    
                    # Get payment details from Razorpay
                    payment_details = self.razorpay_client.payment.fetch(razorpay_payment_id)
                    
                    # Update purchase with payment details
                    purchase.payment_gateway_response = payment_details
                    purchase.payment_method = payment_details.get("method", "unknown")
                    
                except Exception as e:
                    print(f"Razorpay verification failed: {e}")
                    # For development, allow mock payments to proceed
                    if not razorpay_order_id.startswith("mock_"):
                        raise ValueError("Payment verification failed")
            
            # Mark purchase as completed
            purchase.mark_completed(razorpay_payment_id, razorpay_signature)
            await purchase.save()
            
            # Update developer earnings
            await self._update_developer_earnings(purchase)
            
            # Update item sales count
            await self._update_item_sales_count(purchase)
            
            # Log audit event
            await log_audit_event(
                user_id=str(user.id),
                action="VERIFY_ITEM_PURCHASE",
                resource_type="item_purchase",
                resource_id=str(purchase.id),
                details={
                    "item_id": str(purchase.item_id),
                    "item_type": purchase.item_type,
                    "amount_inr": purchase.paid_amount_inr,
                    "razorpay_payment_id": razorpay_payment_id
                }
            )
            
            return {
                "success": True,
                "purchase_id": purchase.purchase_id,
                "message": "Payment verified successfully",
                "access_granted": True,
                "item_details": {
                    "id": str(purchase.item_id),
                    "title": purchase.item_title,
                    "type": purchase.item_type
                }
            }
            
        except Exception as e:
            print(f"Verify item purchase error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_cart_order(self, user: User, cart_items: List[CartItem]) -> Dict[str, Any]:
        """
        Create Razorpay order for multiple items in cart
        """
        try:
            if not cart_items:
                raise ValueError("Cart is empty")
            
            # Calculate total amount
            total_amount_inr = sum(item.price_inr for item in cart_items)
            
            # Create batch purchase ID
            batch_purchase_id = f"BATCH_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Prepare order data
            amount_paisa = total_amount_inr * 100
            
            order_data = {
                "amount": amount_paisa,
                "currency": "INR",
                "receipt": batch_purchase_id,
                "notes": {
                    "user_id": str(user.id),
                    "batch_purchase": "true",
                    "item_count": len(cart_items),
                    "total_amount_inr": total_amount_inr
                }
            }
            
            # Create Razorpay order
            razorpay_order = None
            if self.razorpay_client:
                try:
                    razorpay_order = self.razorpay_client.order.create(data=order_data)
                except Exception as e:
                    print(f"Razorpay batch order creation failed: {e}")
            
            # Create individual purchase records for each item
            purchase_ids = []
            for cart_item in cart_items:
                # Get item details
                if cart_item.item_type == "template":
                    item = await Template.get(cart_item.item_id)
                else:
                    item = await Component.get(cart_item.item_id)
                
                if not item:
                    continue
                
                # Get developer
                developer = await User.get(item.user_id)
                if not developer:
                    continue
                
                # Create individual purchase record
                purchase_id = f"PUR_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
                purchase = ItemPurchase(
                    purchase_id=purchase_id,
                    user_id=user.id,
                    item_id=cart_item.item_id,
                    item_type=ItemType(cart_item.item_type),
                    item_title=cart_item.item_title,
                    developer_id=developer.id,
                    developer_username=developer.username,
                    original_price_inr=cart_item.price_inr,
                    original_price_usd=cart_item.price_usd,
                    paid_amount_inr=cart_item.price_inr,
                    paid_currency="INR",
                    razorpay_order_id=razorpay_order["id"] if razorpay_order else f"mock_batch_{batch_purchase_id}",
                    status=PurchaseStatus.PENDING
                )
                
                purchase.calculate_revenue_split()
                await purchase.insert()
                purchase_ids.append(purchase_id)
            
            return {
                "success": True,
                "batch_purchase_id": batch_purchase_id,
                "purchase_ids": purchase_ids,
                "razorpay_order_id": razorpay_order["id"] if razorpay_order else f"mock_batch_{batch_purchase_id}",
                "total_amount_inr": total_amount_inr,
                "amount_paisa": amount_paisa,
                "currency": "INR",
                "item_count": len(cart_items),
                "razorpay_key_id": self.razorpay_key_id
            }
            
        except Exception as e:
            print(f"Create cart order error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_cart_purchase(self, user: User, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify cart purchase and grant access to all items
        """
        try:
            razorpay_payment_id = payment_data.get("razorpay_payment_id")
            razorpay_order_id = payment_data.get("razorpay_order_id")
            razorpay_signature = payment_data.get("razorpay_signature")
            
            # Find all purchases for this order
            purchases = await ItemPurchase.find({
                "razorpay_order_id": razorpay_order_id,
                "user_id": user.id,
                "status": PurchaseStatus.PENDING
            }).to_list()
            
            if not purchases:
                raise ValueError("No pending purchases found for this order")
            
            # Verify signature (similar to individual item)
            if self.razorpay_client and not razorpay_order_id.startswith("mock_"):
                try:
                    params_dict = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_payment_id': razorpay_payment_id,
                        'razorpay_signature': razorpay_signature
                    }
                    self.razorpay_client.utility.verify_payment_signature(params_dict)
                except Exception as e:
                    print(f"Cart payment verification failed: {e}")
                    if not razorpay_order_id.startswith("mock_"):
                        raise ValueError("Payment verification failed")
            
            # Mark all purchases as completed
            completed_items = []
            for purchase in purchases:
                purchase.mark_completed(razorpay_payment_id, razorpay_signature)
                await purchase.save()
                
                # Update developer earnings
                await self._update_developer_earnings(purchase)
                
                # Update item sales count
                await self._update_item_sales_count(purchase)
                
                completed_items.append({
                    "id": str(purchase.item_id),
                    "title": purchase.item_title,
                    "type": purchase.item_type
                })
            
            return {
                "success": True,
                "message": f"Payment verified for {len(completed_items)} items",
                "completed_items": completed_items,
                "total_amount_inr": sum(p.paid_amount_inr for p in purchases)
            }
            
        except Exception as e:
            print(f"Verify cart purchase error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_developer_earnings(self, purchase: ItemPurchase):
        """Update developer earnings after successful purchase"""
        try:
            # Get or create developer earnings record
            earnings = await DeveloperEarnings.find_one({"developer_id": purchase.developer_id})
            if not earnings:
                earnings = DeveloperEarnings(
                    developer_id=purchase.developer_id,
                    developer_username=purchase.developer_username
                )
            
            # Add sale earnings
            earnings.add_sale_earnings(
                purchase.paid_amount_inr,
                str(purchase.item_id),
                purchase.item_type
            )
            
            await earnings.save()
            
        except Exception as e:
            print(f"Update developer earnings error: {e}")
    
    async def _update_item_sales_count(self, purchase: ItemPurchase):
        """Update item sales/purchase count"""
        try:
            if purchase.item_type == "template":
                item = await Template.get(purchase.item_id)
            else:
                item = await Component.get(purchase.item_id)
            
            if item:
                await item.update({"$inc": {"purchase_count": 1}})
                
        except Exception as e:
            print(f"Update item sales count error: {e}")
    
    async def get_user_purchase_history(self, user: User, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get user's purchase history with pagination"""
        try:
            skip = (page - 1) * page_size
            
            # Get total count
            total_count = await ItemPurchase.count({
                "user_id": user.id,
                "status": PurchaseStatus.COMPLETED
            })
            
            # Get purchases
            purchases = await ItemPurchase.find({
                "user_id": user.id,
                "status": PurchaseStatus.COMPLETED
            }).sort([("payment_completed_at", -1)]).skip(skip).limit(page_size).to_list()
            
            # Calculate stats
            total_spent = await ItemPurchase.aggregate([
                {"$match": {"user_id": user.id, "status": PurchaseStatus.COMPLETED}},
                {"$group": {"_id": None, "total": {"$sum": "$paid_amount_inr"}}}
            ]).to_list()
            
            total_spent_amount = total_spent[0]["total"] if total_spent else 0
            
            return {
                "success": True,
                "purchases": [purchase.to_dict() for purchase in purchases],
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                },
                "statistics": {
                    "total_purchases": total_count,
                    "total_spent_inr": total_spent_amount,
                    "template_purchases": len([p for p in purchases if p.item_type == "template"]),
                    "component_purchases": len([p for p in purchases if p.item_type == "component"])
                }
            }
            
        except Exception as e:
            print(f"Get purchase history error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global payment service instance
payment_service = PaymentService()
