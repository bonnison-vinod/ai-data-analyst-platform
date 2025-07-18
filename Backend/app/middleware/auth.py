from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.services.user_service import UserService
from app.utils.security import decode_token
from app.models.user import User
from typing import Optional

security = HTTPBearer()

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = decode_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        
        # Get user from database
        user = UserService.get_user_by_email(db, email=user_email)
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        return user
    
    except Exception:
        raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=400, 
            detail="Email not verified. Please verify your email address."
        )
    return current_user

def optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_token(token)
        if payload is None:
            return None
        
        user_email: str = payload.get("sub")
        if user_email is None:
            return None
        
        user = UserService.get_user_by_email(db, email=user_email)
        if user is None or not user.is_active:
            return None
        
        return user
    
    except Exception:
        return None
