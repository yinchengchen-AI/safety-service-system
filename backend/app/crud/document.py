"""
文档管理CRUD
"""
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.document import Document, DocumentCategory


class CRUDDocument(CRUDBase[Document]):
    """文档CRUD"""

    async def get_with_relations(self, db: AsyncSession, id: int) -> Document | None:
        """获取文档及关联信息"""
        result = await db.execute(
            select(Document)
            .where(Document.id == id, Document.is_deleted == False)
            .options(selectinload(Document.category))
            .options(selectinload(Document.uploader))
        )
        return result.scalar_one_or_none()

    async def get_multi_with_filter(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: str | None = None,
        category_id: int | None = None,
        type: str | None = None,
        status: str | None = None,
    ) -> list[Document]:
        """获取文档列表（带筛选）"""
        query = (
            select(Document)
            .where(Document.is_deleted == False)
            .options(selectinload(Document.category))
            .options(selectinload(Document.uploader))
        )

        if keyword:
            query = query.where(
                (Document.title.ilike(f"%{keyword}%")) |
                (Document.file_name.ilike(f"%{keyword}%"))
            )

        if category_id:
            query = query.where(Document.category_id == category_id)

        if type:
            query = query.where(Document.type == type)

        if status:
            query = query.where(Document.status == status)

        query = query.order_by(Document.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_with_filter(
        self,
        db: AsyncSession,
        *,
        keyword: str | None = None,
        category_id: int | None = None,
        type: str | None = None,
        status: str | None = None,
    ) -> int:
        """统计文档数"""
        query = select(func.count(Document.id)).where(Document.is_deleted == False)

        if keyword:
            query = query.where(
                (Document.title.ilike(f"%{keyword}%")) |
                (Document.file_name.ilike(f"%{keyword}%"))
            )

        if category_id:
            query = query.where(Document.category_id == category_id)

        if type:
            query = query.where(Document.type == type)

        if status:
            query = query.where(Document.status == status)

        result = await db.execute(query)
        return result.scalar() or 0

    async def increment_view_count(self, db: AsyncSession, id: int) -> None:
        """增加浏览次数"""
        result = await db.execute(
            select(Document).where(Document.id == id, Document.is_deleted == False)
        )
        doc = result.scalar_one_or_none()
        if doc:
            doc.view_count += 1
            db.add(doc)
            await db.flush()

    async def increment_download_count(self, db: AsyncSession, id: int) -> None:
        """增加下载次数"""
        result = await db.execute(
            select(Document).where(Document.id == id, Document.is_deleted == False)
        )
        doc = result.scalar_one_or_none()
        if doc:
            doc.download_count += 1
            db.add(doc)
            await db.flush()


class CRUDDocumentCategory(CRUDBase[DocumentCategory]):
    """文档分类CRUD"""

    async def get_by_code(self, db: AsyncSession, code: str) -> DocumentCategory | None:
        """根据编码获取"""
        result = await db.execute(
            select(DocumentCategory).where(DocumentCategory.code == code)
        )
        return result.scalar_one_or_none()

    async def get_tree(self, db: AsyncSession) -> list[DocumentCategory]:
        """获取分类树"""
        result = await db.execute(
            select(DocumentCategory)
            .where(DocumentCategory.parent_id == None)
            .order_by(DocumentCategory.sort_order)
            .options(selectinload(DocumentCategory.children))
        )
        return list(result.scalars().all())

    async def get_all(self, db: AsyncSession) -> list[DocumentCategory]:
        """获取所有分类"""
        result = await db.execute(
            select(DocumentCategory).order_by(DocumentCategory.sort_order)
        )
        return list(result.scalars().all())


# 实例化
document_crud = CRUDDocument(Document)
document_category_crud = CRUDDocumentCategory(DocumentCategory)
