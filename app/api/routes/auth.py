from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.core.roles import parse_roles, primary_role
from app.services.user_service import build_user_response

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: SessionDep):
    if len(user_in.password) < 10:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 10 characters long.",
        )
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create_user(db, user=user_in)
    return build_user_response(user)

@router.post("/login", response_model=Token)
def login_access_token(
    db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = crud_user.get_user_by_email(db, email=form_data.username) # Form uses 'username' instead of 'email'
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    roles = parse_roles(user.role)
    if not roles:
        raise HTTPException(status_code=500, detail="User role is invalid")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email,
            expires_delta=access_token_expires,
            additional_claims={"role": primary_role(roles), "roles": roles},
        ),
        "token_type": "bearer",
        "role": primary_role(roles),
        "roles": roles,
        "email": user.email,
    }
