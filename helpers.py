import json
import logging
from typing import Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class LoggerUtilities:
    @staticmethod
    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        """Setup a logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))
        
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, level))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    @staticmethod
    def log_request(method: str, path: str, status_code: int, duration: float) -> None:
        """Log API request."""
        logger.info(
            f"Method: {method}, Path: {path}, Status: {status_code}, Duration: {duration}ms"
        )

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """Log error."""
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)

    @staticmethod
    def log_audit(user_id: str, action: str, details: dict = None) -> None:
        """Log audit trail."""
        logger.info(
            f"Audit: User {user_id} performed action '{action}' with details {details}"
        )


class ValidationUtilities:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number."""
        import re
        pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url.lower()) is not None

    @staticmethod
    def validate_currency_amount(amount: float) -> bool:
        """Validate currency amount."""
        return isinstance(amount, (int, float)) and amount >= 0

    @staticmethod
    def validate_date(date_string: str, format: str = "%Y-%m-%d") -> bool:
        """Validate date string."""
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            return False


class GeneratorUtilities:
    @staticmethod
    def generate_uuid() -> str:
        """Generate a unique UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_reference_id(prefix: str = "") -> str:
        """Generate a reference ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}{timestamp}{unique_id}"

    @staticmethod
    def generate_invoice_number(year: int = None, sequence: int = None) -> str:
        """Generate an invoice number."""
        if year is None:
            year = datetime.utcnow().year
        if sequence is None:
            sequence = uuid.uuid4().int % 10000
        return f"INV-{year}-{sequence:05d}"

    @staticmethod
    def generate_donation_receipt(donation_id: str) -> str:
        """Generate a donation receipt number."""
        return f"REC-{datetime.utcnow().strftime('%Y%m%d')}-{donation_id[:8].upper()}"


class FormatterUtilities:
    @staticmethod
    def format_currency(amount: float, currency: str = "USD") -> str:
        """Format currency amount."""
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        elif currency == "INR":
            return f"₹{amount:,.2f}"
        return f"{currency} {amount:,.2f}"

    @staticmethod
    def format_date(date: datetime, format: str = "%Y-%m-%d") -> str:
        """Format date."""
        return date.strftime(format)

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number."""
        cleaned = ''.join(filter(str.isdigit, phone))
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        elif len(cleaned) == 11:
            return f"+{cleaned[0]} ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
        return phone

    @staticmethod
    def truncate_string(text: str, length: int = 100) -> str:
        """Truncate string to specified length."""
        if len(text) <= length:
            return text
        return text[:length-3] + "..."

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to slug format."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')


class PaginationUtilities:
    @staticmethod
    def get_pagination_params(skip: int = 0, limit: int = 10) -> tuple[int, int]:
        """Get validated pagination parameters."""
        if skip < 0:
            skip = 0
        if limit < 1:
            limit = 10
        if limit > 100:
            limit = 100
        return skip, limit

    @staticmethod
    def get_offset_limit(page: int = 1, page_size: int = 10) -> tuple[int, int]:
        """Convert page number to offset and limit."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        return offset, page_size

    @staticmethod
    def calculate_total_pages(total_items: int, page_size: int = 10) -> int:
        """Calculate total pages."""
        if page_size < 1:
            page_size = 10
        return (total_items + page_size - 1) // page_size


class FileUtilities:
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension."""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ""

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
        """Validate file extension."""
        ext = FileUtilities.get_file_extension(filename)
        return ext in allowed_extensions

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
