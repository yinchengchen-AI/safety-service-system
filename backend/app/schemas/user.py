"""
用户相关Schema
"""
from datetime import datetime
from typing import Any

from pydantic import EmailStr, Field, model_validator

from app.schemas.base import BaseOutSchema, BaseSchema


# ==================== 部门Schema ====================
class DepartmentBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    parent_id: int | None = None
    sort_order: int = 0
    description: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=100)
    code: str | None = Field(None, min_length=1, max_length=50)
    parent_id: int | None = None
    sort_order: int | None = None
    description: str | None = None


class DepartmentOut(DepartmentBase, BaseOutSchema):
    children: list["DepartmentOut"] = []


# ==================== 权限Schema ====================
class PermissionBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(menu|button|api)$")
    parent_id: int | None = None
    path: str | None = None
    icon: str | None = None
    sort_order: int = 0
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=50)
    code: str | None = Field(None, min_length=1, max_length=100)
    type: str | None = Field(None, pattern="^(menu|button|api)$")
    parent_id: int | None = None
    path: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    description: str | None = None


class PermissionOut(PermissionBase, BaseOutSchema):
    children: list["PermissionOut"] = []


# ==================== 角色Schema ====================
class RoleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    sort_order: int = 0


class RoleCreate(RoleBase):
    permission_ids: list[int] = []


class RoleUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=50)
    code: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = None
    sort_order: int | None = None
    permission_ids: list[int] | None = None


class RoleOut(RoleBase, BaseOutSchema):
    is_system: bool
    permissions: list[dict] = []


class RoleSimpleOut(BaseSchema):
    id: int
    name: str
    code: str


# ==================== 用户Schema ====================
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    real_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    department_id: int | None = None
    status: str = "active"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)
    role_ids: list[int] = []
    is_superuser: bool = False


class UserUpdate(BaseSchema):
    username: str | None = Field(None, min_length=3, max_length=50)
    real_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    department_id: int | None = None
    status: str | None = None
    role_ids: list[int] | None = None


class UserOut(UserBase, BaseOutSchema):
    avatar: str | None = None
    is_superuser: bool
    last_login_at: datetime | None = None
    department: dict | None = None
    roles: list[dict] = []


class UserSimpleOut(BaseSchema):
    id: int
    username: str
    real_name: str | None = None
    avatar: str | None = None


class UserProfileOut(BaseSchema):
    id: int
    username: str
    real_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    department: dict | None = None
    roles: list[str] = []
    permissions: list[str] = []


class UserPasswordUpdate(BaseSchema):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("新密码和确认密码不一致")
        return self


class UserProfileUpdate(BaseSchema):
    """个人资料更新"""
    real_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    avatar: str | None = Field(None, max_length=255)


class UserResetPassword(BaseSchema):
    new_password: str = Field(..., min_length=6, max_length=50)


# ==================== 登录Schema ====================
class LoginRequest(BaseSchema):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileOut


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


# ==================== 查询参数 ====================
class UserQuery(BaseSchema):
    keyword: str | None = None
    department_id: int | None = None
    status: str | None = None
    page: int = 1
    page_size: int = 20


class RoleQuery(BaseSchema):
    keyword: str | None = None
    page: int = 1
    page_size: int = 20


class DepartmentQuery(BaseSchema):
    keyword: str | None = None
