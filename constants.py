from enum import Enum


class DonorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"


class DonationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CASH = "cash"


class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    DONOR = "donor"
    ORGANIZATION = "organization"
    VOLUNTEER = "volunteer"


class NotificationType(str, Enum):
    DONATION_RECEIVED = "donation_received"
    CAMPAIGN_UPDATED = "campaign_updated"
    CAMPAIGN_COMPLETED = "campaign_completed"
    DONATION_RECEIPT = "donation_receipt"
    SYSTEM_ALERT = "system_alert"
    NEW_CAMPAIGN = "new_campaign"
    THANK_YOU_MESSAGE = "thank_you_message"


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


class TransactionType(str, Enum):
    DONATION = "donation"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"
    ADJUSTMENT = "adjustment"


class EmailTemplate(str, Enum):
    WELCOME = "welcome"
    DONATION_CONFIRMATION = "donation_confirmation"
    DONATION_RECEIPT = "donation_receipt"
    CAMPAIGN_UPDATE = "campaign_update"
    CAMPAIGN_COMPLETED = "campaign_completed"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_VERIFICATION = "account_verification"
    THANK_YOU = "thank_you"
    REMINDER = "reminder"
    NEWSLETTER = "newsletter"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class ApiStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    FAILED = "failed"


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"


# Constants
SUPPORTED_IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
SUPPORTED_DOCUMENT_FORMATS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
TOKEN_EXPIRY_MINUTES = 30
REFRESH_TOKEN_EXPIRY_DAYS = 7
PASSWORD_MIN_LENGTH = 8
