from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, UserDetailResponse
)
from app.models.models import User
from app.utils.security import SecurityUtilities, PasswordUtilities
from app.utils.helpers import ValidationUtilities, GeneratorUtilities, LoggerUtilities
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["users"])
logger = LoggerUtilities.setup_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Validate email
    if not ValidationUtilities.validate_email(user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # Validate password
    is_strong, message = PasswordUtilities.validate_password_strength(user_data.password)
    if not is_strong:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    # Create user
    new_user = User(
        id=GeneratorUtilities.generate_uuid(),
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        organization=user_data.organization,
        hashed_password=SecurityUtilities.hash_password(user_data.password),
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.log_audit(new_user.id, "user_registered", {"email": user_data.email})
    return new_user


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    logger.log_audit(user_id, "user_updated", {"fields": list(update_data.keys())})
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    logger.log_audit(user_id, "user_deleted", {})


@router.post("/{user_id}/change-password")
def change_password(user_id: str, old_password: str, new_password: str, db: Session = Depends(get_db)):
    """Change user password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not SecurityUtilities.verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    
    is_strong, message = PasswordUtilities.validate_password_strength(new_password)
    if not is_strong:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    user.hashed_password = SecurityUtilities.hash_password(new_password)
    db.commit()
    
    logger.log_audit(user_id, "password_changed", {})
    return {"message": "Password changed successfully"}


@router.post("/{user_id}/verify-email")
def verify_email(user_id: str, token: str, db: Session = Depends(get_db)):
    """Verify user email."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    logger.log_audit(user_id, "email_verified", {})
    return {"message": "Email verified successfully"}


@router.get("/{user_id}/profile")
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "organization": user.organization,
        "profile_image": user.profile_image,
        "bio": user.bio,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at,
        "last_login": user.last_login
    }


@router.post("/{user_id}/preferences")
def update_user_preferences(user_id: str, preferences: dict, db: Session = Depends(get_db)):
    """Update user preferences."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.preferences = preferences
    db.commit()
    
    logger.log_audit(user_id, "preferences_updated", {"preferences": preferences})
    return {"message": "Preferences updated successfully"}


@router.get("/{user_id}/notifications")
def get_user_notifications(user_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get user notifications."""
    from app.models.models import Notification
    
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return notifications


@router.post("/{user_id}/notifications/{notification_id}/read")
def mark_notification_as_read(user_id: str, notification_id: str, db: Session = Depends(get_db)):
    """Mark notification as read."""
    from app.models.models import Notification
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.get("/{user_id}/activity-log")
def get_user_activity_log(user_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get user activity log."""
    from app.models.models import Activity
    
    activities = db.query(Activity).filter(
        Activity.user_id == user_id
    ).order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()
    
    return activities


@router.get("/{user_id}/search")
def search_users(query: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Search users."""
    users = db.query(User).filter(
        (User.first_name.ilike(f"%{query}%")) |
        (User.last_name.ilike(f"%{query}%")) |
        (User.email.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()
    
    return users
