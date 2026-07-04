"""Razorpay payment gateway integration."""

import razorpay
from typing import Dict, Optional
from app.config.payment import OWNER_BANK_ACCOUNT
from app.utils.helpers import LoggerUtilities, GeneratorUtilities

logger = LoggerUtilities.setup_logger(__name__)


class RazorpayPaymentGateway:
    """Razorpay payment gateway integration."""

    def __init__(self, api_key: str, secret_key: str):
        """Initialize Razorpay client."""
        self.client = razorpay.Client(auth=(api_key, secret_key))
        self.api_key = api_key

    def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt_id: Optional[str] = None,
        notes: Optional[Dict] = None
    ) -> Dict:
        """Create a Razorpay order."""
        try:
            if not receipt_id:
                receipt_id = GeneratorUtilities.generate_reference_id()

            order_data = {
                "amount": int(amount * 100),  # Amount in paise
                "currency": currency,
                "receipt": receipt_id,
                "notes": notes or {}
            }

            order = self.client.order.create(order_data)
            logger.info(f"Order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            raise

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """Verify payment signature from Razorpay."""
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            logger.info(f"Payment verified: {payment_id}")
            return True
        except razorpay.BadRequestError:
            logger.error(f"Invalid signature for payment: {payment_id}")
            return False
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            raise

    def get_payment_details(self, payment_id: str) -> Dict:
        """Get payment details from Razorpay."""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment details: {str(e)}")
            raise

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        notes: Optional[Dict] = None
    ) -> Dict:
        """Refund a payment."""
        try:
            refund_data = {"notes": notes or {}}
            if amount:
                refund_data["amount"] = int(amount * 100)  # Amount in paise

            refund = self.client.payment.refund(payment_id, refund_data)
            logger.info(f"Refund processed: {refund['id']}")
            return refund
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise

    def get_refund_details(self, refund_id: str) -> Dict:
        """Get refund details."""
        try:
            refund = self.client.refund.fetch(refund_id)
            return refund
        except Exception as e:
            logger.error(f"Error fetching refund details: {str(e)}")
            raise

    def create_customer(
        self,
        email: str,
        contact: str,
        name: str
    ) -> Dict:
        """Create a customer."""
        try:
            customer = self.client.customer.create({
                "email": email,
                "contact": contact,
                "name": name
            })
            logger.info(f"Customer created: {customer['id']}")
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise

    def create_token(
        self,
        customer_id: str,
        max_amount: float,
        method: str = "emandate"
    ) -> Dict:
        """Create a token for recurring payments."""
        try:
            token = self.client.token.create({
                "customer_id": customer_id,
                "max_amount": int(max_amount * 100),
                "method": method
            })
            logger.info(f"Token created: {token['id']}")
            return token
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            raise


class PaymentProcessor:
    """Payment processing service."""

    @staticmethod
    def process_donation_payment(
        gateway: RazorpayPaymentGateway,
        amount: float,
        donor_name: str,
        donor_email: str,
        campaign_id: str,
        donor_id: str
    ) -> Dict:
        """Process a donation payment."""
        try:
            # Create order
            notes = {
                "donor_name": donor_name,
                "donor_email": donor_email,
                "campaign_id": campaign_id,
                "donor_id": donor_id,
                "type": "donation"
            }

            order = gateway.create_order(
                amount=amount,
                currency="INR",
                notes=notes
            )

            logger.info(f"Donation payment order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error processing donation payment: {str(e)}")
            raise

    @staticmethod
    def process_refund(
        gateway: RazorpayPaymentGateway,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Process a refund."""
        try:
            refund = gateway.refund_payment(
                payment_id=payment_id,
                amount=amount,
                notes={"reason": reason} if reason else None
            )

            logger.info(f"Refund processed: {refund['id']}")
            return refund
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise

    @staticmethod
    def setup_recurring_donation(
        gateway: RazorpayPaymentGateway,
        donor_name: str,
        donor_email: str,
        contact: str,
        amount: float
    ) -> Dict:
        """Setup recurring donation (subscription)."""
        try:
            # Create customer
            customer = gateway.create_customer(
                email=donor_email,
                contact=contact,
                name=donor_name
            )

            # Create token for recurring payments
            token = gateway.create_token(
                customer_id=customer['id'],
                max_amount=amount
            )

            logger.info(f"Recurring donation setup: {customer['id']}")
            return {
                "customer_id": customer['id'],
                "token_id": token['id']
            }
        except Exception as e:
            logger.error(f"Error setting up recurring donation: {str(e)}")
            raise
