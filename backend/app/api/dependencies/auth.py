"""
Dependency for getting the current authenticated user from the JWT token.
This will be used in protected routes that require authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import user as user_models
from app.services import user as user_service

# Configuration from auth.py
from app.api.endpoints.auth import SECRET_KEY, ALGORITHM, oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that validates the JWT token and returns the current user.
    This can be used in any endpoint that requires authentication.
    
    Example:
        @router.get("/me")
        async def read_users_me(current_user = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Optional: dependency for endpoints that need an active user
async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Dependency that ensures the user is active.
    This can be used in endpoints that require an active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user