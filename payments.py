from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Transaction, Donation
from app.schemas.schemas import TransactionResponse, DonationCreate
from app.config.payment import OWNER_CONFIG
from app.services.payment import PaymentProcessor
from app.utils.helpers import LoggerUtilities, GeneratorUtilities
from typing import Dict
import os

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
logger = LoggerUtilities.setup_logger(__name__)


@router.post("/initiate")
async def initiate_payment(
    donation_data: DonationCreate,
    db: Session = Depends(get_db)
) -> Dict:
    """Initiate a donation payment."""
    try:
        # Import here to avoid circular imports
        from app.services.payment import RazorpayPaymentGateway
        
        # Initialize Razorpay gateway
        razorpay_key = os.getenv("RAZORPAY_KEY_ID")
        razorpay_secret = os.getenv("RAZORPAY_SECRET_KEY")
        
        if not razorpay_key or not razorpay_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment gateway not configured"
            )
        
        gateway = RazorpayPaymentGateway(razorpay_key, razorpay_secret)
        
        # Process payment
        order = PaymentProcessor.process_donation_payment(
            gateway=gateway,
            amount=donation_data.amount,
            donor_name=donation_data.donor_name,
            donor_email=donation_data.donor_email,
            campaign_id=donation_data.campaign_id,
            donor_id=donation_data.donor_id
        )
        
        # Create transaction record
        transaction = Transaction(
            id=GeneratorUtilities.generate_uuid(),
            donor_id=donation_data.donor_id,
            amount=donation_data.amount,
            currency="INR",
            type="donation",
            status="pending",
            payment_gateway="razorpay",
            reference_id=order['id']
        )
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"Payment initiated for donation: {order['id']}")
        
        return {
            "order_id": order['id'],
            "amount": order['amount'] / 100,
            "currency": order['currency'],
            "key_id": razorpay_key,
            "recipient_name": OWNER_CONFIG.name,
            "recipient_email": OWNER_CONFIG.email
        }
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate payment"
        )


@router.post("/verify")
async def verify_payment(
    payment_data: Dict,
    db: Session = Depends(get_db)
):
    """Verify payment from Razorpay webhook."""
    try:
        from app.services.payment import RazorpayPaymentGateway
        
        razorpay_key = os.getenv("RAZORPAY_KEY_ID")
        razorpay_secret = os.getenv("RAZORPAY_SECRET_KEY")
        
        gateway = RazorpayPaymentGateway(razorpay_key, razorpay_secret)
        
        # Verify payment signature
        is_valid = gateway.verify_payment(
            order_id=payment_data['razorpay_order_id'],
            payment_id=payment_data['razorpay_payment_id'],
            signature=payment_data['razorpay_signature']
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature"
            )
        
        # Update transaction status
        transaction = db.query(Transaction).filter(
            Transaction.reference_id == payment_data['razorpay_order_id']
        ).first()
        
        if transaction:
            transaction.status = "completed"
            transaction.payment_id = payment_data['razorpay_payment_id']
            db.commit()
            
            logger.info(f"Payment verified and completed: {payment_data['razorpay_payment_id']}")
        
        return {
            "status": "verified",
            "payment_id": payment_data['razorpay_payment_id'],
            "order_id": payment_data['razorpay_order_id']
        }
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment verification failed"
        )


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: str,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """Refund a payment."""
    try:
        from app.services.payment import RazorpayPaymentGateway
        
        razorpay_key = os.getenv("RAZORPAY_KEY_ID")
        razorpay_secret = os.getenv("RAZORPAY_SECRET_KEY")
        
        gateway = RazorpayPaymentGateway(razorpay_key, razorpay_secret)
        
        # Process refund
        refund = PaymentProcessor.process_refund(
            gateway=gateway,
            payment_id=payment_id,
            reason=reason
        )
        
        # Update transaction status
        transaction = db.query(Transaction).filter(
            Transaction.payment_id == payment_id
        ).first()
        
        if transaction:
            transaction.status = "refunded"
            transaction.refund_id = refund['id']
            db.commit()
        
        logger.info(f"Refund processed: {refund['id']}")
        
        return {
            "status": "refunded",
            "refund_id": refund['id'],
            "amount": refund['amount'] / 100
        }
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refund processing failed"
        )


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Get payment status."""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.reference_id == order_id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return {
            "order_id": order_id,
            "status": transaction.status,
            "amount": transaction.amount,
            "payment_id": transaction.payment_id
        }
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment status"
        )


@router.get("/bank-details")
async def get_bank_details():
    """Get recipient bank details."""
    from app.config.payment import PaymentConfig
    
    return {
        "recipient_name": OWNER_CONFIG.name,
        "recipient_email": OWNER_CONFIG.email,
        "bank_account": PaymentConfig.get_bank_account_display(OWNER_CONFIG.bank_account)
    }
