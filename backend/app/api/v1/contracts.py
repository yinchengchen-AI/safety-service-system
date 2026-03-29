"""
合同管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.models.company import Company

router = APIRouter()


def build_contract_response(contract: Contract) -> dict:
    """构建合同响应数据"""
    return {
        "id": contract.id,
        "code": contract.code,
        "name": contract.name,
        "type": contract.type,
        "amount": float(contract.amount) if contract.amount else 0,
        "company_id": contract.company_id,
        "sign_date": contract.sign_date.isoformat() if contract.sign_date else None,
        "start_date": contract.start_date.isoformat() if contract.start_date else None,
        "end_date": contract.end_date.isoformat() if contract.end_date else None,
        "status": contract.status,
        "service_content": contract.service_content,
        "service_cycle": contract.service_cycle,
        "service_times": contract.service_times,
        "payment_terms": contract.payment_terms,
        "manager_id": contract.manager_id,
        "remark": contract.remark,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
        "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
        "company": {
            "id": contract.company.id,
            "name": contract.company.name
        } if contract.company else None,
        "manager": {
            "id": contract.manager.id,
            "real_name": contract.manager.real_name
        } if contract.manager else None
    }


@router.get("", response_model=ResponseSchema)
async def list_contracts(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    status: str = None,
    company_id: int = None,
    current_user: User = Depends(require_permissions(["contract:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取合同列表"""
    # 构建查询
    query = select(Contract).options(
        selectinload(Contract.company),
        selectinload(Contract.manager)
    )
    
    # 关键词搜索
    if keyword:
        query = query.where(
            (Contract.name.ilike(f"%{keyword}%")) |
            (Contract.code.ilike(f"%{keyword}%"))
        )
    
    # 状态筛选
    if status:
        query = query.where(Contract.status == status)
    
    # 客户筛选
    if company_id:
        query = query.where(Contract.company_id == company_id)
    
    # 获取总数
    count_query = select(func.count(Contract.id))
    if keyword:
        count_query = count_query.where(
            (Contract.name.ilike(f"%{keyword}%")) |
            (Contract.code.ilike(f"%{keyword}%"))
        )
    if status:
        count_query = count_query.where(Contract.status == status)
    if company_id:
        count_query = count_query.where(Contract.company_id == company_id)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Contract.created_at.desc())
    
    result = await db.execute(query)
    contracts = result.scalars().all()
    
    return ResponseSchema(data={
        "items": [build_contract_response(c) for c in contracts],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/{contract_id}", response_model=ResponseSchema)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(require_permissions(["contract:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取合同详情"""
    result = await db.execute(
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.company),
            selectinload(Contract.manager)
        )
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    return ResponseSchema(data=build_contract_response(contract))


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contract(
    data: dict,
    current_user: User = Depends(require_permissions(["contract:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建合同"""
    # 检查合同编号是否已存在
    result = await db.execute(
        select(Contract).where(Contract.code == data.get("code"))
    )
    if result.scalar_one_or_none():
        return ResponseSchema(code=400, message="合同编号已存在")
    
    # 检查客户是否存在
    company_id = data.get("company_id")
    if company_id:
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        if not result.scalar_one_or_none():
            return ResponseSchema(code=400, message="客户不存在")
    
    contract = Contract(**data)
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    
    return ResponseSchema(data=build_contract_response(contract), message="创建成功")


@router.put("/{contract_id}", response_model=ResponseSchema)
async def update_contract(
    contract_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["contract:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新合同"""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    # 更新字段
    for key, value in data.items():
        if hasattr(contract, key) and key != "id":
            setattr(contract, key, value)
    
    await db.commit()
    await db.refresh(contract)
    
    return ResponseSchema(data=build_contract_response(contract), message="更新成功")


@router.delete("/{contract_id}", response_model=ResponseSchema)
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(require_permissions(["contract:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除合同"""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    await db.delete(contract)
    await db.commit()
    
    return ResponseSchema(message="删除成功")


@router.post("/{contract_id}/approve", response_model=ResponseSchema)
async def approve_contract(
    contract_id: int,
    data: dict = None,
    current_user: User = Depends(require_permissions(["contract:approve"])),
    db: AsyncSession = Depends(get_db)
):
    """审批合同"""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    # 更新状态为已审批
    contract.status = ContractStatus.APPROVED
    await db.commit()
    await db.refresh(contract)
    
    return ResponseSchema(data=build_contract_response(contract), message="审批成功")
