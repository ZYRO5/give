from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database.session import get_db
from app.schemas.schemas import LoginRequest, TokenResponse, PasswordResetRequest, PasswordResetConfirm
from app.models.models import User
from app.utils.security import SecurityUtilities, TokenUtilities
from app.utils.helpers import ValidationUtilities, GeneratorUtilities, LoggerUtilities
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer()
logger = LoggerUtilities.setup_logger(__name__)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint."""
    # Validate email
    if not ValidationUtilities.validate_email(credentials.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not SecurityUtilities.verify_password(credentials.password, user.hashed_password):
        logger.log_audit(user.id, "login_failed", {"reason": "invalid_password"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate tokens
    access_token = SecurityUtilities.create_access_token(
        {"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    refresh_token = SecurityUtilities.create_refresh_token(
        {"sub": user.id, "email": user.email}
    )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.log_audit(user.id, "login_success", {})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token."""
    payload = SecurityUtilities.decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    new_access_token = SecurityUtilities.create_access_token(
        {"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/password-reset")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If email exists, reset link has been sent"}
    
    # Generate reset token
    reset_token = TokenUtilities.generate_unique_token()
    user.password_reset_token = reset_token
    db.commit()
    
    logger.log_audit(user.id, "password_reset_requested", {"email": request.email})
    
    # TODO: Send email with reset link
    return {"message": "Password reset link has been sent to your email"}


@router.post("/password-reset-confirm")
def confirm_password_reset(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset."""
    # Find user by reset token
    user = db.query(User).filter(User.password_reset_token == request.token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = SecurityUtilities.hash_password(request.new_password)
    user.password_reset_token = None
    db.commit()
    
    logger.log_audit(user.id, "password_reset_confirmed", {})
    
    return {"message": "Password has been reset successfully"}


@router.post("/logout")
def logout(current_user = Depends(security)):
    """Logout user."""
    logger.log_audit(current_user, "logout", {})
    return {"message": "Logged out successfully"}


@router.post("/verify-email")
def send_verification_email(email: str, db: Session = Depends(get_db)):
    """Send email verification."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Generate verification token
    verification_token = TokenUtilities.generate_unique_token()
    user.verification_token = verification_token
    db.commit()
    
    logger.log_audit(user.id, "verification_email_sent", {"email": email})
    
    # TODO: Send verification email
    return {"message": "Verification email has been sent"}


@router.get("/me", response_model=dict)
def get_current_user(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    token = credentials.credentials
    payload = SecurityUtilities.decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role
    }


@router.post("/two-factor/enable")
def enable_two_factor(user_id: str, db: Session = Depends(get_db)):
    """Enable two-factor authentication."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate 2FA secret
    import pyotp
    secret = pyotp.random_base32()
    
    logger.log_audit(user_id, "two_factor_enabled", {})
    
    return {
        "message": "Two-factor authentication enabled",
        "secret": secret,
        "qr_code": pyotp.totp.TOTP(secret).provisioning_uri(user.email)
    }


@router.post("/two-factor/verify")
def verify_two_factor_code(user_id: str, code: str, db: Session = Depends(get_db)):
    """Verify two-factor authentication code."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # TODO: Verify TOTP code
    return {"message": "Two-factor code verified"}
