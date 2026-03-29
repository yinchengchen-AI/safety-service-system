"""
Schema导出
"""
from app.schemas.base import (
    BaseOutSchema,
    BaseSchema,
    ListResponseSchema,
    PageResponseSchema,
    PaginationSchema,
    ResponseSchema,
)
from app.schemas.user import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    LoginRequest,
    LoginResponse,
    PermissionCreate,
    PermissionOut,
    PermissionUpdate,
    RefreshTokenRequest,
    RoleCreate,
    RoleOut,
    RoleSimpleOut,
    RoleUpdate,
    UserCreate,
    UserOut,
    UserPasswordUpdate,
    UserProfileOut,
    UserQuery,
    UserResetPassword,
    UserSimpleOut,
    UserUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    "BaseOutSchema",
    "PaginationSchema",
    "ResponseSchema",
    "ListResponseSchema",
    "PageResponseSchema",
    # User
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "UserSimpleOut",
    "UserProfileOut",
    "UserPasswordUpdate",
    "UserResetPassword",
    "UserQuery",
    # Role
    "RoleCreate",
    "RoleUpdate",
    "RoleOut",
    "RoleSimpleOut",
    # Department
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentOut",
    # Permission
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionOut",
    # Auth
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
]
