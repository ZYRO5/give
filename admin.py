"""Admin utilities and dashboard services."""

from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    User, Donor, Campaign, Donation, Transaction,
    Notification, Activity
)
from app.utils.helpers import LoggerUtilities

logger = LoggerUtilities.setup_logger(__name__)


class AdminDashboardService:
    """Service for admin dashboard metrics."""

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict:
        """Get dashboard summary metrics."""
        today = datetime.utcnow()
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)

        # Total metrics
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_donors = db.query(func.count(Donor.id)).scalar() or 0
        total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
        total_donations = db.query(func.sum(Donation.amount)).filter(
            Donation.status == "confirmed"
        ).scalar() or 0

        # This month metrics
        month_donations = db.query(func.sum(Donation.amount)).filter(
            Donation.created_at >= month_ago,
            Donation.status == "confirmed"
        ).scalar() or 0

        month_donors = db.query(func.count(Donor.id)).filter(
            Donor.created_at >= month_ago
        ).scalar() or 0

        # This year metrics
        year_donations = db.query(func.sum(Donation.amount)).filter(
            Donation.created_at >= year_ago,
            Donation.status == "confirmed"
        ).scalar() or 0

        return {
            "total_users": total_users,
            "total_donors": total_donors,
            "total_campaigns": total_campaigns,
            "total_donations": total_donations,
            "month_donations": month_donations,
            "month_new_donors": month_donors,
            "year_donations": year_donations,
            "generated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_recent_activity(db: Session, limit: int = 20) -> List[Dict]:
        """Get recent platform activity."""
        activities = db.query(Activity).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()

        return [
            {
                "id": a.id,
                "user_id": a.user_id,
                "action": a.action,
                "resource_type": a.resource_type,
                "timestamp": a.created_at.isoformat()
            }
            for a in activities
        ]

    @staticmethod
    def get_pending_approvals(db: Session) -> Dict:
        """Get pending items requiring approval."""
        pending_comments = db.query(Comment).filter(
            Comment.is_approved == False
        ).count()

        pending_campaigns = db.query(Campaign).filter(
            Campaign.status == "pending"
        ).count()

        return {
            "pending_comments": pending_comments,
            "pending_campaigns": pending_campaigns,
            "total_pending": pending_comments + pending_campaigns
        }


class AdminUserService:
    """Service for admin user management."""

    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role_filter: str = None
    ) -> List[Dict]:
        """Get all users with optional role filter."""
        query = db.query(User)

        if role_filter:
            query = query.filter(User.role == role_filter)

        users = query.offset(skip).limit(limit).all()

        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ]

    @staticmethod
    def suspend_user(db: Session, user_id: str, reason: str = None) -> bool:
        """Suspend a user account."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            logger.warning(f"User suspended: {user_id}, reason: {reason}")
            return True
        return False

    @staticmethod
    def activate_user(db: Session, user_id: str) -> bool:
        """Activate a suspended user account."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = True
            db.commit()
            logger.info(f"User activated: {user_id}")
            return True
        return False

    @staticmethod
    def update_user_role(db: Session, user_id: str, new_role: str) -> bool:
        """Update user role."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            db.commit()
            logger.info(f"User role updated: {user_id} -> {new_role}")
            return True
        return False


class AdminCampaignService:
    """Service for admin campaign management."""

    @staticmethod
    def approve_campaign(db: Session, campaign_id: str) -> bool:
        """Approve a campaign."""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = "active"
            db.commit()
            logger.info(f"Campaign approved: {campaign_id}")
            return True
        return False

    @staticmethod
    def reject_campaign(db: Session, campaign_id: str, reason: str = None) -> bool:
        """Reject a campaign."""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = "rejected"
            db.commit()
            logger.warning(f"Campaign rejected: {campaign_id}, reason: {reason}")
            return True
        return False

    @staticmethod
    def close_campaign(db: Session, campaign_id: str) -> bool:
        """Close a campaign."""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = "closed"
            db.commit()
            logger.info(f"Campaign closed: {campaign_id}")
            return True
        return False


class AdminReportService:
    """Service for generating admin reports."""

    @staticmethod
    def generate_financial_report(db: Session, start_date: datetime, end_date: datetime) -> Dict:
        """Generate financial report for date range."""
        donations = db.query(
            func.sum(Donation.amount).label('total'),
            func.count(Donation.id).label('count'),
            func.avg(Donation.amount).label('average')
        ).filter(
            Donation.created_at >= start_date,
            Donation.created_at <= end_date,
            Donation.status == "confirmed"
        ).first()

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_raised": donations.total or 0,
            "total_donations": donations.count or 0,
            "average_donation": donations.average or 0
        }

    @staticmethod
    def generate_user_report(db: Session) -> Dict:
        """Generate user statistics report."""
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar() or 0
        admin_users = db.query(func.count(User.id)).filter(
            User.role == "admin"
        ).scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users
        }
