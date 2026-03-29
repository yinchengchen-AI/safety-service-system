"""
附件管理接口
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.core.permissions import PermissionCode
from app.database import get_db
from app.models.attachment import Attachment
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.services.minio_service import minio_service

router = APIRouter()

# 允许的文件类型
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_ext(filename: str) -> str:
    """获取文件扩展名"""
    return filename.split(".")[-1].lower() if "." in filename else ""


@router.get("", response_model=ResponseSchema)
async def list_attachments(
    ref_type: str = Query(None, description="关联类型: contract/invoice"),
    ref_id: int = Query(None, description="关联对象ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取附件列表"""
    query = select(Attachment).options(selectinload(Attachment.uploader))
    
    # 筛选条件
    if ref_type:
        query = query.where(Attachment.ref_type == ref_type)
    if ref_id:
        query = query.where(Attachment.ref_id == ref_id)
    
    # 获取总数
    count_query = select(func.count(Attachment.id))
    if ref_type:
        count_query = count_query.where(Attachment.ref_type == ref_type)
    if ref_id:
        count_query = count_query.where(Attachment.ref_id == ref_id)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Attachment.created_at.desc())
    
    result = await db.execute(query)
    attachments = result.scalars().all()
    
    # 构建响应
    items = []
    for att in attachments:
        items.append({
            "id": att.id,
            "file_name": att.file_name,
            "file_size": att.file_size,
            "file_type": att.file_type,
            "file_ext": att.file_ext,
            "file_path": att.file_path,
            "ref_type": att.ref_type,
            "ref_id": att.ref_id,
            "description": att.description,
            "uploader": {
                "id": att.uploader.id,
                "real_name": att.uploader.real_name,
                "username": att.uploader.username,
            } if att.uploader else None,
            "created_at": att.created_at,
        })
    
    return ResponseSchema(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.post("/upload", response_model=ResponseSchema)
async def upload_attachment(
    file: UploadFile = File(...),
    ref_type: str = Query(..., description="关联类型: contract/invoice"),
    ref_id: int = Query(..., description="关联对象ID"),
    description: str = Query(None, description="文件描述"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传附件
    
    - **file**: 文件内容
    - **ref_type**: 关联类型 (contract/invoice)
    - **ref_id**: 关联对象ID
    - **description**: 文件描述（可选）
    """
    # 验证文件类型
    file_ext = get_file_ext(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 验证 MIME 类型
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {content_type}"
        )
    
    # 读取文件内容
    contents = await file.read()
    file_size = len(contents)
    
    # 验证文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大50MB）"
        )
    
    # 生成存储路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = f"{timestamp}_{unique_id}.{file_ext}"
    object_name = f"{ref_type}s/{ref_id}/{safe_filename}"
    
    # 上传到 MinIO
    from io import BytesIO
    file_path = minio_service.upload_file(
        BytesIO(contents),
        object_name,
        content_type=content_type,
        file_size=file_size
    )
    
    # 保存到数据库
    attachment = Attachment(
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=content_type,
        file_ext=file_ext,
        ref_type=ref_type,
        ref_id=ref_id,
        description=description,
        uploader_id=current_user.id
    )
    db.add(attachment)
    await db.flush()
    await db.refresh(attachment)
    
    # 生成预览 URL
    preview_url = minio_service.get_presigned_url(file_path, expires=3600)
    
    return ResponseSchema(data={
        "id": attachment.id,
        "file_name": attachment.file_name,
        "file_size": attachment.file_size,
        "file_ext": attachment.file_ext,
        "preview_url": preview_url,
    }, message="上传成功")


@router.get("/{attachment_id}/download", response_model=ResponseSchema)
async def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取附件下载链接"""
    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    
    # 生成下载 URL（30分钟有效）
    download_url = minio_service.get_presigned_url(attachment.file_path, expires=1800)
    
    return ResponseSchema(data={
        "download_url": download_url,
        "file_name": attachment.file_name,
    })


@router.get("/{attachment_id}/preview", response_model=ResponseSchema)
async def preview_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取附件预览链接"""
    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    
    # 生成预览 URL（1小时有效）
    preview_url = minio_service.get_presigned_url(attachment.file_path, expires=3600)
    
    return ResponseSchema(data={
        "preview_url": preview_url,
        "file_name": attachment.file_name,
        "file_type": attachment.file_type,
    })


@router.delete("/{attachment_id}", response_model=ResponseSchema)
async def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除附件"""
    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    
    # 权限检查：上传人本人或管理员可以删除
    if attachment.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此附件"
        )
    
    # 从 MinIO 删除文件
    minio_service.delete_file(attachment.file_path)
    
    # 从数据库删除记录
    await db.delete(attachment)
    await db.flush()
    
    return ResponseSchema(message="删除成功")
