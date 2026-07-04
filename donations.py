from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.schemas import (
    DonationCreate, DonationResponse, DonationUpdate, DonationDetailResponse
)
from app.models.models import Donation, Campaign, Donor, User, Transaction
from app.utils.constants import DonationStatus, TransactionType
from app.utils.helpers import GeneratorUtilities, LoggerUtilities, FormatterUtilities
from datetime import datetime

router = APIRouter(prefix="/api/v1/donations", tags=["donations"])
logger = LoggerUtilities.setup_logger(__name__)


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(donation_data: DonationCreate, db: Session = Depends(get_db)):
    """Create a new donation."""
    if donation_data.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    
    # Verify donor and campaign exist
    donor = db.query(Donor).filter(Donor.id == donation_data.donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    campaign = db.query(Campaign).filter(Campaign.id == donation_data.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    # Create donation
    receipt_number = GeneratorUtilities.generate_donation_receipt(donation_data.donor_id)
    new_donation = Donation(
        id=GeneratorUtilities.generate_uuid(),
        donor_id=donation_data.donor_id,
        campaign_id=donation_data.campaign_id,
        user_id=donor.user_id,
        amount=donation_data.amount,
        currency=donation_data.currency,
        payment_method=donation_data.payment_method,
        receipt_number=receipt_number,
        is_anonymous=donation_data.is_anonymous,
        donor_comment=donation_data.donor_comment,
        status=DonationStatus.PENDING
    )
    
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    
    # Create transaction
    transaction = Transaction(
        id=GeneratorUtilities.generate_uuid(),
        donation_id=new_donation.id,
        type=TransactionType.DONATION,
        amount=donation_data.amount,
        currency=donation_data.currency,
        status="pending",
        description=f"Donation to {campaign.title}"
    )
    
    db.add(transaction)
    db.commit()
    
    # Update donor stats
    donor.donation_count += 1
    db.commit()
    
    logger.log_audit(donor.user_id, "donation_created", {
        "donation_id": new_donation.id,
        "amount": donation_data.amount,
        "campaign_id": donation_data.campaign_id
    })
    
    return new_donation


@router.get("/{donation_id}", response_model=DonationDetailResponse)
def get_donation(donation_id: str, db: Session = Depends(get_db)):
    """Get donation by ID."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    return donation


@router.get("", response_model=list[DonationResponse])
def list_donations(
    skip: int = 0,
    limit: int = 10,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """List all donations."""
    query = db.query(Donation)
    
    if status_filter:
        query = query.filter(Donation.status == status_filter)
    
    donations = query.order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    return donations


@router.put("/{donation_id}", response_model=DonationResponse)
def update_donation(donation_id: str, donation_data: DonationUpdate, db: Session = Depends(get_db)):
    """Update donation."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    update_data = donation_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donation, field, value)
    
    donation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(donation)
    
    logger.log_audit("system", "donation_updated", {"donation_id": donation_id})
    return donation


@router.post("/{donation_id}/confirm")
def confirm_donation(donation_id: str, db: Session = Depends(get_db)):
    """Confirm donation."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    donation.status = DonationStatus.CONFIRMED
    donation.completed_at = datetime.utcnow()
    
    # Update campaign
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    if campaign:
        campaign.raised_amount += donation.amount
        campaign.donation_count += 1
    
    # Update donor
    donor = db.query(Donor).filter(Donor.id == donation.donor_id).first()
    if donor:
        donor.total_donated += donation.amount
        donor.last_donation_date = datetime.utcnow()
    
    db.commit()
    
    logger.log_audit("system", "donation_confirmed", {"donation_id": donation_id})
    return {"message": "Donation confirmed successfully"}


@router.post("/{donation_id}/refund")
def refund_donation(donation_id: str, reason: str = None, db: Session = Depends(get_db)):
    """Refund donation."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    # Create refund transaction
    refund_transaction = Transaction(
        id=GeneratorUtilities.generate_uuid(),
        donation_id=donation_id,
        type=TransactionType.REFUND,
        amount=donation.amount,
        currency=donation.currency,
        status="completed",
        description=f"Refund for donation {donation_id}: {reason}"
    )
    
    db.add(refund_transaction)
    
    # Update donation
    donation.status = DonationStatus.REFUNDED
    donation.refund_amount = donation.amount
    donation.refund_reason = reason
    
    # Update campaign
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    if campaign:
        campaign.raised_amount -= donation.amount
        campaign.donation_count -= 1
    
    db.commit()
    
    logger.log_audit("system", "donation_refunded", {"donation_id": donation_id, "reason": reason})
    return {"message": "Donation refunded successfully"}


@router.get("/{donation_id}/receipt")
def get_donation_receipt(donation_id: str, db: Session = Depends(get_db)):
    """Get donation receipt."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    donor = db.query(Donor).filter(Donor.id == donation.donor_id).first()
    campaign = db.query(Campaign).filter(Campaign.id == donation.campaign_id).first()
    
    receipt = {
        "receipt_number": donation.receipt_number,
        "donation_id": donation_id,
        "donor_name": donor.user_id if donor else "Anonymous",
        "campaign_name": campaign.title if campaign else "Unknown",
        "amount": FormatterUtilities.format_currency(donation.amount, donation.currency),
        "payment_method": donation.payment_method,
        "donation_date": donation.created_at.strftime("%Y-%m-%d"),
        "status": donation.status,
        "tax_deductible": True
    }
    
    return receipt


@router.get("/campaign/{campaign_id}/donations")
def get_campaign_donations(campaign_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all donations for a campaign."""
    donations = db.query(Donation).filter(
        Donation.campaign_id == campaign_id
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    
    return donations


@router.get("/donor/{donor_id}/donations")
def get_donor_donations(donor_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all donations by a donor."""
    donations = db.query(Donation).filter(
        Donation.donor_id == donor_id
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    
    return donations


@router.post("/{donation_id}/send-receipt")
def send_receipt_email(donation_id: str, db: Session = Depends(get_db)):
    """Send receipt email for donation."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    donation.receipt_email_sent = True
    db.commit()
    
    logger.log_audit("system", "receipt_email_sent", {"donation_id": donation_id})
    return {"message": "Receipt email sent successfully"}


@router.post("/{donation_id}/send-thank-you")
def send_thank_you_email(donation_id: str, db: Session = Depends(get_db)):
    """Send thank you email for donation."""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    
    donation.thank_you_email_sent = True
    db.commit()
    
    logger.log_audit("system", "thank_you_email_sent", {"donation_id": donation_id})
    return {"message": "Thank you email sent successfully"}


@router.get("/analytics/summary")
def get_donations_summary(db: Session = Depends(get_db)):
    """Get donations summary."""
    donations = db.query(Donation).all()
    
    total_donations = len(donations)
    total_amount = sum(d.amount for d in donations)
    average_donation = total_amount / total_donations if total_donations > 0 else 0
    largest_donation = max((d.amount for d in donations), default=0)
    
    # Get by status
    by_status = {}
    for donation in donations:
        status = donation.status.value
        by_status[status] = by_status.get(status, 0) + 1
    
    return {
        "total_donations": total_donations,
        "total_amount": total_amount,
        "average_donation": average_donation,
        "largest_donation": largest_donation,
        "by_status": by_status
    }
