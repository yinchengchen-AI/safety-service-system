"""
全局依赖（保持兼容性）
"""
# 从api.deps导出
from app.api.deps import (
    get_current_user,
    get_current_active_user,
    require_permissions,
    require_superuser,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "require_permissions",
    "require_superuser",
]
