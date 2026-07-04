"""Database initialization and migration utilities."""

from sqlalchemy import text
from app.database.session import SessionLocal, engine, Base
from app.models.models import (
    User, Donor, Campaign, Donation, Milestone,
    CampaignUpdate, Comment, Transaction, Notification,
    Activity, Report, DonationHistory
)


def init_db():
    """Initialize all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_db():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully")


def reset_db():
    """Reset database (drop and create)."""
    drop_db()
    init_db()
    print("Database reset successfully")


def seed_database():
    """Seed database with initial data."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already seeded")
            return
        
        # Create admin user
        admin_user = User(
            id="admin-001",
            username="admin",
            email="admin@donorplatform.com",
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            hashed_password="$2b$12$...",  # Placeholder
            role="admin",
            is_verified=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("Database seeded successfully")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_database()
