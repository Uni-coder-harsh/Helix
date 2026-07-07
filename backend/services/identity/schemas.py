# Unified validation schemas for Auth, Identity, and User Management
import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    name: str = Field(default="Citizen")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


class UserRegisterResponse(BaseModel):
    id: str
    email: str
    is_verified: bool


class UserLoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


class VerifyEmailRequest(BaseModel):
    token: str


# User Management Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    status: str
    department_id: str | None = None
    phone: str | None = None
    bio: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str | None = None
    bio: str | None = None


class CitizenRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str | None = None
    bio: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    bio: str | None = None
    department_id: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    status: str
    is_verified: bool = False
    department_id: str | None = None
    phone: str | None = None
    bio: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field(..., description="Role to invite: MLA or OFFICER")
    department_id: str | None = None


class InvitationAccept(BaseModel):
    token: str
    password: str
    name: str
    phone: str | None = None
    bio: str | None = None


class InvitationResponse(BaseModel):
    id: str
    email: str
    role: str
    department_id: str | None = None
    token: str
    status: str
    invited_by: str
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Unified token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: UserResponse | None = None
