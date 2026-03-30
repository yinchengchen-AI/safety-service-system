"""
文档管理接口
"""
import uuid
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions, require_superuser
from app.core.permissions import PermissionCode
from app.crud.document import document_crud, document_category_crud
from app.database import get_db
from app.models.document import Document, DocumentCategory, DocumentType
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.services.minio_service import minio_service

router = APIRouter()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    "pdf", "jpg", "jpeg", "png", "gif",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "zip", "rar"
}
# 最大文件大小 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


def get_file_ext(filename: str) -> str:
    """获取文件扩展名"""
    return filename.split(".")[-1].lower() if "." in filename else ""


def build_document_response(doc: Document) -> dict:
    """构建文档响应数据"""
    return {
        "id": doc.id,
        "title": doc.title,
        "description": doc.description,
        "category_id": doc.category_id,
        "type": doc.type,
        "file_name": doc.file_name,
        "file_path": doc.file_path,
        "file_size": doc.file_size,
        "file_type": doc.file_type,
        "file_ext": doc.file_ext,
        "version": doc.version,
        "status": doc.status,
        "is_public": doc.is_public,
        "allow_download": doc.allow_download,
        "view_count": doc.view_count,
        "download_count": doc.download_count,
        "uploader_id": doc.uploader_id,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "category": {
            "id": doc.category.id,
            "name": doc.category.name,
            "code": doc.category.code,
        } if doc.category else None,
        "uploader": {
            "id": doc.uploader.id,
            "real_name": doc.uploader.real_name,
            "username": doc.uploader.username,
        } if doc.uploader else None,
    }


def build_category_response(cat: DocumentCategory, include_children: bool = True) -> dict:
    """构建分类响应数据"""
    data = {
        "id": cat.id,
        "name": cat.name,
        "code": cat.code,
        "parent_id": cat.parent_id,
        "sort_order": cat.sort_order,
        "description": cat.description,
        "created_at": cat.created_at,
        "updated_at": cat.updated_at,
    }
    if include_children and hasattr(cat, "children"):
        data["children"] = [build_category_response(c, include_children=False) for c in cat.children]
    return data


# ==================== 文档接口 ====================

@router.get("", response_model=ResponseSchema)
async def list_documents(
    keyword: str = Query(None, description="关键词搜索"),
    category_id: int = Query(None, description="分类ID"),
    type: str = Query(None, description="文档类型"),
    status: str = Query(None, description="文档状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    skip = (page - 1) * page_size

    total = await document_crud.count_with_filter(
        db, keyword=keyword, category_id=category_id, type=type, status=status
    )
    documents = await document_crud.get_multi_with_filter(
        db, skip=skip, limit=page_size,
        keyword=keyword, category_id=category_id, type=type, status=status
    )

    return ResponseSchema(data={
        "items": [build_document_response(d) for d in documents],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/{document_id}", response_model=ResponseSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    doc = await document_crud.get_with_relations(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    return ResponseSchema(data=build_document_response(doc))


@router.post("", response_model=ResponseSchema)
async def create_document(
    document_in: dict,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_CREATE])),
    db: AsyncSession = Depends(get_db)
):
    """
    创建文档记录（不上传文件，仅创建元数据）
    """
    # 实际创建文档应通过上传接口完成，此接口保留用于特殊场景
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="请使用上传接口创建文档"
    )


@router.post("/upload", response_model=ResponseSchema)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Query(..., description="文档标题"),
    type: str = Query(..., description="文档类型: contract/report/certificate/training/policy/other"),
    category_id: int = Query(None, description="分类ID"),
    description: str = Query(None, description="文档描述"),
    version: str = Query("1.0", description="版本号"),
    is_public: bool = Query(False, description="是否公开"),
    allow_download: bool = Query(True, description="允许下载"),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_CREATE])),
    db: AsyncSession = Depends(get_db)
):
    """
    上传文档
    """
    # 验证文件类型
    file_ext = get_file_ext(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 读取文件内容
    contents = await file.read()
    file_size = len(contents)

    # 验证文件大小
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制（最大100MB）"
        )

    # 验证分类
    if category_id:
        cat = await document_category_crud.get(db, category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不存在"
            )

    # 生成存储路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = f"{timestamp}_{unique_id}.{file_ext}"
    object_name = f"documents/{type}/{safe_filename}"

    content_type = file.content_type or "application/octet-stream"

    # 上传到 MinIO
    file_path = minio_service.upload_file(
        BytesIO(contents),
        object_name,
        content_type=content_type,
        file_size=file_size
    )

    # 保存到数据库
    document = Document(
        title=title,
        description=description,
        category_id=category_id,
        type=type,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=content_type,
        file_ext=file_ext,
        version=version,
        status="active",
        is_public=is_public,
        allow_download=allow_download,
        uploader_id=current_user.id
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    # 生成预览 URL
    preview_url = minio_service.get_presigned_url(file_path, expires=3600)

    return ResponseSchema(data={
        "id": document.id,
        "title": document.title,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "file_ext": document.file_ext,
        "preview_url": preview_url,
    }, message="上传成功")


@router.put("/{document_id}", response_model=ResponseSchema)
async def update_document(
    document_id: int,
    title: str = Query(None, description="文档标题"),
    description: str = Query(None, description="文档描述"),
    category_id: int = Query(None, description="分类ID"),
    type: str = Query(None, description="文档类型"),
    version: str = Query(None, description="版本号"),
    status: str = Query(None, description="文档状态"),
    is_public: bool = Query(None, description="是否公开"),
    allow_download: bool = Query(None, description="允许下载"),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """更新文档信息"""
    doc = await document_crud.get(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 权限检查：上传人本人或管理员可以修改
    if doc.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此文档"
        )

    # 验证分类
    if category_id is not None:
        cat = await document_category_crud.get(db, category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不存在"
            )

    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if category_id is not None:
        update_data["category_id"] = category_id
    if type is not None:
        update_data["type"] = type
    if version is not None:
        update_data["version"] = version
    if status is not None:
        update_data["status"] = status
    if is_public is not None:
        update_data["is_public"] = is_public
    if allow_download is not None:
        update_data["allow_download"] = allow_download

    doc = await document_crud.update(db, db_obj=doc, obj_in=update_data)
    await db.refresh(doc, attribute_names=["category", "uploader"])
    return ResponseSchema(data=build_document_response(doc), message="更新成功")


@router.delete("/{document_id}", response_model=ResponseSchema)
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_DELETE])),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    doc = await document_crud.get(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 权限检查：上传人本人或管理员可以删除
    if doc.uploader_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此文档"
        )

    # 从 MinIO 删除文件
    minio_service.delete_file(doc.file_path)

    # 软删除
    await document_crud.delete(db, id=document_id)

    return ResponseSchema(message="删除成功")


