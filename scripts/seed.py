import sys
import os
from datetime import datetime, timedelta, timezone

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.base_class import Base
from app.models.user import User
from app.models.category import Category
from app.models.event import Event
from app.core.security import get_password_hash


def seed_database():
    print("Initializing Database...")
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Seed Categories
        categories_data = [
            {"name": "Technology", "slug": "technology", "description": "Tech conferences, workshops, hackathons"},
            {"name": "Music & Concerts", "slug": "music-concerts", "description": "Live concerts, festivals, music performances"},
            {"name": "Sports & Fitness", "slug": "sports-fitness", "description": "Athletic events, matches, workouts"},
            {"name": "Food & Drink", "slug": "food-drink", "description": "Wine tastings, cooking masterclasses, food markets"},
            {"name": "Business & Startups", "slug": "business-startups", "description": "Networking, pitches, business development sessions"}
        ]
        
        categories = []
        for cat_data in categories_data:
            existing_cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing_cat:
                cat = Category(**cat_data)
                db.add(cat)
                categories.append(cat)
                print(f"Seeded category: {cat_data['name']}")
            else:
                categories.append(existing_cat)
        
        # Flush to get IDs
        db.commit()

        # 2. Seed Users
        users_data = [
            {
                "email": "admin@eventsphere.com",
                "hashed_password": get_password_hash("adminpassword"),
                "full_name": "EventSphere Admin",
                "role": "Admin"
            },
            {
                "email": "organizer@eventsphere.com",
                "hashed_password": get_password_hash("organizerpassword"),
                "full_name": "Jane Organizer",
                "role": "Organizer"
            },
            {
                "email": "user@eventsphere.com",
                "hashed_password": get_password_hash("userpassword"),
                "full_name": "John Regular User",
                "role": "User"
            }
        ]
        
        seeded_users = {}
        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                usr = User(**user_data)
                db.add(usr)
                seeded_users[user_data["role"]] = usr
                print(f"Seeded {user_data['role']} user: {user_data['email']}")
            else:
                seeded_users[user_data["role"]] = existing_user

        db.commit()

        # 3. Seed Events
        organizer = seeded_users.get("Organizer")
        tech_cat = next((c for c in categories if c.slug == "technology"), None)
        
        if organizer and tech_cat:
            existing_event = db.query(Event).filter(Event.title == "EventSphere Tech Hackathon 2026").first()
            if not existing_event:
                event = Event(
                    title="EventSphere Tech Hackathon 2026",
                    description="The ultimate annual weekend hacking event to build cutting edge web services using FastAPI.",
                    location="Silicon Valley Innovation Hub, CA",
                    date_time=datetime.now(timezone.utc) + timedelta(days=30),
                    capacity=50,
                    organizer_id=organizer.id,
                    category_id=tech_cat.id
                )
                db.add(event)
                print(f"Seeded Event: {event.title}")
            
        db.commit()
        print("Database Seed completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"An error occurred during database seeding: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
