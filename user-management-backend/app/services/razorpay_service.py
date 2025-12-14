"""Razorpay payment service for handling payments in INR."""

import razorpay
import os
from typing import Dict, Any, Optional
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class RazorpayService:
    """Service for handling Razorpay payments."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client = razorpay.Client(
            auth=(
                settings.razorpay_key_id,
                settings.razorpay_key_secret
            )
        )
    
    async def create_order(
        self, 
        amount_inr: float, 
        plan_name: str, 
        user_email: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order for a subscription plan.
        
        Args:
            amount_inr: Amount in INR
            plan_name: Name of the subscription plan
            user_email: User's email address
            user_id: User's ID
            
        Returns:
            Dict containing order details
        """
        try:
            # Convert INR to paisa (Razorpay uses paisa)
            amount_paisa = int(amount_inr * 100)
            
            # Create order data
            order_data = {
                "amount": amount_paisa,
                "currency": "INR",
                "receipt": f"rcpt_{user_id[-8:]}_{plan_name[:10]}_{int(datetime.now().timestamp())}",
                "notes": {
                    "plan_name": plan_name,
                    "user_email": user_email,
                    "user_id": user_id,
                    "amount_inr": str(amount_inr)
                }
            }
            
            # Create order with Razorpay
            order = self.client.order.create(data=order_data)
            
            # Store order in database
            await self._store_order(order, user_id, plan_name, amount_inr)
            
            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "amount_inr": amount_inr,
                "key_id": settings.razorpay_key_id
            }
            
        except Exception as e:
            error_msg = f"Failed to create Razorpay order: {str(e)}"
            logger.error(error_msg)
            # Write to file for debugging
            try:
                with open("razorpay_error.log", "a") as f:
                    f.write(f"{datetime.now()}: {error_msg}\n")
                    import traceback
                    f.write(traceback.format_exc() + "\n")
            except:
                pass
            raise Exception(f"Payment order creation failed: {str(e)}")
    
    async def verify_payment(
        self, 
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> Dict[str, Any]:
        """
        Verify Razorpay payment signature and process the payment.
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Razorpay signature for verification
            
        Returns:
            Dict containing verification result
        """
        try:
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # This will raise an exception if signature is invalid
            self.client.utility.verify_payment_signature(params_dict)
            
            # Get payment details
            payment = self.client.payment.fetch(razorpay_payment_id)
            order = self.client.order.fetch(razorpay_order_id)
            
            # Update order status in database
            await self._update_order_status(
                order_id=razorpay_order_id,
                payment_id=razorpay_payment_id,
                status="completed",
                payment_details=payment
            )
            
            return {
                "verified": True,
                "payment_id": razorpay_payment_id,
                "order_id": razorpay_order_id,
                "amount": payment["amount"],
                "currency": payment["currency"],
                "status": payment["status"],
                "method": payment["method"],
                "user_id": order["notes"]["user_id"],
                "plan_name": order["notes"]["plan_name"]
            }
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            await self._update_order_status(
                order_id=razorpay_order_id,
                payment_id=razorpay_payment_id,
                status="failed",
                error=str(e)
            )
            raise Exception(f"Payment verification failed: {str(e)}")
    
    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details from Razorpay."""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch payment details: {str(e)}")
            raise Exception(f"Failed to fetch payment details: {str(e)}")
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Refund a payment."""
        try:
            refund_data = {}
            if amount:
                refund_data["amount"] = amount
            
            refund = self.client.payment.refund(payment_id, refund_data)
            return refund
        except Exception as e:
            logger.error(f"Failed to refund payment: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")
    
    async def _store_order(
        self, 
        order: Dict[str, Any], 
        user_id: str, 
        plan_name: str, 
        amount_inr: float
    ):
        """Store order details in database."""
        try:
            order_doc = {
                "razorpay_order_id": order["id"],
                "user_id": user_id,
                "plan_name": plan_name,
                "amount_inr": amount_inr,
                "amount_paisa": order["amount"],
                "currency": order["currency"],
                "status": "created",
                "created_at": datetime.now(timezone.utc),
                "receipt": order["receipt"],
                "notes": order["notes"]
            }
            
            await self.db.razorpay_orders.insert_one(order_doc)
            
        except Exception as e:
            logger.error(f"Failed to store order in database: {str(e)}")
            # Don't raise here as the order was created successfully in Razorpay
    
    async def _update_order_status(
        self,
        order_id: str,
        payment_id: str,
        status: str,
        payment_details: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update order status in database."""
        try:
            update_data = {
                "status": status,
                "payment_id": payment_id,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if payment_details:
                update_data["payment_details"] = payment_details
            
            if error:
                update_data["error"] = error
            
            await self.db.razorpay_orders.update_one(
                {"razorpay_order_id": order_id},
                {"$set": update_data}
            )
            
        except Exception as e:
            logger.error(f"Failed to update order status: {str(e)}")
    
    async def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details from database."""
        try:
            order = await self.db.razorpay_orders.find_one({"razorpay_order_id": order_id})
            return order
        except Exception as e:
            logger.error(f"Failed to fetch order from database: {str(e)}")
            return None
    
    async def get_user_orders(self, user_id: str) -> list:
        """Get all orders for a user."""
        try:
            cursor = self.db.razorpay_orders.find({"user_id": user_id})
            orders = await cursor.to_list(length=None)
            return orders
        except Exception as e:
            logger.error(f"Failed to fetch user orders: {str(e)}")
            return []
