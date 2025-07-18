from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserRegistration, UserLogin, LoginResponse, PasswordReset, PasswordResetConfirm, UserResponse
from app.services.user_service import UserService
from app.utils.security import create_access_token
from app.middleware.auth import get_current_user, get_current_active_user, get_current_verified_user
from app.database.config import get_db

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    """User registration endpoint"""
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/login", response_model=LoginResponse)
def login_user(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """User login endpoint"""
    user = UserService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create user session
    user_session = UserService.create_user_session(
        db, user, ip_address=request.client.host, user_agent=request.headers.get("user-agent")
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "expires_in": 3600 * 24 * 7  # 7 days
    }

@router.post("/auth/password-reset")
def initiate_password_reset(data: PasswordReset, db: Session = Depends(get_db)):
    """Initiate password reset process"""
    reset_token = UserService.initiate_password_reset(db, data.email)
    if not reset_token:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Here, you would send the reset token via email
    print(f"Password reset token: {reset_token}")  # This is for debugging purposes

@router.post("/auth/password-reset-confirm")
def password_reset_confirm(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset"""
    success = UserService.reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

@router.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.get("/auth/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email address"""
    success = UserService.verify_email(db, token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
