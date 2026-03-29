"""
CRUD导出
"""
from app.crud.user import user_crud, role_crud, dept_crud, permission_crud

__all__ = [
    "user_crud",
    "role_crud", 
    "dept_crud",
    "permission_crud",
]
