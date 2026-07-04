from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Table, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base
from app.utils.constants import (
    DonorStatus, DonationStatus, CampaignStatus, PaymentMethod, 
    UserRole, TransactionType
)


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DONOR, nullable=False)
    organization = Column(String(100), nullable=True)
    profile_image = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    status = Column(Enum(DonorStatus), default=DonorStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    preferences = Column(JSON, default={}, nullable=False)

    donors = relationship("Donor", back_populates="user", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="created_by_user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")


class Donor(Base):
    """Donor model."""
    __tablename__ = "donors"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_name = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    donor_type = Column(String(50), default="individual", nullable=False)
    tax_id = Column(String(50), nullable=True)
    total_donated = Column(Float, default=0, nullable=False)
    donation_count = Column(Integer, default=0, nullable=False)
    last_donation_date = Column(DateTime, nullable=True)
    status = Column(Enum(DonorStatus), default=DonorStatus.ACTIVE, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    communication_preferences = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="donors")
    donations = relationship("Donation", back_populates="donor", cascade="all, delete-orphan")
    donation_history = relationship("DonationHistory", back_populates="donor", cascade="all, delete-orphan")


class Campaign(Base):
    """Campaign model."""
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    raised_amount = Column(Float, default=0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    image_url = Column(String(255), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    beneficiary_name = Column(String(255), nullable=True)
    beneficiary_email = Column(String(100), nullable=True)
    beneficiary_phone = Column(String(20), nullable=True)
    impact_description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    donation_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    tags = Column(JSON, default=[], nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_urgent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    created_by_user = relationship("User", back_populates="campaigns")
    donations = relationship("Donation", back_populates="campaign", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="campaign", cascade="all, delete-orphan")
    updates = relationship("CampaignUpdate", back_populates="campaign", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="campaign", cascade="all, delete-orphan")


class Donation(Base):
    """Donation model."""
    __tablename__ = "donations"

    id = Column(String(36), primary_key=True, index=True)
    donor_id = Column(String(36), ForeignKey("donors.id"), nullable=False, index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=True)
    status = Column(Enum(DonationStatus), default=DonationStatus.PENDING, nullable=False)
    payment_processor = Column(String(50), nullable=True)
    receipt_number = Column(String(100), unique=True, nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    thank_you_email_sent = Column(Boolean, default=False, nullable=False)
    receipt_email_sent = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)
    refund_reason = Column(String(255), nullable=True)
    donor_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    donor = relationship("Donor", back_populates="donations")
    campaign = relationship("Campaign", back_populates="donations")
    user = relationship("User", back_populates="donations")
    transactions = relationship("Transaction", back_populates="donation", cascade="all, delete-orphan")


class Milestone(Base):
    """Campaign milestone model."""
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Float, nullable=False)
    achieved_amount = Column(Float, default=0, nullable=False)
    target_date = Column(DateTime, nullable=True)
    is_achieved = Column(Boolean, default=False, nullable=False)
    achieved_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign", back_populates="milestones")


class CampaignUpdate(Base):
    """Campaign update model."""
    __tablename__ = "campaign_updates"

    id = Column(String(36), primary_key=True, index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign", back_populates="updates")


class Comment(Base):
    """Comment model."""
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign", back_populates="comments")


class Transaction(Base):
    """Transaction model."""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, index=True)
    donation_id = Column(String(36), ForeignKey("donations.id"), nullable=False, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(50), nullable=False)
    payment_gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    donation = relationship("Donation", back_populates="transactions")


class Notification(Base):
    """Notification model."""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    related_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")


class Activity(Base):
    """Activity log model."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, default={}, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="activities")


class Report(Base):
    """Report model."""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_donors = Column(Integer, default=0, nullable=False)
    total_campaigns = Column(Integer, default=0, nullable=False)
    total_donations = Column(Float, default=0, nullable=False)
    total_raised = Column(Float, default=0, nullable=False)
    average_donation = Column(Float, default=0, nullable=False)
    largest_donation = Column(Float, default=0, nullable=False)
    data = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_at = Column(DateTime, nullable=True)


class DonationHistory(Base):
    """Donation history model."""
    __tablename__ = "donation_histories"

    id = Column(String(36), primary_key=True, index=True)
    donor_id = Column(String(36), ForeignKey("donors.id"), nullable=False, index=True)
    total_amount = Column(Float, default=0, nullable=False)
    donation_count = Column(Integer, default=0, nullable=False)
    last_donation_date = Column(DateTime, nullable=True)
    average_donation = Column(Float, default=0, nullable=False)
    largest_donation = Column(Float, default=0, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    donor = relationship("Donor", back_populates="donation_history")
