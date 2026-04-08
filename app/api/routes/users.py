from typing import List
from fastapi import APIRouter, status
from app.api.deps import SessionDep, CurrentUser
from app.schemas.user import (
    StaffAccountCreate,
    StaffAccountResponse,
    StaffAccountUpdate,
    UserResponse,
    UserUpdateRoles,
)
from app.services.user_service import UserService
from app.services.user_service import build_user_response

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return build_user_response(current_user)


@router.get("/", response_model=List[UserResponse])
def get_all_users(db: SessionDep, current_user: CurrentUser):
    return UserService.get_users(db, current_user)


@router.post("/staff", response_model=StaffAccountResponse, status_code=status.HTTP_201_CREATED)
def create_staff_account(
    staff_in: StaffAccountCreate,
    db: SessionDep,
    current_user: CurrentUser,
):
    return UserService.create_staff_account(db, staff_in, current_user)


@router.put("/{user_id}/staff", response_model=StaffAccountResponse)
def update_staff_account(
    user_id: int,
    staff_in: StaffAccountUpdate,
    db: SessionDep,
    current_user: CurrentUser,
):
    return UserService.update_staff_account(db, user_id, staff_in, current_user)


@router.put("/{user_id}/roles", response_model=UserResponse)
def update_user_roles(
    user_id: int, 
    role_in: UserUpdateRoles, 
    db: SessionDep, 
    current_user: CurrentUser
):
    return UserService.update_user_roles(db, user_id, role_in, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: SessionDep,
    current_user: CurrentUser,
):
    UserService.delete_staff_account(db, user_id, current_user)
