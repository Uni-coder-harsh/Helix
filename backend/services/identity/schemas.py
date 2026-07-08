# Unified validation schemas for Auth, Identity, and User Management
import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

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


# Geographic Schemas
class CountryCreate(BaseModel):
    name: str
    code: str | None = None


class CountryUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None


class CountryResponse(BaseModel):
    id: str
    name: str
    code: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StateCreate(BaseModel):
    name: str
    country_id: str
    code: str | None = None


class StateUpdate(BaseModel):
    name: str | None = None
    country_id: str | None = None
    code: str | None = None
    is_active: bool | None = None


class StateResponse(BaseModel):
    id: str
    name: str
    country_id: str
    code: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DistrictCreate(BaseModel):
    name: str
    state_id: str
    code: str | None = None


class DistrictUpdate(BaseModel):
    name: str | None = None
    state_id: str | None = None
    code: str | None = None
    is_active: bool | None = None


class DistrictResponse(BaseModel):
    id: str
    name: str
    state_id: str
    code: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConstituencyCreate(BaseModel):
    name: str
    district_id: str
    parliamentary_constituency_id: str | None = None
    code: str | None = None
    geojson_boundary: str | None = None
    area_metadata: str | None = None
    population_metadata: str | None = None


class ConstituencyResponse(BaseModel):
    id: str
    name: str
    district_id: str
    parliamentary_constituency_id: str | None = None
    code: str | None = None
    is_active: bool
    geojson_boundary: str | None = None
    boundary_version: int
    area_metadata: str | None = None
    population_metadata: str | None = None
    mla_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WardCreate(BaseModel):
    name: str
    assembly_constituency_id: str | None = None
    constituency_id: str | None = None
    code: str | None = None
    geojson_boundary: str | None = None

    @model_validator(mode="after")
    def validate_parent_reference(self) -> "WardCreate":
        if self.assembly_constituency_id or self.constituency_id:
            return self
        raise ValueError("assembly_constituency_id or constituency_id must be provided")


class WardResponse(BaseModel):
    id: str
    name: str
    assembly_constituency_id: str
    constituency_id: str
    code: str | None = None
    is_active: bool
    geojson_boundary: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


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
    name: str = "Citizen"
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    phone: str | None = None
    bio: str | None = None

    # Geography Onboarding
    state_id: str | None = None
    district_id: str | None = None
    constituency_id: str | None = None
    ward_or_village: str | None = None
    address: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    bio: str | None = None
    department_id: str | None = None
    state_id: str | None = None
    district_id: str | None = None
    constituency_id: str | None = None
    ward_or_village: str | None = None
    address: str | None = None


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

    # Geography Onboarding
    state_id: str | None = None
    district_id: str | None = None
    constituency_id: str | None = None
    ward_or_village: str | None = None
    address: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field(..., description="Role to invite: MLA or OFFICER")
    department_id: str | None = None
    constituency_id: str | None = None


class InvitationAccept(BaseModel):
    token: str
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    name: str
    phone: str | None = None
    bio: str | None = None


class InvitationResponse(BaseModel):
    id: str
    email: str
    role: str
    department_id: str | None = None
    constituency_id: str | None = None
    token: str
    status: str
    invited_by: str
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Unified token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: UserResponse | None = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    device_info: str | None = None
    ip_address: str | None = None
    is_active: bool
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class AuditLoginResponse(BaseModel):
    id: str
    user_id: str | None = None
    email: str
    event_type: str
    ip_address: str | None = None
    user_agent: str | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# RBAC Schemas
class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    parent_role_id: str | None = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    parent_role_id: str | None = None

    model_config = {"from_attributes": True}


class PermissionCreate(BaseModel):
    name: str
    description: str | None = None


class PermissionResponse(BaseModel):
    id: str
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class ParliamentaryConstituencyCreate(BaseModel):
    name: str
    state_id: str
    code: str | None = None
    geojson_boundary: str | None = None
    area_metadata: str | None = None
    population_metadata: str | None = None


class ParliamentaryConstituencyUpdate(BaseModel):
    name: str | None = None
    state_id: str | None = None
    code: str | None = None
    is_active: bool | None = None
    geojson_boundary: str | None = None
    area_metadata: str | None = None
    population_metadata: str | None = None


class ParliamentaryConstituencyResponse(BaseModel):
    id: str
    name: str
    state_id: str
    code: str | None = None
    is_active: bool
    geojson_boundary: str | None = None
    boundary_version: int
    area_metadata: str | None = None
    population_metadata: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssemblyConstituencyCreate(BaseModel):
    name: str
    district_id: str
    parliamentary_constituency_id: str | None = None
    code: str | None = None
    geojson_boundary: str | None = None
    area_metadata: str | None = None
    population_metadata: str | None = None


class AssemblyConstituencyUpdate(BaseModel):
    name: str | None = None
    district_id: str | None = None
    parliamentary_constituency_id: str | None = None
    code: str | None = None
    is_active: bool | None = None
    geojson_boundary: str | None = None
    area_metadata: str | None = None
    population_metadata: str | None = None


class AssemblyConstituencyResponse(BaseModel):
    id: str
    name: str
    district_id: str
    parliamentary_constituency_id: str | None = None
    code: str | None = None
    is_active: bool
    geojson_boundary: str | None = None
    boundary_version: int
    area_metadata: str | None = None
    population_metadata: str | None = None
    mla_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WardUpdate(BaseModel):
    name: str | None = None
    assembly_constituency_id: str | None = None
    constituency_id: str | None = None
    code: str | None = None
    is_active: bool | None = None
    geojson_boundary: str | None = None


class VillageCreate(BaseModel):
    name: str
    assembly_constituency_id: str | None = None
    constituency_id: str | None = None
    code: str | None = None
    geojson_boundary: str | None = None

    @model_validator(mode="after")
    def validate_parent_reference(self) -> "VillageCreate":
        if self.assembly_constituency_id or self.constituency_id:
            return self
        raise ValueError("assembly_constituency_id or constituency_id must be provided")


class VillageUpdate(BaseModel):
    name: str | None = None
    assembly_constituency_id: str | None = None
    constituency_id: str | None = None
    code: str | None = None
    is_active: bool | None = None
    geojson_boundary: str | None = None


class VillageResponse(BaseModel):
    id: str
    name: str
    assembly_constituency_id: str
    constituency_id: str
    code: str | None = None
    is_active: bool
    geojson_boundary: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BoundaryUploadRequest(BaseModel):
    geojson_boundary: str


class JurisdictionLookupResponse(BaseModel):
    state: dict[str, Any] | None = None
    district: dict[str, Any] | None = None
    parliamentary_constituency: dict[str, Any] | None = None
    assembly_constituency: dict[str, Any] | None = None
    ward: dict[str, Any] | None = None
    village: dict[str, Any] | None = None
