from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from app.utils.constants import (
    DonorStatus, DonationStatus, CampaignStatus, PaymentMethod, 
    UserRole, NotificationType
)


# ========== User Schemas ==========
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    role: UserRole = UserRole.DONOR


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    status: DonorStatus
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    bio: Optional[str]
    profile_image: Optional[str]
    preferences: dict


# ========== Donor Schemas ==========
class DonorBase(BaseModel):
    donor_type: str = "individual"
    is_anonymous: bool = False


class DonorCreate(DonorBase):
    user_id: str
    organization_name: Optional[str] = None
    tax_id: Optional[str] = None


class DonorUpdate(BaseModel):
    organization_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_anonymous: Optional[bool] = None
    communication_preferences: Optional[dict] = None


class DonorResponse(DonorBase):
    id: str
    user_id: str
    total_donated: float
    donation_count: int
    status: DonorStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DonorDetailResponse(DonorResponse):
    organization_name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    tax_id: Optional[str]
    last_donation_date: Optional[datetime]


# ========== Campaign Schemas ==========
class CampaignBase(BaseModel):
    title: str
    description: str
    category: str
    target_amount: float
    currency: str = "USD"


class CampaignCreate(CampaignBase):
    long_description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    beneficiary_name: Optional[str] = None
    beneficiary_email: Optional[str] = None
    location: Optional[str] = None
    is_urgent: bool = False
    tags: Optional[List[str]] = []


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_amount: Optional[float] = None
    status: Optional[CampaignStatus] = None
    end_date: Optional[datetime] = None
    beneficiary_name: Optional[str] = None
    is_urgent: Optional[bool] = None


class CampaignResponse(CampaignBase):
    id: str
    status: CampaignStatus
    raised_amount: float
    donation_count: int
    view_count: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    long_description: Optional[str]
    beneficiary_name: Optional[str]
    beneficiary_email: Optional[str]
    location: Optional[str]
    is_featured: bool
    is_urgent: bool
    tags: List[str]
    share_count: int
    progress_percentage: float = Field(default=0)


# ========== Donation Schemas ==========
class DonationBase(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method: PaymentMethod
    is_anonymous: bool = False


class DonationCreate(DonationBase):
    donor_id: str
    campaign_id: str
    donor_comment: Optional[str] = None


class DonationUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[DonationStatus] = None


class DonationResponse(DonationBase):
    id: str
    donor_id: str
    campaign_id: str
    status: DonationStatus
    receipt_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DonationDetailResponse(DonationResponse):
    transaction_id: Optional[str]
    thank_you_email_sent: bool
    receipt_email_sent: bool
    completed_at: Optional[datetime]


# ========== Milestone Schemas ==========
class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_amount: float
    target_date: Optional[datetime] = None


class MilestoneCreate(MilestoneBase):
    campaign_id: str


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    is_achieved: Optional[bool] = None


class MilestoneResponse(MilestoneBase):
    id: str
    campaign_id: str
    achieved_amount: float
    is_achieved: bool
    achieved_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Campaign Update Schemas ==========
class CampaignUpdateBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None


class CampaignUpdateCreate(CampaignUpdateBase):
    campaign_id: str


class CampaignUpdateResponse(CampaignUpdateBase):
    id: str
    campaign_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Comment Schemas ==========
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    campaign_id: str


class CommentResponse(CommentBase):
    id: str
    campaign_id: str
    user_id: str
    likes: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Notification Schemas ==========
class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType


class NotificationCreate(NotificationBase):
    user_id: str
    related_id: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Report Schemas ==========
class ReportResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    report_type: str
    start_date: datetime
    end_date: datetime
    total_donors: int
    total_campaigns: int
    total_donations: float
    total_raised: float
    average_donation: float
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Auth Schemas ==========
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# ========== Pagination Schemas ==========
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    skip: int
    limit: int
    pages: int


# ========== Response Schemas ==========
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    status: int
    message: str
    error: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
