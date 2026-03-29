"""
权限控制功能
"""
from enum import Enum
from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.crud.user import user_crud


class PermissionCode(str, Enum):
    """权限编码枚举"""
    # 用户管理
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 角色管理
    ROLE_VIEW = "role:view"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # 客户管理
    COMPANY_VIEW = "company:view"
    COMPANY_CREATE = "company:create"
    COMPANY_UPDATE = "company:update"
    COMPANY_DELETE = "company:delete"
    
    # 合同管理
    CONTRACT_VIEW = "contract:view"
    CONTRACT_CREATE = "contract:create"
    CONTRACT_UPDATE = "contract:update"
    CONTRACT_DELETE = "contract:delete"
    CONTRACT_APPROVE = "contract:approve"
    
    # 服务管理
    SERVICE_VIEW = "service:view"
    SERVICE_CREATE = "service:create"
    SERVICE_UPDATE = "service:update"
    SERVICE_DELETE = "service:delete"
    
    # 财务管理
    INVOICE_VIEW = "invoice:view"
    INVOICE_CREATE = "invoice:create"
    INVOICE_APPROVE = "invoice:approve"
    PAYMENT_VIEW = "payment:view"
    PAYMENT_CREATE = "payment:create"
    
    # 文档管理
    DOCUMENT_VIEW = "document:view"
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_UPDATE = "document:update"
    DOCUMENT_DELETE = "document:delete"
    
    # 公告管理
    NOTICE_VIEW = "notice:view"
    NOTICE_CREATE = "notice:create"
    NOTICE_UPDATE = "notice:update"
    NOTICE_DELETE = "notice:delete"
    
    # 系统管理
    SYSTEM_CONFIG = "system:config"
    LOG_VIEW = "log:view"
    STATISTICS_VIEW = "statistics:view"


async def get_current_user(
    token: str = Depends(lambda: ""),  # 这里需要从请求头获取
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取当前用户"""
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # 这里会在deps.py中实现，这里是占位
    pass


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, current_user: Any = Depends(get_current_user)):
        """检查权限"""
        if current_user.is_superuser:
            return current_user
        
        user_permissions = set()
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.code)
        
        for required in self.required_permissions:
            if required not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
        
        return current_user


def require_permissions(permissions: list[str]):
    """权限装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 权限检查逻辑在依赖注入中处理
            return await func(*args, **kwargs)
        return wrapper
    return decorator
