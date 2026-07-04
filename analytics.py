"""Analytics and reporting service."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Donation, Campaign, Donor, User
from app.utils.helpers import LoggerUtilities

logger = LoggerUtilities.setup_logger(__name__)


class AnalyticsService:
    """Service for analytics calculations."""

    @staticmethod
    def get_total_donations(db: Session) -> float:
        """Get total donation amount."""
        result = db.query(func.sum(Donation.amount)).filter(
            Donation.status == "completed"
        ).scalar()
        return result or 0

    @staticmethod
    def get_total_donors(db: Session) -> int:
        """Get total number of donors."""
        return db.query(func.count(Donor.id)).scalar() or 0

    @staticmethod
    def get_total_campaigns(db: Session) -> int:
        """Get total number of campaigns."""
        return db.query(func.count(Campaign.id)).scalar() or 0

    @staticmethod
    def get_average_donation(db: Session) -> float:
        """Get average donation amount."""
        result = db.query(func.avg(Donation.amount)).filter(
            Donation.status == "completed"
        ).scalar()
        return result or 0

    @staticmethod
    def get_largest_donation(db: Session) -> float:
        """Get largest donation amount."""
        result = db.query(func.max(Donation.amount)).filter(
            Donation.status == "completed"
        ).scalar()
        return result or 0

    @staticmethod
    def get_donations_by_month(db: Session, months: int = 12) -> List[Dict]:
        """Get donations grouped by month."""
        donations = db.query(
            func.to_char(Donation.created_at, 'YYYY-MM').label('month'),
            func.count(Donation.id).label('count'),
            func.sum(Donation.amount).label('total')
        ).filter(
            Donation.status == "completed"
        ).group_by('month').all()

        return [
            {"month": d.month, "count": d.count, "total": d.total or 0}
            for d in donations
        ]

    @staticmethod
    def get_top_donors(db: Session, limit: int = 10) -> List[Dict]:
        """Get top donors by total amount."""
        donors = db.query(Donor).order_by(Donor.total_donated.desc()).limit(limit).all()
        
        result = []
        for donor in donors:
            user = db.query(User).filter(User.id == donor.user_id).first()
            result.append({
                "donor_id": donor.id,
                "name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "total_donated": donor.total_donated,
                "donation_count": donor.donation_count
            })
        
        return result

    @staticmethod
    def get_top_campaigns(db: Session, limit: int = 10) -> List[Dict]:
        """Get top campaigns by total raised."""
        campaigns = db.query(Campaign).order_by(Campaign.raised_amount.desc()).limit(limit).all()
        
        return [
            {
                "campaign_id": c.id,
                "title": c.title,
                "target_amount": c.target_amount,
                "raised_amount": c.raised_amount,
                "progress": (c.raised_amount / c.target_amount * 100) if c.target_amount > 0 else 0
            }
            for c in campaigns
        ]

    @staticmethod
    def get_campaigns_by_category(db: Session) -> Dict[str, Dict]:
        """Get campaigns statistics by category."""
        campaigns = db.query(Campaign).all()
        
        by_category = {}
        for campaign in campaigns:
            if campaign.category not in by_category:
                by_category[campaign.category] = {
                    "count": 0,
                    "target_total": 0,
                    "raised_total": 0
                }
            
            by_category[campaign.category]["count"] += 1
            by_category[campaign.category]["target_total"] += campaign.target_amount
            by_category[campaign.category]["raised_total"] += campaign.raised_amount
        
        return by_category

    @staticmethod
    def get_donor_retention_rate(db: Session, months: int = 12) -> float:
        """Calculate donor retention rate."""
        cutoff_date = datetime.utcnow() - timedelta(days=30*months)
        
        total_donors = db.query(func.count(Donor.id)).filter(
            Donor.created_at >= cutoff_date
        ).scalar() or 1
        
        repeat_donors = db.query(func.count(Donor.id)).filter(
            Donor.created_at >= cutoff_date,
            Donor.donation_count > 1
        ).scalar() or 0
        
        return (repeat_donors / total_donors) * 100 if total_donors > 0 else 0

    @staticmethod
    def get_growth_metrics(db: Session, period_days: int = 30) -> Dict:
        """Get growth metrics for period."""
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        new_donors = db.query(func.count(Donor.id)).filter(
            Donor.created_at >= cutoff_date
        ).scalar() or 0
        
        new_campaigns = db.query(func.count(Campaign.id)).filter(
            Campaign.created_at >= cutoff_date
        ).scalar() or 0
        
        new_donations = db.query(func.sum(Donation.amount)).filter(
            Donation.created_at >= cutoff_date,
            Donation.status == "completed"
        ).scalar() or 0
        
        return {
            "new_donors": new_donors,
            "new_campaigns": new_campaigns,
            "new_donations_amount": new_donations,
            "period_days": period_days
        }

    @staticmethod
    def get_engagement_score(db: Session, donor_id: str) -> float:
        """Calculate engagement score for donor."""
        donor = db.query(Donor).filter(Donor.id == donor_id).first()
        if not donor:
            return 0
        
        # Score based on donation count, frequency, and recency
        donations = db.query(Donation).filter(Donation.donor_id == donor_id).all()
        
        if not donations:
            return 0
        
        # Recency score (0-30 points)
        last_donation = max((d.created_at for d in donations), default=None)
        if last_donation:
            days_since = (datetime.utcnow() - last_donation).days
            recency_score = max(0, 30 - (days_since / 10))
        else:
            recency_score = 0
        
        # Frequency score (0-40 points)
        frequency_score = min(40, donor.donation_count * 4)
        
        # Amount score (0-30 points)
        average_donation = donor.total_donated / donor.donation_count if donor.donation_count > 0 else 0
        amount_score = min(30, (average_donation / 100))
        
        total_score = recency_score + frequency_score + amount_score
        return round(total_score, 2)


class ReportGenerationService:
    """Service for generating comprehensive reports."""

    @staticmethod
    def generate_executive_summary(db: Session) -> Dict:
        """Generate executive summary report."""
        analytics = AnalyticsService()
        
        return {
            "total_raised": analytics.get_total_donations(db),
            "total_donors": analytics.get_total_donors(db),
            "total_campaigns": analytics.get_total_campaigns(db),
            "average_donation": analytics.get_average_donation(db),
            "largest_donation": analytics.get_largest_donation(db),
            "growth_metrics": analytics.get_growth_metrics(db),
            "generated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def generate_donor_report(db: Session) -> Dict:
        """Generate detailed donor report."""
        donors = db.query(Donor).all()
        
        return {
            "total_donors": len(donors),
            "top_donors": AnalyticsService.get_top_donors(db),
            "retention_rate": AnalyticsService.get_donor_retention_rate(db),
            "by_donor_type": [
                {
                    "type": d.donor_type,
                    "count": len([x for x in donors if x.donor_type == d.donor_type]),
                    "total_donated": sum(x.total_donated for x in donors if x.donor_type == d.donor_type)
                }
                for d in set(donors)
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def generate_campaign_report(db: Session) -> Dict:
        """Generate detailed campaign report."""
        return {
            "total_campaigns": AnalyticsService.get_total_campaigns(db),
            "top_campaigns": AnalyticsService.get_top_campaigns(db),
            "by_category": AnalyticsService.get_campaigns_by_category(db),
            "generated_at": datetime.utcnow().isoformat()
        }