@router.get("/{document_id}/download", response_model=ResponseSchema)
async def download_document(
    document_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档下载链接"""
    doc = await document_crud.get(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    if not doc.allow_download:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该文档不允许下载"
        )

    # 增加下载次数
    await document_crud.increment_download_count(db, document_id)

    # 生成下载 URL（30分钟有效）
    download_url = minio_service.get_presigned_url(doc.file_path, expires=1800)

    return ResponseSchema(data={
        "download_url": download_url,
        "file_name": doc.file_name,
    })


@router.get("/{document_id}/preview", response_model=ResponseSchema)
async def preview_document(
    document_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档预览链接"""
    doc = await document_crud.get(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 增加浏览次数
    await document_crud.increment_view_count(db, document_id)

    # 生成预览 URL（1小时有效）
    preview_url = minio_service.get_presigned_url(doc.file_path, expires=3600)

    return ResponseSchema(data={
        "preview_url": preview_url,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
    })


# ==================== 文档分类接口 ====================

@router.get("/categories", response_model=ResponseSchema)
async def list_categories(
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档分类列表"""
    categories = await document_category_crud.get_all(db)
    return ResponseSchema(data=[
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "parent_id": c.parent_id,
            "sort_order": c.sort_order,
            "description": c.description,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in categories
    ])


@router.get("/categories/tree", response_model=ResponseSchema)
async def get_category_tree(
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取文档分类树"""
    categories = await document_category_crud.get_tree(db)
    return ResponseSchema(data=[build_category_response(c) for c in categories])


@router.post("/categories", response_model=ResponseSchema)
async def create_category(
    name: str = Query(..., description="分类名称"),
    code: str = Query(..., description="分类编码"),
    parent_id: int = Query(None, description="父分类ID"),
    sort_order: int = Query(0, description="排序"),
    description: str = Query(None, description="描述"),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_CREATE])),
    db: AsyncSession = Depends(get_db)
):
    """创建文档分类"""
    # 检查编码是否已存在
    existing = await document_category_crud.get_by_code(db, code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类编码已存在"
        )

    category = await document_category_crud.create(db, obj_in={
        "name": name,
        "code": code,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "description": description,
    })

    return ResponseSchema(data={
        "id": category.id,
        "name": category.name,
        "code": category.code,
    }, message="创建成功")


@router.put("/categories/{category_id}", response_model=ResponseSchema)
async def update_category(
    category_id: int,
    name: str = Query(None, description="分类名称"),
    code: str = Query(None, description="分类编码"),
    parent_id: int = Query(None, description="父分类ID"),
    sort_order: int = Query(None, description="排序"),
    description: str = Query(None, description="描述"),
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """更新文档分类"""
    category = await document_category_crud.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    # 检查编码是否冲突
    if code is not None and code != category.code:
        existing = await document_category_crud.get_by_code(db, code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类编码已存在"
            )

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if code is not None:
        update_data["code"] = code
    if parent_id is not None:
        update_data["parent_id"] = parent_id
    if sort_order is not None:
        update_data["sort_order"] = sort_order
    if description is not None:
        update_data["description"] = description

    category = await document_category_crud.update(db, db_obj=category, obj_in=update_data)
    return ResponseSchema(data={
        "id": category.id,
        "name": category.name,
        "code": category.code,
    }, message="更新成功")


@router.delete("/categories/{category_id}", response_model=ResponseSchema)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.DOCUMENT_DELETE])),
    db: AsyncSession = Depends(get_db)
):
    """删除文档分类"""
    category = await document_category_crud.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    # 检查是否有子分类
    result = await db.execute(
        select(func.count(DocumentCategory.id)).where(DocumentCategory.parent_id == category_id)
    )
    child_count = result.scalar() or 0
    if child_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下存在子分类，无法删除"
        )

    # 检查是否有关联文档
    result = await db.execute(
        select(func.count(Document.id)).where(
            Document.category_id == category_id,
            Document.is_deleted == False
        )
    )
    doc_count = result.scalar() or 0
    if doc_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下存在文档，无法删除"
        )

    await document_category_crud.hard_delete(db, id=category_id)
    return ResponseSchema(message="删除成功")
