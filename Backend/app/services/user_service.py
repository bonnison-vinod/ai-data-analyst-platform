from sqlalchemy.orm import Session
from app.models.user import User, UserSession
from app.schemas.user import UserRegistration, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token, generate_session_token
from datetime import datetime, timedelta
from typing import Optional
import uuid

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserRegistration) -> User:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        verification_token = str(uuid.uuid4())
        
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            company=user_data.company,
            position=user_data.position,
            email_verification_token=verification_token
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise ValueError("Account is temporarily locked due to too many failed login attempts")
        
        # Check if account is active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            db.commit()
            return None
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_user_session(db: Session, user: User, ip_address: str = None, user_agent: str = None) -> UserSession:
        # Deactivate old sessions
        db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        # Create new session
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days
        
        db_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        return db_session
    
    @staticmethod
    def get_user_by_session(db: Session, session_token: str) -> Optional[User]:
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        user = db.query(User).filter(User.id == session.user_id).first()
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def logout_user(db: Session, session_token: str) -> bool:
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        user = db.query(User).filter(User.email_verification_token == token).first()
        if not user:
            return False
        
        user.is_verified = True
        user.email_verification_token = None
        db.commit()
        return True
    
    @staticmethod
    def initiate_password_reset(db: Session, email: str) -> Optional[str]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        return reset_token
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        user = db.query(User).filter(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow()
        ).first()
        
        if not user:
            return False
        
        user.hashed_password = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
        
        return True
