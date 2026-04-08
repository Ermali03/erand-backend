from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str  # validated in API layer and hashed before storage
    # Default role applied in DB / CRUD

class UserUpdateRole(BaseModel):
    role: Literal["Admin", "Main Surgeon", "Doctor", "Nurse"]


class UserUpdateRoles(BaseModel):
    roles: list[Literal["Admin", "Main Surgeon", "Doctor", "Nurse"]]

    @model_validator(mode="after")
    def validate_roles(self) -> "UserUpdateRoles":
        if not self.roles:
            raise ValueError("At least one role must be selected.")
        return self


class StaffAccountCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    roles: list[Literal["Admin", "Main Surgeon", "Doctor", "Nurse"]]

    @model_validator(mode="after")
    def validate_roles(self) -> "StaffAccountCreate":
        if not self.roles:
            raise ValueError("At least one role must be selected.")
        return self


class StaffAccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    specialty: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=10, max_length=128)
    roles: list[Literal["Admin", "Main Surgeon", "Doctor", "Nurse"]] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "StaffAccountUpdate":
        if all(
            value is None
            for value in (self.name, self.specialty, self.email, self.password, self.roles)
        ):
            raise ValueError("At least one field must be provided.")
        if self.roles is not None and not self.roles:
            raise ValueError("At least one role must be selected.")
        return self


class StaffAccountResponse(BaseModel):
    user_id: int
    doctor_id: str
    name: str
    specialty: str
    email: EmailStr
    role: str
    roles: list[str]

class UserResponse(UserBase):
    id: int
    role: str
    roles: list[str]
    doctor_id: str | None = None
    name: str | None = None
    specialty: str | None = None

    model_config = {"from_attributes": True}
