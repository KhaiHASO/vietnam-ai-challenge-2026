from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    ADMIN = "admin"
    EXPERT = "expert"
    OPERATOR = "operator"
    TEACHER = "teacher"
    STUDENT = "student"


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    tenant_id: str = "single"
    roles: frozenset[Role] = Field(default_factory=frozenset)


class SessionToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str = Field(exclude=True)
    token_type: str = "bearer"
    expires_in: int
    family_id: str = Field(exclude=True)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=1024)


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=12, max_length=1024)
    email: str | None = Field(default=None, max_length=320)
    roles: frozenset[Role] = Field(min_length=1)


class UserStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_active: bool


class UserView(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: str
    tenant_id: str
    username: str
    email: str | None = None
    roles: list[Role]
    is_active: bool
