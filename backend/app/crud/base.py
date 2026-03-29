"""
CRUD基础类
"""
from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """CRUD基础类"""
    
    def __init__(self, model: type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """根据ID获取"""
        result = await db.execute(
            select(self.model).where(self.model.id == id, self.model.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_or_404(self, db: AsyncSession, id: int) -> ModelType:
        """根据ID获取，不存在则抛出404"""
        obj = await self.get(db, id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return obj
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
        """获取列表"""
        query = select(self.model).where(self.model.is_deleted == False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    column = getattr(self.model, key)
                    if isinstance(column, InstrumentedAttribute):
                        query = query.where(column == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def count(self, db: AsyncSession, filters: dict[str, Any] | None = None) -> int:
        """获取总数"""
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(self.model.is_deleted == False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    column = getattr(self.model, key)
                    if isinstance(column, InstrumentedAttribute):
                        query = query.where(column == value)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelType:
        """创建"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: dict[str, Any]
    ) -> ModelType:
        """更新"""
        # 过滤掉None值和不可更新字段
        update_data = {
            k: v for k, v in obj_in.items()
            if v is not None and k not in ["id", "created_at", "is_deleted"]
        }
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        """删除（软删除）"""
        obj = await self.get_or_404(db, id)
        obj.is_deleted = True
        db.add(obj)
        await db.flush()
        return obj
    
    async def hard_delete(self, db: AsyncSession, *, id: int) -> None:
        """硬删除"""
        obj = await self.get_or_404(db, id)
        await db.delete(obj)
        await db.flush()
