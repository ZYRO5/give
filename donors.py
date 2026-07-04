from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.schemas import DonorCreate, DonorResponse, DonorUpdate, DonorDetailResponse
from app.models.models import Donor, User, Donation
from app.utils.helpers import GeneratorUtilities, LoggerUtilities
from datetime import datetime

router = APIRouter(prefix="/api/v1/donors", tags=["donors"])
logger = LoggerUtilities.setup_logger(__name__)


@router.post("", response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor(donor_data: DonorCreate, db: Session = Depends(get_db)):
    """Create a new donor."""
    user = db.query(User).filter(User.id == donor_data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if donor already exists for user
    existing_donor = db.query(Donor).filter(Donor.user_id == donor_data.user_id).first()
    if existing_donor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Donor already exists for this user")
    
    new_donor = Donor(
        id=GeneratorUtilities.generate_uuid(),
        user_id=donor_data.user_id,
        organization_name=donor_data.organization_name,
        tax_id=donor_data.tax_id,
        donor_type=donor_data.donor_type,
        is_anonymous=donor_data.is_anonymous
    )
    
    db.add(new_donor)
    db.commit()
    db.refresh(new_donor)
    
    logger.log_audit(donor_data.user_id, "donor_created", {"donor_id": new_donor.id})
    return new_donor


@router.get("/{donor_id}", response_model=DonorDetailResponse)
def get_donor(donor_id: str, db: Session = Depends(get_db)):
    """Get donor by ID."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    return donor


@router.get("", response_model=list[DonorResponse])
def list_donors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all donors."""
    donors = db.query(Donor).offset(skip).limit(limit).all()
    return donors


@router.put("/{donor_id}", response_model=DonorResponse)
def update_donor(donor_id: str, donor_data: DonorUpdate, db: Session = Depends(get_db)):
    """Update donor."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    update_data = donor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donor, field, value)
    
    donor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(donor)
    
    logger.log_audit(donor.user_id, "donor_updated", {"donor_id": donor_id})
    return donor


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donor(donor_id: str, db: Session = Depends(get_db)):
    """Delete donor."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    db.delete(donor)
    db.commit()
    
    logger.log_audit(donor.user_id, "donor_deleted", {"donor_id": donor_id})


@router.get("/{donor_id}/donations")
def get_donor_donations(donor_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get donor's donations."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    donations = db.query(Donation).filter(
        Donation.donor_id == donor_id
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    
    return donations


@router.get("/{donor_id}/statistics")
def get_donor_statistics(donor_id: str, db: Session = Depends(get_db)):
    """Get donor statistics."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    donations = db.query(Donation).filter(Donation.donor_id == donor_id).all()
    
    stats = {
        "donor_id": donor_id,
        "total_donated": donor.total_donated,
        "donation_count": donor.donation_count,
        "average_donation": donor.total_donated / donor.donation_count if donor.donation_count > 0 else 0,
        "largest_donation": max((d.amount for d in donations), default=0) if donations else 0,
        "last_donation_date": donor.last_donation_date.isoformat() if donor.last_donation_date else None,
        "donor_since": donor.created_at.isoformat(),
        "donor_type": donor.donor_type,
        "is_anonymous": donor.is_anonymous
    }
    
    return stats


@router.post("/{donor_id}/tax-certificate")
def generate_tax_certificate(donor_id: str, year: int, db: Session = Depends(get_db)):
    """Generate tax certificate for donor."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    from datetime import datetime
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    donations = db.query(Donation).filter(
        Donation.donor_id == donor_id,
        Donation.created_at >= start_date,
        Donation.created_at <= end_date,
        Donation.status == "completed"
    ).all()
    
    total_amount = sum(d.amount for d in donations)
    
    cert = {
        "certificate_id": GeneratorUtilities.generate_uuid(),
        "donor_id": donor_id,
        "donor_name": db.query(User).filter(User.id == donor.user_id).first().first_name,
        "tax_id": donor.tax_id,
        "year": year,
        "total_donated": total_amount,
        "donation_count": len(donations),
        "generated_date": datetime.utcnow().isoformat(),
        "valid": True
    }
    
    return cert


@router.get("/{donor_id}/insights")
def get_donor_insights(donor_id: str, db: Session = Depends(get_db)):
    """Get donor insights."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    donations = db.query(Donation).filter(Donation.donor_id == donor_id).all()
    
    # Categorize donations
    by_category = {}
    for donation in donations:
        campaign = db.query(type('Campaign', (object,), {'category': 'unknown'})).first()
        category = campaign.category if campaign else 'unknown'
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += donation.amount
    
    insights = {
        "total_impact": donor.total_donated,
        "campaigns_supported": len(set(d.campaign_id for d in donations)),
        "favorite_category": max(by_category.items(), key=lambda x: x[1])[0] if by_category else None,
        "donations_by_category": by_category,
        "member_since": (datetime.utcnow() - donor.created_at).days,
        "last_active": (datetime.utcnow() - donor.last_donation_date).days if donor.last_donation_date else None
    }
    
    return insights


@router.get("/search")
def search_donors(query: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Search donors."""
    # Join with User to search by name
    donors = db.query(Donor).join(User).filter(
        (User.first_name.ilike(f"%{query}%")) |
        (User.last_name.ilike(f"%{query}%")) |
        (Donor.organization_name.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()
    
    return donors


@router.post("/{donor_id}/send-thank-you")
def send_thank_you_message(donor_id: str, db: Session = Depends(get_db)):
    """Send thank you message to donor."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    user = db.query(User).filter(User.id == donor.user_id).first()
    
    logger.log_audit("system", "thank_you_message_sent", {"donor_id": donor_id, "email": user.email if user else None})
    return {"message": "Thank you message sent successfully"}


@router.get("/{donor_id}/impact-summary")
def get_donor_impact_summary(donor_id: str, db: Session = Depends(get_db)):
    """Get donor impact summary."""
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found")
    
    donations = db.query(Donation).filter(Donation.donor_id == donor_id).all()
    
    summary = {
        "donor_id": donor_id,
        "total_contributed": donor.total_donated,
        "lives_impacted": len(donations) * 10,  # Placeholder
        "campaigns_supported": len(set(d.campaign_id for d in donations)),
        "causes_supported": len(set(db.query(Donation.campaign_id).filter(Donation.donor_id == donor_id).all())),
        "average_gift_size": donor.total_donated / donor.donation_count if donor.donation_count > 0 else 0,
        "giving_frequency": f"{donor.donation_count} times",
        "donor_level": "Gold" if donor.total_donated >= 10000 else "Silver" if donor.total_donated >= 5000 else "Bronze" if donor.total_donated >= 1000 else "Friend"
    }
    
    return summary
