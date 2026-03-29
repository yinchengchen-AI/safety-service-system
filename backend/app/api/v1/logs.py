"""
日志管理接口 - 操作日志、登录日志
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.core.permissions import PermissionCode
from app.database import get_db
from app.models.system import OperationLog, LoginLog, LogType
from app.models.user import User
from app.schemas.base import ResponseSchema

router = APIRouter()


@router.get("/operation", response_model=ResponseSchema)
async def list_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="操作人用户名"),
    module: Optional[str] = Query(None, description="操作模块"),
    log_type: Optional[str] = Query(None, description="操作类型: create/update/delete/query"),
    status: Optional[str] = Query(None, description="操作状态: success/fail"),
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    current_user: User = Depends(require_permissions([PermissionCode.LOG_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志列表"""
    # 构建查询条件
    conditions = []
    
    if username:
        conditions.append(OperationLog.username.ilike(f"%{username}%"))
    if module:
        conditions.append(OperationLog.module == module)
    if log_type:
        conditions.append(OperationLog.log_type == log_type)
    if status:
        conditions.append(OperationLog.status == status)
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d")
            conditions.append(OperationLog.operation_time >= start_dt)
        except ValueError:
            pass
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(OperationLog.operation_time < end_dt)
        except ValueError:
            pass
    
    # 构建查询
    query = select(OperationLog)
    count_query = select(func.count(OperationLog.id))
    
    if conditions:
        where_clause = and_(*conditions)
        query = query.where(where_clause)
        count_query = count_query.where(where_clause)
    
    # 获取总数
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.order_by(OperationLog.operation_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # 构建响应
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "real_name": log.real_name,
            "log_type": log.log_type,
            "module": log.module,
            "action": log.action,
            "description": log.description,
            "request_method": log.request_method,
            "request_url": log.request_url,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "execution_time": log.execution_time,
            "status": log.status,
            "error_msg": log.error_msg,
            "operation_time": log.operation_time.isoformat() if log.operation_time else None,
        })
    
    return ResponseSchema(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/operation/{log_id}", response_model=ResponseSchema)
async def get_operation_log_detail(
    log_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.LOG_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志详情"""
    result = await db.execute(
        select(OperationLog).where(OperationLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    
    return ResponseSchema(data={
        "id": log.id,
        "user_id": log.user_id,
        "username": log.username,
        "real_name": log.real_name,
        "log_type": log.log_type,
        "module": log.module,
        "action": log.action,
        "description": log.description,
        "request_method": log.request_method,
        "request_url": log.request_url,
        "request_params": log.request_params,
        "response_data": log.response_data,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "execution_time": log.execution_time,
        "status": log.status,
        "error_msg": log.error_msg,
        "operation_time": log.operation_time.isoformat() if log.operation_time else None,
    })


@router.delete("/operation/{log_id}", response_model=ResponseSchema)
async def delete_operation_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除单条操作日志（仅超级管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅超级管理员可删除日志"
        )
    
    result = await db.execute(
        select(OperationLog).where(OperationLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    
    await db.delete(log)
    await db.flush()
    
    return ResponseSchema(message="删除成功")


@router.delete("/operation", response_model=ResponseSchema)
async def batch_delete_operation_logs(
    ids: list[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批量删除操作日志（仅超级管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅超级管理员可删除日志"
        )
    
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要删除的日志"
        )
    
    result = await db.execute(
        select(OperationLog).where(OperationLog.id.in_(ids))
    )
    logs = result.scalars().all()
    
    for log in logs:
        await db.delete(log)
    
    await db.flush()
    
    return ResponseSchema(message=f"成功删除 {len(logs)} 条日志")


@router.get("/login", response_model=ResponseSchema)
async def list_login_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    login_status: Optional[str] = Query(None, description="登录状态: success/fail"),
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    current_user: User = Depends(require_permissions([PermissionCode.LOG_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取登录日志列表"""
    # 构建查询条件
    conditions = []
    
    if username:
        conditions.append(LoginLog.username.ilike(f"%{username}%"))
    if login_status:
        conditions.append(LoginLog.login_status == login_status)
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d")
            conditions.append(LoginLog.login_time >= start_dt)
        except ValueError:
            pass
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(LoginLog.login_time < end_dt)
        except ValueError:
            pass
    
    # 构建查询
    query = select(LoginLog)
    count_query = select(func.count(LoginLog.id))
    
    if conditions:
        where_clause = and_(*conditions)
        query = query.where(where_clause)
        count_query = count_query.where(where_clause)
    
    # 获取总数
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.order_by(LoginLog.login_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # 构建响应
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "real_name": log.real_name,
            "login_type": log.login_type,
            "login_status": log.login_status,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "browser": log.browser,
            "os": log.os,
            "device": log.device,
            "fail_reason": log.fail_reason,
            "login_time": log.login_time.isoformat() if log.login_time else None,
        })
    
    return ResponseSchema(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/modules", response_model=ResponseSchema)
async def get_log_modules(
    current_user: User = Depends(require_permissions([PermissionCode.LOG_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取所有操作模块列表（用于筛选下拉框）"""
    result = await db.execute(
        select(OperationLog.module).distinct().where(OperationLog.module.isnot(None))
    )
    modules = [m for m in result.scalars().all() if m]
    
    return ResponseSchema(data=modules)
