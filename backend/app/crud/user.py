"""
用户、角色、部门CRUD
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.user import Department, Permission, Role, User


class CRUDUser(CRUDBase[User]):
    """用户CRUD"""
    
    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """根据用户名获取"""
        result = await db.execute(
            select(User)
            .where(User.username == username, User.is_deleted == False)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .options(selectinload(User.department))
        )
        return result.scalar_one_or_none()
    
    async def get_with_roles(self, db: AsyncSession, id: int) -> User | None:
        """获取用户及其角色"""
        result = await db.execute(
            select(User)
            .where(User.id == id, User.is_deleted == False)
            .options(selectinload(User.roles))
            .options(selectinload(User.department))
        )
        return result.scalar_one_or_none()
    
    async def get_multi_with_roles(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: str | None = None,
        department_id: int | None = None,
        status: str | None = None
    ) -> list[User]:
        """获取用户列表（带角色）"""
        query = (
            select(User)
            .where(User.is_deleted == False)
            .options(selectinload(User.roles))
            .options(selectinload(User.department))
        )
        
        if keyword:
            query = query.where(
                (User.username.ilike(f"%{keyword}%")) |
                (User.real_name.ilike(f"%{keyword}%")) |
                (User.phone.ilike(f"%{keyword}%"))
            )
        
        if department_id:
            query = query.where(User.department_id == department_id)
        
        if status:
            query = query.where(User.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count_with_filter(
        self,
        db: AsyncSession,
        *,
        keyword: str | None = None,
        department_id: int | None = None,
        status: str | None = None
    ) -> int:
        """统计用户数"""
        from sqlalchemy import func
        
        query = select(func.count(User.id)).where(User.is_deleted == False)
        
        if keyword:
            query = query.where(
                (User.username.ilike(f"%{keyword}%")) |
                (User.real_name.ilike(f"%{keyword}%")) |
                (User.phone.ilike(f"%{keyword}%"))
            )
        
        if department_id:
            query = query.where(User.department_id == department_id)
        
        if status:
            query = query.where(User.status == status)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def create_with_roles(
        self,
        db: AsyncSession,
        *,
        obj_in: dict[str, Any],
        role_ids: list[int]
    ) -> User:
        """创建用户并分配角色"""
        # 移除role_ids
        user_data = {k: v for k, v in obj_in.items() if k != "role_ids"}
        
        db_obj = User(**user_data)
        
        # 获取角色
        if role_ids:
            roles_result = await db.execute(
                select(Role).where(Role.id.in_(role_ids))
            )
            db_obj.roles = list(roles_result.scalars().all())
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_with_roles(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: dict[str, Any],
        role_ids: list[int] | None = None
    ) -> User:
        """更新用户及角色"""
        # 更新基本信息
        update_data = {k: v for k, v in obj_in.items() if k != "role_ids" and v is not None}
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # 更新角色
        if role_ids is not None:
            roles_result = await db.execute(
                select(Role).where(Role.id.in_(role_ids))
            )
            db_obj.roles = list(roles_result.scalars().all())
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class CRUDRole(CRUDBase[Role]):
    """角色CRUD"""
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Role | None:
        """根据编码获取"""
        result = await db.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_with_permissions(self, db: AsyncSession, id: int) -> Role | None:
        """获取角色及其权限"""
        result = await db.execute(
            select(Role)
            .where(Role.id == id)
            .options(selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()
    
    async def create_with_permissions(
        self,
        db: AsyncSession,
        *,
        obj_in: dict[str, Any],
        permission_ids: list[int]
    ) -> Role:
        """创建角色并分配权限"""
        role_data = {k: v for k, v in obj_in.items() if k != "permission_ids"}
        db_obj = Role(**role_data)
        
        if permission_ids:
            perms_result = await db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            db_obj.permissions = list(perms_result.scalars().all())
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_with_permissions(
        self,
        db: AsyncSession,
        *,
        db_obj: Role,
        obj_in: dict[str, Any],
        permission_ids: list[int] | None = None
    ) -> Role:
        """更新角色及权限"""
        update_data = {k: v for k, v in obj_in.items() if k != "permission_ids" and v is not None}
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        if permission_ids is not None:
            perms_result = await db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            db_obj.permissions = list(perms_result.scalars().all())
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


class CRUDDepartment(CRUDBase[Department]):
    """部门CRUD"""
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Department | None:
        """根据编码获取"""
        result = await db.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_tree(self, db: AsyncSession) -> list[Department]:
        """获取部门树"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Department)
            .where(Department.parent_id == None)
            .order_by(Department.sort_order)
            .options(selectinload(Department.children))
        )
        return list(result.scalars().all())


class CRUDPermission(CRUDBase[Permission]):
    """权限CRUD"""
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Permission | None:
        """根据编码获取"""
        result = await db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_tree(self, db: AsyncSession, type: str | None = None) -> list[Permission]:
        """获取权限树"""
        query = select(Permission).where(Permission.parent_id == None)
        
        if type:
            query = query.where(Permission.type == type)
        
        query = query.order_by(Permission.sort_order)
        result = await db.execute(query)
        return list(result.scalars().all())


# 实例化
user_crud = CRUDUser(User)
role_crud = CRUDRole(Role)
dept_crud = CRUDDepartment(Department)
permission_crud = CRUDPermission(Permission)
