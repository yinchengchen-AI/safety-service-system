"""
服务管理接口
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.core.permissions import PermissionCode
from app.database import get_db
from app.models.contract import Contract, ContractStatus
from app.models.service import Service, ServiceSchedule, ServiceRecord, ServiceReport, ServiceStatus
from app.models.user import User
from app.schemas.base import ResponseSchema

router = APIRouter()


def build_service_response(service: Service) -> dict:
    """构建服务响应数据"""
    return {
        "id": service.id,
        "code": service.code,
        "name": service.name,
        "type": service.type,
        "contract_id": service.contract_id,
        "planned_start_date": service.planned_start_date.isoformat() if service.planned_start_date else None,
        "planned_end_date": service.planned_end_date.isoformat() if service.planned_end_date else None,
        "actual_start_date": service.actual_start_date.isoformat() if service.actual_start_date else None,
        "actual_end_date": service.actual_end_date.isoformat() if service.actual_end_date else None,
        "status": service.status,
        "description": service.description,
        "requirements": service.requirements,
        "deliverables": service.deliverables,
        "manager_id": service.manager_id,
        "remark": service.remark,
        "created_at": service.created_at.isoformat() if service.created_at else None,
        "updated_at": service.updated_at.isoformat() if service.updated_at else None,
        "contract": {
            "id": service.contract.id,
            "name": service.contract.name,
            "code": service.contract.code,
        } if service.contract else None,
        "manager": {
            "id": service.manager.id,
            "real_name": service.manager.real_name,
        } if service.manager else None,
    }


# ==================== 服务管理 ====================

@router.get("", response_model=ResponseSchema)
async def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    contract_id: Optional[int] = None,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取服务列表"""
    query = select(Service).options(
        selectinload(Service.contract),
        selectinload(Service.manager)
    )
    
    if keyword:
        query = query.where(
            (Service.name.ilike(f"%{keyword}%")) |
            (Service.code.ilike(f"%{keyword}%"))
        )
    
    if status:
        query = query.where(Service.status == status)
    
    if contract_id:
        query = query.where(Service.contract_id == contract_id)
    
    # 获取总数
    count_query = select(func.count(Service.id))
    if keyword:
        count_query = count_query.where(
            (Service.name.ilike(f"%{keyword}%")) |
            (Service.code.ilike(f"%{keyword}%"))
        )
    if status:
        count_query = count_query.where(Service.status == status)
    if contract_id:
        count_query = count_query.where(Service.contract_id == contract_id)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Service.created_at.desc())
    
    result = await db.execute(query)
    services = result.scalars().all()
    
    return ResponseSchema(data={
        "items": [build_service_response(s) for s in services],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{service_id}", response_model=ResponseSchema)
async def get_service(
    service_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取服务详情"""
    result = await db.execute(
        select(Service)
        .where(Service.id == service_id)
        .options(
            selectinload(Service.contract),
            selectinload(Service.manager),
            selectinload(Service.schedules),
            selectinload(Service.records),
            selectinload(Service.reports)
        )
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    data = build_service_response(service)
    data["schedules"] = [
        {
            "id": s.id,
            "title": s.title,
            "scheduled_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
            "status": s.status,
        }
        for s in service.schedules
    ]
    data["records"] = [
        {
            "id": r.id,
            "title": r.title,
            "record_date": r.record_date.isoformat() if r.record_date else None,
        }
        for r in service.records
    ]
    data["reports"] = [
        {
            "id": r.id,
            "code": r.code,
            "title": r.title,
            "status": r.status,
        }
        for r in service.reports
    ]
    
    return ResponseSchema(data=data)


@router.post("", response_model=ResponseSchema)
async def create_service(
    data: dict,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_CREATE])),
    db: AsyncSession = Depends(get_db)
):
    """创建服务"""
    contract_id = data.get("contract_id")
    
    # 检查合同是否存在
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
    
    # 检查合同状态是否允许创建服务
    if contract.status not in [ContractStatus.SIGNED, ContractStatus.EXECUTING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"合同状态为{contract.status}，无法创建服务"
        )
    
    # 生成服务编号
    result = await db.execute(select(func.count(Service.id)))
    count = result.scalar()
    code = f"FW{count + 1:06d}"
    
    service_data = {
        "code": code,
        "name": data.get("name"),
        "type": data.get("type", "on_site"),
        "contract_id": contract_id,
        "planned_start_date": data.get("planned_start_date"),
        "planned_end_date": data.get("planned_end_date"),
        "description": data.get("description"),
        "requirements": data.get("requirements"),
        "deliverables": data.get("deliverables"),
        "manager_id": data.get("manager_id"),
        "remark": data.get("remark"),
        "status": ServiceStatus.PLANNED,
    }
    
    service = Service(**service_data)
    db.add(service)
    
    # 如果合同状态是signed，更新为executing
    if contract.status == ContractStatus.SIGNED:
        contract.status = ContractStatus.EXECUTING
    
    await db.flush()
    await db.refresh(service)
    
    return ResponseSchema(data=build_service_response(service), message="创建成功")


@router.put("/{service_id}", response_model=ResponseSchema)
async def update_service(
    service_id: int,
    data: dict,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """更新服务"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    # 已取消和已完成的服务不能修改
    if service.status in [ServiceStatus.COMPLETED, ServiceStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已完成或已取消的服务不能修改"
        )
    
    for key, value in data.items():
        if hasattr(service, key) and key != "id":
            setattr(service, key, value)
    
    await db.flush()
    await db.refresh(service)
    
    return ResponseSchema(data=build_service_response(service), message="更新成功")


@router.delete("/{service_id}", response_model=ResponseSchema)
async def delete_service(
    service_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_DELETE])),
    db: AsyncSession = Depends(get_db)
):
    """删除服务"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    await db.delete(service)
    await db.flush()
    
    return ResponseSchema(message="删除成功")


# ==================== 状态管理 ====================

@router.post("/{service_id}/start", response_model=ResponseSchema)
async def start_service(
    service_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """开始服务（planned/scheduled -> in_progress）"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    if service.status not in [ServiceStatus.PLANNED, ServiceStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态{service.status}不能开始服务"
        )
    
    service.status = ServiceStatus.IN_PROGRESS
    service.actual_start_date = date.today()
    
    await db.flush()
    await db.refresh(service)
    
    return ResponseSchema(data=build_service_response(service), message="服务已开始")


