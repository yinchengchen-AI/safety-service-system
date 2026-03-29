"""
附件相关 Schema
"""
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseOutSchema, BaseSchema


class AttachmentBase(BaseSchema):
    """附件基础"""
    file_name: str
    file_size: int
    file_type: str
    file_ext: str
    description: str | None = None


class AttachmentCreate(BaseSchema):
    """创建附件（内部使用）"""
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    file_ext: str
    ref_type: str
    ref_id: int
    description: str | None = None


class AttachmentOut(AttachmentBase, BaseOutSchema):
    """附件输出"""
    file_path: str
    ref_type: str
    ref_id: int
    uploader: dict | None = None
    
    
class AttachmentListParams(BaseSchema):
    """附件列表查询参数"""
    ref_type: str | None = None
    ref_id: int | None = None
    page: int = 1
    page_size: int = 20


class AttachmentUploadResponse(BaseSchema):
    """上传响应"""
    id: int
    file_name: str
    file_size: int
    file_ext: str
    preview_url: str | None = None
