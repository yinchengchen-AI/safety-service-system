"""
合同管理接口
"""
from datetime import date
from decimal import Decimal

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
from app.api.v1.companies import update_company_status_on_contract


# 状态机定义：定义允许的状态流转
def validate_status_transition(old_status: str, new_status: str) -> tuple[bool, str]:
    """校验合同状态流转是否合法
    
    Returns:
        (是否合法, 错误信息)
    """
    valid_transitions = {
        ContractStatus.DRAFT: [ContractStatus.PENDING, ContractStatus.TERMINATED],
        ContractStatus.PENDING: [ContractStatus.APPROVED, ContractStatus.DRAFT, ContractStatus.TERMINATED],
        ContractStatus.APPROVED: [ContractStatus.SIGNED, ContractStatus.DRAFT, ContractStatus.TERMINATED],
        ContractStatus.SIGNED: [ContractStatus.EXECUTING, ContractStatus.TERMINATED],
        ContractStatus.EXECUTING: [ContractStatus.COMPLETED, ContractStatus.TERMINATED],
        ContractStatus.COMPLETED: [],  # 终态
        ContractStatus.TERMINATED: [],  # 终态
        ContractStatus.EXPIRED: [],  # 终态
    }
    
    allowed = valid_transitions.get(old_status, [])
    if new_status in allowed:
        return True, ""
    
    return False, f"不能从{old_status}状态变更为{new_status}状态"

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
    
    # 转换数据类型
    contract_data = {
        "code": data.get("code"),
        "name": data.get("name"),
        "type": data.get("type"),
        "amount": Decimal(str(data.get("amount", 0))),
        "company_id": int(data.get("company_id")),
        "status": data.get("status", "draft"),
        "service_content": data.get("service_content"),
        "service_cycle": data.get("service_cycle"),
        "service_times": int(data.get("service_times", 1)),
        "payment_terms": data.get("payment_terms"),
        "manager_id": data.get("manager_id"),
        "remark": data.get("remark"),
    }
    
    # 处理日期字段
    if data.get("sign_date"):
        if isinstance(data["sign_date"], str):
            contract_data["sign_date"] = date.fromisoformat(data["sign_date"])
        else:
            contract_data["sign_date"] = data["sign_date"]
    
    if data.get("start_date"):
        if isinstance(data["start_date"], str):
            contract_data["start_date"] = date.fromisoformat(data["start_date"])
        else:
            contract_data["start_date"] = data["start_date"]
    
    if data.get("end_date"):
        if isinstance(data["end_date"], str):
            contract_data["end_date"] = date.fromisoformat(data["end_date"])
        else:
            contract_data["end_date"] = data["end_date"]
    
    contract = Contract(**contract_data)
    db.add(contract)
    await db.flush()
    
    # 更新客户状态（潜在客户 -> 合作中）
    await update_company_status_on_contract(db, int(data.get("company_id")))
    
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
    
    # 状态变更校验
    new_status = data.get("status")
    if new_status and new_status != contract.status:
        is_valid, error_msg = validate_status_transition(contract.status, new_status)
        if not is_valid:
            return ResponseSchema(code=400, message=error_msg)
    
    # 更新字段（处理类型转换）
    for key, value in data.items():
        if key == "id" or not hasattr(contract, key):
            continue
        
        # 处理金额字段
        if key == "amount" and value is not None:
            value = Decimal(str(value))
        # 处理日期字段
        elif key in ("sign_date", "start_date", "end_date") and value is not None:
            if isinstance(value, str):
                value = date.fromisoformat(value)
        # 处理整数字段
        elif key in ("company_id", "manager_id", "service_times") and value is not None:
            value = int(value) if value else None
        
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


@router.post("/{contract_id}/change-status", response_model=ResponseSchema)
async def change_contract_status(
    contract_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["contract:update"])),
    db: AsyncSession = Depends(get_db)
):
    """变更合同状态（带状态机校验）"""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    new_status = data.get("status")
    if not new_status:
        return ResponseSchema(code=400, message="缺少status参数")
    
    # 状态机校验
    is_valid, error_msg = validate_status_transition(contract.status, new_status)
    if not is_valid:
        return ResponseSchema(code=400, message=error_msg)
    
    old_status = contract.status
    contract.status = new_status
    
    # 状态变更时的特殊处理
    if new_status == ContractStatus.SIGNED and not contract.sign_date:
        # 签订时自动设置签订日期
        contract.sign_date = date.today()
    
    if new_status == ContractStatus.EXECUTING and not contract.start_date:
        # 执行时自动设置开始日期
        contract.start_date = date.today()
    
    if new_status == ContractStatus.COMPLETED and not contract.end_date:
        # 完成时自动设置结束日期
        contract.end_date = date.today()
    
    await db.commit()
    await db.refresh(contract)
    
    return ResponseSchema(
        data=build_contract_response(contract), 
        message=f"状态变更成功：{old_status} -> {new_status}"
    )


@router.post("/{contract_id}/approve", response_model=ResponseSchema)
async def approve_contract(
    contract_id: int,
    data: dict = None,
    current_user: User = Depends(require_permissions(["contract:approve"])),
    db: AsyncSession = Depends(get_db)
):
    """审批合同（pending -> approved）"""
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        return ResponseSchema(code=404, message="合同不存在")
    
    if contract.status != ContractStatus.PENDING:
        return ResponseSchema(code=400, message="只有待审批状态的合同可以审批")
    
    contract.status = ContractStatus.APPROVED
    await db.commit()
    await db.refresh(contract)
    
    return ResponseSchema(data=build_contract_response(contract), message="审批成功")