@router.post("/{service_id}/complete", response_model=ResponseSchema)
async def complete_service(
    service_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """完成服务（in_progress -> completed）"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    if service.status != ServiceStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态{service.status}不能完成服务"
        )
    
    service.status = ServiceStatus.COMPLETED
    service.actual_end_date = date.today()
    
    await db.flush()
    await db.refresh(service)
    
    # 检查合同下所有服务是否都已完成
    await check_and_update_contract_status(db, service.contract_id)
    
    return ResponseSchema(data=build_service_response(service), message="服务已完成")


@router.post("/{service_id}/cancel", response_model=ResponseSchema)
async def cancel_service(
    service_id: int,
    data: dict = None,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """取消服务"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    if service.status == ServiceStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已完成的服务不能取消"
        )
    
    service.status = ServiceStatus.CANCELLED
    
    await db.flush()
    await db.refresh(service)
    
    return ResponseSchema(data=build_service_response(service), message="服务已取消")


async def check_and_update_contract_status(db: AsyncSession, contract_id: int):
    """检查并更新合同状态 - 当所有服务都完成时，合同自动变为completed"""
    # 获取合同
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract or contract.status != ContractStatus.EXECUTING:
        return
    
    # 获取合同下所有未取消的服务
    result = await db.execute(
        select(Service).where(
            Service.contract_id == contract_id,
            Service.status != ServiceStatus.CANCELLED
        )
    )
    services = result.scalars().all()
    
    if not services:
        return
    
    # 如果所有服务都已完成，合同自动变为completed
    all_completed = all(s.status == ServiceStatus.COMPLETED for s in services)
    if all_completed:
        contract.status = ContractStatus.COMPLETED
        await db.flush()


# ==================== 服务排期 ====================

@router.get("/{service_id}/schedules", response_model=ResponseSchema)
async def list_service_schedules(
    service_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_VIEW])),
    db: AsyncSession = Depends(get_db)
):
    """获取服务排期列表"""
    result = await db.execute(
        select(ServiceSchedule)
        .where(ServiceSchedule.service_id == service_id)
        .options(selectinload(ServiceSchedule.staff))
    )
    schedules = result.scalars().all()
    
    return ResponseSchema(data=[
        {
            "id": s.id,
            "title": s.title,
            "scheduled_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
            "scheduled_time": s.scheduled_time,
            "duration": s.duration,
            "status": s.status,
            "staff": {
                "id": s.staff.id,
                "real_name": s.staff.real_name,
            } if s.staff else None,
        }
        for s in schedules
    ])


@router.post("/{service_id}/schedules", response_model=ResponseSchema)
async def create_service_schedule(
    service_id: int,
    data: dict,
    current_user: User = Depends(require_permissions([PermissionCode.SERVICE_UPDATE])),
    db: AsyncSession = Depends(get_db)
):
    """创建服务排期"""
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务不存在")
    
    schedule = ServiceSchedule(
        service_id=service_id,
        title=data.get("title"),
        scheduled_date=data.get("scheduled_date"),
        scheduled_time=data.get("scheduled_time"),
        duration=data.get("duration"),
        staff_id=data.get("staff_id"),
        remark=data.get("remark"),
    )
    db.add(schedule)
    
    # 如果服务状态是planned，更新为scheduled
    if service.status == ServiceStatus.PLANNED:
        service.status = ServiceStatus.SCHEDULED
    
    await db.flush()
    await db.refresh(schedule)
    
    return ResponseSchema(data={
        "id": schedule.id,
        "title": schedule.title,
        "scheduled_date": schedule.scheduled_date.isoformat() if schedule.scheduled_date else None,
    }, message="排期创建成功")
