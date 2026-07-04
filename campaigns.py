from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.schemas import (
    CampaignCreate, CampaignResponse, CampaignUpdate, CampaignDetailResponse,
    MilestoneCreate, MilestoneResponse, CampaignUpdateCreate, CampaignUpdateResponse,
    CommentCreate, CommentResponse
)
from app.models.models import Campaign, Donation, Milestone, CampaignUpdate as CampaignUpdateModel, Comment
from app.utils.constants import CampaignStatus
from app.utils.helpers import GeneratorUtilities, LoggerUtilities, PaginationUtilities
from datetime import datetime

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])
logger = LoggerUtilities.setup_logger(__name__)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new campaign."""
    if campaign_data.target_amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target amount must be positive")
    
    if campaign_data.start_date >= campaign_data.end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must be after start date")
    
    new_campaign = Campaign(
        id=GeneratorUtilities.generate_uuid(),
        title=campaign_data.title,
        description=campaign_data.description,
        long_description=campaign_data.long_description,
        category=campaign_data.category,
        target_amount=campaign_data.target_amount,
        currency=campaign_data.currency,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        created_by=campaign_data.created_by if hasattr(campaign_data, 'created_by') else "",
        beneficiary_name=campaign_data.beneficiary_name,
        beneficiary_email=campaign_data.beneficiary_email,
        location=campaign_data.location,
        is_urgent=campaign_data.is_urgent,
        tags=campaign_data.tags or []
    )
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    logger.log_audit(campaign_data.created_by if hasattr(campaign_data, 'created_by') else "system", "campaign_created", {"campaign_id": new_campaign.id})
    return new_campaign


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Get campaign by ID."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    campaign.view_count += 1
    db.commit()
    
    # Calculate progress
    progress = (campaign.raised_amount / campaign.target_amount * 100) if campaign.target_amount > 0 else 0
    
    campaign_data = CampaignDetailResponse.from_orm(campaign)
    campaign_data.progress_percentage = progress
    return campaign_data


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 10,
    status_filter: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all campaigns."""
    query = db.query(Campaign)
    
    if status_filter:
        query = query.filter(Campaign.status == status_filter)
    
    if category:
        query = query.filter(Campaign.category == category)
    
    campaigns = query.offset(skip).limit(limit).all()
    return campaigns


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: str, campaign_data: CampaignUpdate, db: Session = Depends(get_db)):
    """Update campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    
    logger.log_audit("system", "campaign_updated", {"campaign_id": campaign_id})
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Delete campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    db.delete(campaign)
    db.commit()
    
    logger.log_audit("system", "campaign_deleted", {"campaign_id": campaign_id})


@router.post("/{campaign_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(campaign_id: str, milestone_data: MilestoneCreate, db: Session = Depends(get_db)):
    """Create campaign milestone."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    new_milestone = Milestone(
        id=GeneratorUtilities.generate_uuid(),
        campaign_id=campaign_id,
        title=milestone_data.title,
        description=milestone_data.description,
        target_amount=milestone_data.target_amount,
        target_date=milestone_data.target_date
    )
    
    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)
    
    return new_milestone


@router.get("/{campaign_id}/milestones", response_model=list[MilestoneResponse])
def get_milestones(campaign_id: str, db: Session = Depends(get_db)):
    """Get campaign milestones."""
    milestones = db.query(Milestone).filter(Milestone.campaign_id == campaign_id).all()
    return milestones


@router.post("/{campaign_id}/updates", response_model=CampaignUpdateResponse, status_code=status.HTTP_201_CREATED)
def create_campaign_update(campaign_id: str, update_data: CampaignUpdateCreate, db: Session = Depends(get_db)):
    """Create campaign update."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    new_update = CampaignUpdateModel(
        id=GeneratorUtilities.generate_uuid(),
        campaign_id=campaign_id,
        title=update_data.title,
        content=update_data.content,
        image_url=update_data.image_url
    )
    
    db.add(new_update)
    db.commit()
    db.refresh(new_update)
    
    return new_update


@router.get("/{campaign_id}/updates", response_model=list[CampaignUpdateResponse])
def get_campaign_updates(campaign_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get campaign updates."""
    updates = db.query(CampaignUpdateModel).filter(
        CampaignUpdateModel.campaign_id == campaign_id
    ).order_by(CampaignUpdateModel.created_at.desc()).offset(skip).limit(limit).all()
    return updates


@router.post("/{campaign_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(campaign_id: str, comment_data: CommentCreate, db: Session = Depends(get_db)):
    """Create comment on campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    new_comment = Comment(
        id=GeneratorUtilities.generate_uuid(),
        campaign_id=campaign_id,
        user_id=comment_data.user_id if hasattr(comment_data, 'user_id') else "",
        content=comment_data.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment


@router.get("/{campaign_id}/comments", response_model=list[CommentResponse])
def get_campaign_comments(campaign_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get campaign comments."""
    comments = db.query(Comment).filter(
        Comment.campaign_id == campaign_id,
        Comment.is_approved == True
    ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    return comments


@router.get("/{campaign_id}/donations", response_model=list)
def get_campaign_donations(campaign_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get campaign donations."""
    donations = db.query(Donation).filter(
        Donation.campaign_id == campaign_id
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()
    return donations


@router.get("/{campaign_id}/analytics")
def get_campaign_analytics(campaign_id: str, db: Session = Depends(get_db)):
    """Get campaign analytics."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    donations = db.query(Donation).filter(Donation.campaign_id == campaign_id).all()
    
    analytics = {
        "campaign_id": campaign_id,
        "title": campaign.title,
        "target_amount": campaign.target_amount,
        "raised_amount": campaign.raised_amount,
        "progress_percentage": (campaign.raised_amount / campaign.target_amount * 100) if campaign.target_amount > 0 else 0,
        "total_donations": len(donations),
        "average_donation": sum(d.amount for d in donations) / len(donations) if donations else 0,
        "largest_donation": max((d.amount for d in donations), default=0),
        "view_count": campaign.view_count,
        "share_count": campaign.share_count
    }
    
    return analytics


@router.post("/{campaign_id}/share")
def share_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Share campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    campaign.share_count += 1
    db.commit()
    
    return {"message": "Campaign shared successfully", "share_count": campaign.share_count}


@router.get("/{campaign_id}/featured")
def set_campaign_featured(campaign_id: str, is_featured: bool, db: Session = Depends(get_db)):
    """Set campaign as featured."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    campaign.is_featured = is_featured
    db.commit()
    
    return {"message": f"Campaign marked as {'featured' if is_featured else 'not featured'}"}


@router.get("/search")
def search_campaigns(query: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Search campaigns."""
    campaigns = db.query(Campaign).filter(
        (Campaign.title.ilike(f"%{query}%")) |
        (Campaign.description.ilike(f"%{query}%")) |
        (Campaign.category.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()
    
    return campaigns


@router.post("/{campaign_id}/close")
def close_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Close campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    campaign.status = CampaignStatus.COMPLETED
    db.commit()
    
    logger.log_audit("system", "campaign_closed", {"campaign_id": campaign_id})
    return {"message": "Campaign closed successfully"}
