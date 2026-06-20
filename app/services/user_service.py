from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Fetch user by primary key ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch user by unique email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """Create new user with hashed password and defaults."""
        hashed_pwd = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
            role=user_in.role or "User"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate) -> User:
        """Update existing user properties."""
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by checking email and matching password hash."""
        db_user = UserService.get_by_email(db, email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """List users (useful for Admins)."""
        return db.query(User).offset(skip).limit(limit).all()
