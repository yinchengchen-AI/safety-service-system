"""
文档管理Schema
"""
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseOutSchema, BaseSchema


# ==================== 文档分类Schema ====================
class DocumentCategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    parent_id: int | None = None
    sort_order: int = 0
    description: str | None = None


class DocumentCategoryCreate(DocumentCategoryBase):
    pass


class DocumentCategoryUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=100)
    code: str | None = Field(None, min_length=1, max_length=50)
    parent_id: int | None = None
    sort_order: int | None = None
    description: str | None = None


class DocumentCategoryOut(DocumentCategoryBase, BaseOutSchema):
    children: list["DocumentCategoryOut"] = []


class DocumentCategorySimpleOut(BaseSchema):
    id: int
    name: str
    code: str


# ==================== 文档Schema ====================
class DocumentBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    type: str = Field(..., pattern="^(contract|report|certificate|training|policy|other)$")
    version: str = Field(default="1.0", max_length=20)
    status: str = Field(default="active", pattern="^(active|archived|disabled)$")
    is_public: bool = False
    allow_download: bool = True


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseSchema):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    type: str | None = Field(None, pattern="^(contract|report|certificate|training|policy|other)$")
    version: str | None = Field(None, max_length=20)
    status: str | None = Field(None, pattern="^(active|archived|disabled)$")
    is_public: bool | None = None
    allow_download: bool | None = None


class DocumentOut(DocumentBase, BaseOutSchema):
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    file_ext: str
    view_count: int
    download_count: int
    uploader_id: int
    category: DocumentCategorySimpleOut | None = None
    uploader: dict | None = None


class DocumentSimpleOut(BaseSchema):
    id: int
    title: str
    file_name: str
    file_ext: str
    file_size: int
    type: str
    status: str
    created_at: datetime


# ==================== 查询参数 ====================
class DocumentQuery(BaseSchema):
    keyword: str | None = None
    category_id: int | None = None
    type: str | None = None
    status: str | None = None
    page: int = 1
    page_size: int = 10


class DocumentCategoryQuery(BaseSchema):
    keyword: str | None = None
