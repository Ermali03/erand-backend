from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Doctor, User
from app.schemas.user import (
    StaffAccountCreate,
    StaffAccountResponse,
    StaffAccountUpdate,
    UserResponse,
    UserUpdateRoles,
)
from app.crud import user as crud_user
from app.core.roles import has_any_role, parse_roles, primary_role, serialize_roles


def build_user_response(user: User, doctor: Doctor | None = None) -> UserResponse:
    roles = parse_roles(user.role)
    return UserResponse(
        id=user.id,
        email=user.email,
        role=primary_role(roles),
        roles=roles,
        doctor_id=doctor.id if doctor else None,
        name=doctor.name if doctor else None,
        specialty=doctor.specialty if doctor else None,
    )


def build_staff_account_response(user: User, doctor: Doctor) -> StaffAccountResponse:
    roles = parse_roles(user.role)
    return StaffAccountResponse(
        user_id=user.id,
        doctor_id=doctor.id,
        name=doctor.name,
        specialty=doctor.specialty,
        email=user.email,
        role=primary_role(roles),
        roles=roles,
    )

class UserService:
    @staticmethod
    def get_users(db: Session, current_user: User) -> List[UserResponse]:
        if not has_any_role(current_user.role, {"Admin"}):
            raise HTTPException(status_code=403, detail="Not enough privileges")
        doctors_by_email = {
            doctor.email: doctor for doctor in db.query(Doctor).filter(Doctor.email.isnot(None)).all()
        }
        return [
            build_user_response(user, doctors_by_email.get(user.email))
            for user in crud_user.get_users(db)
        ]

    @staticmethod
    def update_user_roles(
        db: Session,
        user_id: int,
        role_in: UserUpdateRoles,
        current_user: User,
    ) -> UserResponse:
        if not has_any_role(current_user.role, {"Admin"}):
            raise HTTPException(status_code=403, detail="Not enough privileges")

        user_obj = db.query(User).filter(User.id == user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        normalized_roles = parse_roles(role_in.roles)
        if user_obj.id == current_user.id and "Admin" not in normalized_roles:
            raise HTTPException(
                status_code=400,
                detail="Admin cannot remove its own Admin access.",
            )

        doctor_obj = db.query(Doctor).filter(Doctor.email == user_obj.email).first()
        if doctor_obj:
            doctor_obj.role = serialize_roles(normalized_roles)

        updated_user = crud_user.update_user_roles(db, user=user_obj, roles=normalized_roles)
        if doctor_obj:
            db.refresh(doctor_obj)
        return build_user_response(updated_user)

    @staticmethod
    def create_staff_account(
        db: Session,
        staff_in: StaffAccountCreate,
        current_user: User,
    ) -> StaffAccountResponse:
        if not has_any_role(current_user.role, {"Admin"}):
            raise HTTPException(status_code=403, detail="Not enough privileges")

        existing_user = crud_user.get_user_by_email(db, email=staff_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists.",
            )

        doctor_id = f"DOC-{uuid4().hex[:8].upper()}"

        try:
            user = crud_user.create_user(
                db,
                user=staff_in,
                initial_role=serialize_roles(staff_in.roles),
                commit=False,
            )
            doctor = Doctor(
                id=doctor_id,
                name=staff_in.name,
                email=staff_in.email,
                specialty=staff_in.specialty,
                role=serialize_roles(staff_in.roles),
            )
            db.add(doctor)
            db.commit()
            db.refresh(user)
            db.refresh(doctor)
        except Exception:
            db.rollback()
            raise

        return build_staff_account_response(user, doctor)

    @staticmethod
    def update_staff_account(
        db: Session,
        user_id: int,
        staff_in: StaffAccountUpdate,
        current_user: User,
    ) -> StaffAccountResponse:
        if not has_any_role(current_user.role, {"Admin"}):
            raise HTTPException(status_code=403, detail="Not enough privileges")

        user_obj = db.query(User).filter(User.id == user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")

        doctor_obj = db.query(Doctor).filter(Doctor.email == user_obj.email).first()
        if not doctor_obj:
            raise HTTPException(status_code=404, detail="Linked doctor profile not found")

        if staff_in.email and staff_in.email != user_obj.email:
            existing_user = crud_user.get_user_by_email(db, email=staff_in.email)
            if existing_user and existing_user.id != user_obj.id:
                raise HTTPException(
                    status_code=400,
                    detail="A user with this email already exists.",
                )

        next_roles = parse_roles(staff_in.roles if staff_in.roles is not None else user_obj.role)
        if user_obj.id == current_user.id and "Admin" not in next_roles:
            raise HTTPException(
                status_code=400,
                detail="Admin cannot remove its own Admin access.",
            )

        if staff_in.name is not None:
            doctor_obj.name = staff_in.name
        if staff_in.specialty is not None:
            doctor_obj.specialty = staff_in.specialty
        if staff_in.email is not None:
            user_obj.email = staff_in.email
            doctor_obj.email = staff_in.email
        if staff_in.password is not None:
            from app.core.security import get_password_hash

            user_obj.hashed_password = get_password_hash(staff_in.password)
        user_obj.role = serialize_roles(next_roles)
        doctor_obj.role = serialize_roles(next_roles)

        db.add(user_obj)
        db.add(doctor_obj)
        db.commit()
        db.refresh(user_obj)
        db.refresh(doctor_obj)
        return build_staff_account_response(user_obj, doctor_obj)

    @staticmethod
    def delete_staff_account(db: Session, user_id: int, current_user: User) -> None:
        if not has_any_role(current_user.role, {"Admin"}):
            raise HTTPException(status_code=403, detail="Not enough privileges")

        user_obj = db.query(User).filter(User.id == user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        if user_obj.id == current_user.id:
            raise HTTPException(status_code=400, detail="Admin cannot delete itself.")

        doctor_obj = db.query(Doctor).filter(Doctor.email == user_obj.email).first()
        if doctor_obj:
            db.delete(doctor_obj)
        db.delete(user_obj)
        db.commit()
