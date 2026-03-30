"""
通知公告接口
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.core.permissions import PermissionCode
from app.database import get_db
from app.models.notice import Notice, NoticeReadStatus, NoticeStatus, NoticeType
from app.models.user import User
from app.schemas.base import ResponseSchema

router = APIRouter()


def build_notice_response(notice: Notice, read_status: Optional[NoticeReadStatus] = None) -> dict:
    """构建公告响应数据"""
    data = {
        "id": notice.id,
        "title": notice.title,
        "content": notice.content,
        "summary": notice.summary,
        "type": notice.type,
        "status": notice.status,
        "publish_time": notice.publish_time,
        "expire_time": notice.expire_time,
        "is_top": notice.is_top,
        "top_expire_time": notice.top_expire_time,
        "attachment": notice.attachment,
        "view_count": notice.view_count,
        "publisher_id": notice.publisher_id,
        "created_at": notice.created_at,
        "updated_at": notice.updated_at,
        "publisher": {
            "id": notice.publisher.id,
            "real_name": notice.publisher.real_name,
            "username": notice.publisher.username,
        } if notice.publisher else None,
    }
    
    if read_status:
        data["is_read"] = read_status.is_read
        data["read_time"] = read_status.read_time
    
    return data


def get_notice_type_name(type_value: str) -> str:
    """获取公告类型名称"""
    type_names = {
        NoticeType.NORMAL: "普通公告",
        NoticeType.IMPORTANT: "重要公告",
        NoticeType.URGENT: "紧急公告",
    }
    return type_names.get(type_value, "未知")


def get_notice_status_name(status_value: str) -> str:
    """获取公告状态名称"""
    status_names = {
        NoticeStatus.DRAFT: "草稿",
        NoticeStatus.PUBLISHED: "已发布",
        NoticeStatus.WITHDRAWN: "已撤回",
        NoticeStatus.ARCHIVED: "已归档",
    }
    return status_names.get(status_value, "未知")


# ==================== 公告管理接口 ====================

@router.get("", response_model=ResponseSchema)
async def list_notices(
    keyword: str = Query(None, description="关键词搜索"),
    type: str = Query(None, description="公告类型"),
    status: str = Query(None, description="公告状态"),
    is_top: bool = Query(None, description="是否置顶"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_permissions([PermissionCode.NOTICE_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取公告列表（管理后台）"""
    skip = (page - 1) * page_size
    
    # 构建查询条件
    conditions = []
    if keyword:
        conditions.append(
            or_(
                Notice.title.contains(keyword),
                Notice.summary.contains(keyword)
            )
        )
    if type:
        conditions.append(Notice.type == type)
    if status:
        conditions.append(Notice.status == status)
    if is_top is not None:
        conditions.append(Notice.is_top == is_top)
    
    # 统计总数
    count_query = select(func.count(Notice.id)).where(
        Notice.is_deleted == False,
        *conditions
    )
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # 查询列表
    query = select(Notice).where(
        Notice.is_deleted == False,
        *conditions
    ).order_by(
        desc(Notice.is_top),  # 置顶优先
        desc(Notice.publish_time),  # 发布时间倒序
        desc(Notice.created_at)
    ).offset(skip).limit(page_size)
    
    result = await db.execute(query)
    notices = result.scalars().all()
    
    # 加载发布人信息
    for notice in notices:
        await db.refresh(notice, attribute_names=["publisher"])
    
    return ResponseSchema(data={
        "items": [build_notice_response(n) for n in notices],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/published", response_model=ResponseSchema)
async def list_published_notices(
    keyword: str = Query(None, description="关键词搜索"),
    type: str = Query(None, description="公告类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取已发布的公告列表（普通用户查看）"""
    skip = (page - 1) * page_size
    now = datetime.now()
    
    # 构建查询条件
    conditions = [Notice.status == NoticeStatus.PUBLISHED]
    
    if keyword:
        conditions.append(
            or_(
                Notice.title.contains(keyword),
                Notice.summary.contains(keyword)
            )
        )
    if type:
        conditions.append(Notice.type == type)
    
    # 统计总数（只统计未过期的）
    count_query = select(func.count(Notice.id)).where(
        Notice.is_deleted == False,
        *conditions,
        or_(
            Notice.expire_time == None,
            Notice.expire_time > now
        )
    )
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # 查询列表
    query = select(Notice).where(
        Notice.is_deleted == False,
        *conditions,
        or_(
            Notice.expire_time == None,
            Notice.expire_time > now
        )
    ).order_by(
        desc(Notice.is_top),
        desc(Notice.publish_time)
    ).offset(skip).limit(page_size)
    
    result = await db.execute(query)
    notices = result.scalars().all()
    
    # 加载发布人信息和阅读状态
    for notice in notices:
        await db.refresh(notice, attribute_names=["publisher"])
        
        # 查询当前用户的阅读状态
        read_result = await db.execute(
            select(NoticeReadStatus).where(
                NoticeReadStatus.notice_id == notice.id,
                NoticeReadStatus.user_id == current_user.id
            )
        )
        read_status = read_result.scalar_one_or_none()
    
    return ResponseSchema(data={
        "items": [build_notice_response(n, read_status) for n in notices],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/my", response_model=ResponseSchema)
async def list_my_notices(
    is_read: bool = Query(None, description="是否已读"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的公告列表（包含阅读状态）"""
    skip = (page - 1) * page_size
    now = datetime.now()
    
    # 构建查询条件
    conditions = [Notice.status == NoticeStatus.PUBLISHED]
    
    # 统计总数
    count_query = select(func.count(Notice.id)).where(
        Notice.is_deleted == False,
        *conditions,
        or_(
            Notice.expire_time == None,
            Notice.expire_time > now
        )
    )
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # 查询列表
    query = select(Notice).where(
        Notice.is_deleted == False,
        *conditions,
        or_(
            Notice.expire_time == None,
            Notice.expire_time > now
        )
    ).order_by(
        desc(Notice.is_top),
        desc(Notice.publish_time)
    ).offset(skip).limit(page_size)
    
    result = await db.execute(query)
    notices = result.scalars().all()
    
    # 加载阅读状态
    items = []
    for notice in notices:
        await db.refresh(notice, attribute_names=["publisher"])
        
        # 查询阅读状态
        read_result = await db.execute(
            select(NoticeReadStatus).where(
                NoticeReadStatus.notice_id == notice.id,
                NoticeReadStatus.user_id == current_user.id
            )
        )
        read_status = read_result.scalar_one_or_none()
        
        # 筛选已读/未读
        if is_read is not None:
            notice_is_read = read_status.is_read if read_status else False
            if notice_is_read != is_read:
                continue
        
        items.append(build_notice_response(notice, read_status))
    
    return ResponseSchema(data={
        "items": items,
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "pages": (len(items) + page_size - 1) // page_size
    })


@router.get("/unread-count", response_model=ResponseSchema)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取未读公告数量"""
    now = datetime.now()
    
    # 查询已发布的有效公告ID
    notice_query = select(Notice.id).where(
        Notice.is_deleted == False,
        Notice.status == NoticeStatus.PUBLISHED,
        or_(
            Notice.expire_time == None,
            Notice.expire_time > now
        )
    )
    result = await db.execute(notice_query)
    notice_ids = [r for r in result.scalars().all()]
    
    if not notice_ids:
        return ResponseSchema(data={"unread_count": 0, "total": 0})
    
    # 查询已读数量
    read_query = select(func.count(NoticeReadStatus.id)).where(
        NoticeReadStatus.notice_id.in_(notice_ids),
        NoticeReadStatus.user_id == current_user.id,
        NoticeReadStatus.is_read == True
    )
    result = await db.execute(read_query)
    read_count = result.scalar() or 0
    
    total = len(notice_ids)
    unread_count = total - read_count
    
    return ResponseSchema(data={
        "unread_count": unread_count,
        "total": total
    })


@router.get("/{notice_id}", response_model=ResponseSchema)
async def get_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取公告详情"""
    query = select(Notice).where(
        Notice.id == notice_id,
        Notice.is_deleted == False
    )
    result = await db.execute(query)
    notice = result.scalar_one_or_none()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )
    
    # 检查权限：草稿状态只有管理员或发布人可以查看
    if notice.status == NoticeStatus.DRAFT:
        if not current_user.is_superuser and notice.publisher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此公告"
            )
    
    await db.refresh(notice, attribute_names=["publisher"])
    
    # 查询阅读状态
    read_result = await db.execute(
        select(NoticeReadStatus).where(
            NoticeReadStatus.notice_id == notice.id,
            NoticeReadStatus.user_id == current_user.id
        )
    )
    read_status = read_result.scalar_one_or_none()
    
    # 增加浏览次数
    notice.view_count += 1
    await db.flush()
    
    # 自动标记为已读
    if not read_status:
        read_status = NoticeReadStatus(
            notice_id=notice_id,
            user_id=current_user.id,
            is_read=True,
            read_time=datetime.now()
        )
        db.add(read_status)
        await db.flush()
    elif not read_status.is_read:
        read_status.is_read = True
        read_status.read_time = datetime.now()
        await db.flush()
    
    return ResponseSchema(data=build_notice_response(notice, read_status))


@router.post("", response_model=ResponseSchema)
async def create_notice(
    notice_in: dict,
    current_user: User = Depends(require_permissions([PermissionCode.NOTICE_CREATE])),
    db: AsyncSession = Depends(get_db)
):
    """创建公告"""
    # 提取参数
    title = notice_in.get("title")
    content = notice_in.get("content")
    summary = notice_in.get("summary")
    notice_type = notice_in.get("type", NoticeType.NORMAL)
    status = notice_in.get("status", NoticeStatus.DRAFT)
    expire_time = notice_in.get("expire_time")
    is_top = notice_in.get("is_top", False)
    top_expire_time = notice_in.get("top_expire_time")
    attachment = notice_in.get("attachment")
    
    # 验证必填字段
    if not title or not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标题和内容不能为空"
        )
    
    # 如果直接发布，设置发布时间
    publish_time = None
    if status == NoticeStatus.PUBLISHED:
        publish_time = datetime.now()
    
    # 创建公告
    notice = Notice(
        title=title,
        content=content,
        summary=summary,
        type=notice_type,
        status=status,
        publish_time=publish_time,
        expire_time=expire_time,
        is_top=is_top,
        top_expire_time=top_expire_time,
        attachment=attachment,
        publisher_id=current_user.id
    )
    db.add(notice)
    await db.flush()
    await db.refresh(notice, attribute_names=["publisher"])
    
    return ResponseSchema(
        data=build_notice_response(notice),
        message="创建成功"
    )


@router.put("/{notice_id}", response_model=ResponseSchema)
async def update_notice(
    notice_id: int,
    notice_in: dict,
    current_user: User = Depends(require_permissions([PermissionCode.NOTICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """更新公告"""
    query = select(Notice).where(
        Notice.id == notice_id,
        Notice.is_deleted == False
    )
    result = await db.execute(query)
    notice = result.scalar_one_or_none()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )
    
    # 权限检查：只有发布人或管理员可以修改
    if not current_user.is_superuser and notice.publisher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此公告"
        )
    
    # 已归档的公告不能修改
    if notice.status == NoticeStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已归档的公告不能修改"
        )
    
    # 更新字段
    if "title" in notice_in:
        notice.title = notice_in["title"]
    if "content" in notice_in:
        notice.content = notice_in["content"]
    if "summary" in notice_in:
        notice.summary = notice_in["summary"]
    if "type" in notice_in:
        notice.type = notice_in["type"]
    if "expire_time" in notice_in:
        notice.expire_time = notice_in["expire_time"]
    if "is_top" in notice_in:
        notice.is_top = notice_in["is_top"]
    if "top_expire_time" in notice_in:
        notice.top_expire_time = notice_in["top_expire_time"]
    if "attachment" in notice_in:
        notice.attachment = notice_in["attachment"]
    
    # 状态变更
    if "status" in notice_in:
        new_status = notice_in["status"]
        
        # 草稿 -> 发布
        if notice.status == NoticeStatus.DRAFT and new_status == NoticeStatus.PUBLISHED:
            notice.status = NoticeStatus.PUBLISHED
            notice.publish_time = datetime.now()
        # 发布 -> 撤回
        elif notice.status == NoticeStatus.PUBLISHED and new_status == NoticeStatus.WITHDRAWN:
            notice.status = NoticeStatus.WITHDRAWN
        # 撤回 -> 发布
        elif notice.status == NoticeStatus.WITHDRAWN and new_status == NoticeStatus.PUBLISHED:
            notice.status = NoticeStatus.PUBLISHED
            if not notice.publish_time:
                notice.publish_time = datetime.now()
        else:
            notice.status = new_status
    
    await db.flush()
    await db.refresh(notice, attribute_names=["publisher"])
    
    return ResponseSchema(
        data=build_notice_response(notice),
        message="更新成功"
    )


@router.delete("/{notice_id}", response_model=ResponseSchema)
async def delete_notice(
    notice_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.NOTICE_DELETE])),
    db: AsyncSession = Depends(get_db)
):
    """删除公告"""
    query = select(Notice).where(
        Notice.id == notice_id,
        Notice.is_deleted == False
    )
    result = await db.execute(query)
    notice = result.scalar_one_or_none()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )
    
    # 权限检查：只有发布人或管理员可以删除
    if not current_user.is_superuser and notice.publisher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此公告"
        )
    
    # 软删除
    notice.is_deleted = True
    await db.flush()
    
    return ResponseSchema(message="删除成功")


@router.post("/{notice_id}/read", response_model=ResponseSchema)
async def mark_notice_read(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记公告为已读"""
    # 查询公告
    query = select(Notice).where(
        Notice.id == notice_id,
        Notice.is_deleted == False,
        Notice.status == NoticeStatus.PUBLISHED
    )
    result = await db.execute(query)
    notice = result.scalar_one_or_none()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )
    
    # 查询阅读状态
    read_result = await db.execute(
        select(NoticeReadStatus).where(
            NoticeReadStatus.notice_id == notice_id,
            NoticeReadStatus.user_id == current_user.id
        )
    )
    read_status = read_result.scalar_one_or_none()
    
    if read_status:
        if not read_status.is_read:
            read_status.is_read = True
            read_status.read_time = datetime.now()
            await db.flush()
    else:
        read_status = NoticeReadStatus(
            notice_id=notice_id,
            user_id=current_user.id,
            is_read=True,
            read_time=datetime.now()
        )
        db.add(read_status)
        await db.flush()
    
    return ResponseSchema(message="标记已读成功")


@router.get("/{notice_id}/read-stats", response_model=ResponseSchema)
async def get_notice_read_stats(
    notice_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.NOTICE_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取公告阅读统计"""
    # 查询公告
    query = select(Notice).where(
        Notice.id == notice_id,
        Notice.is_deleted == False
    )
    result = await db.execute(query)
    notice = result.scalar_one_or_none()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公告不存在"
        )
    
    # 统计阅读情况
    read_result = await db.execute(
        select(func.count(NoticeReadStatus.id)).where(
            NoticeReadStatus.notice_id == notice_id,
            NoticeReadStatus.is_read == True
        )
    )
    read_count = read_result.scalar() or 0
    
    # 查询用户总数
    from app.models.user import User
    user_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    total_users = user_result.scalar() or 0
    
    unread_count = total_users - read_count
    
    return ResponseSchema(data={
        "notice_id": notice_id,
        "title": notice.title,
        "total_users": total_users,
        "read_count": read_count,
        "unread_count": unread_count,
        "read_rate": round(read_count / total_users * 100, 2) if total_users > 0 else 0
    })

