"""
Dashboard 统计接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_current_user, require_permissions
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User
from app.models.company import Company
from app.models.contract import Contract
from app.models.finance import Invoice, Payment

router = APIRouter()


@router.get("/dashboard", response_model=ResponseSchema)
async def get_dashboard_stats(
    current_user: User = Depends(require_permissions(["statistics:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取 Dashboard 统计数据"""
    
    # 客户总数
    company_count_result = await db.execute(
        select(func.count(Company.id)).where(Company.is_deleted == False)
    )
    total_customers = company_count_result.scalar() or 0
    
    # 合同统计
    contract_result = await db.execute(
        select(
            func.count(Contract.id),
            func.coalesce(func.sum(Contract.amount), 0)
        ).where(Contract.is_deleted == False)
    )
    contract_stats = contract_result.first()
    contract_count = contract_stats[0] if contract_stats else 0
    total_contract_amount = float(contract_stats[1]) if contract_stats else 0
    
    # 收款统计
    payment_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.is_deleted == False)
    )
    total_payment_amount = float(payment_result.scalar() or 0)
    
    # 进行中服务（执行中的合同）
    active_services_result = await db.execute(
        select(func.count(Contract.id))
        .where(Contract.status == "executing", Contract.is_deleted == False)
    )
    active_services = active_services_result.scalar() or 0
    
    # 开票统计
    invoice_count_result = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.is_deleted == False)
    )
    invoice_count = invoice_count_result.scalar() or 0
    
    # 待办任务数量
    pending_tasks = 0  # 暂时返回0，后续可以实现待办逻辑
    
    return ResponseSchema(
        data={
            "total_contract_amount": total_contract_amount,
            "total_payment_amount": total_payment_amount,
            "active_services": active_services,
            "total_customers": total_customers,
            "contract_count": contract_count,
            "invoice_count": invoice_count,
            "pending_tasks": pending_tasks,
        }
    )


@router.get("/todos", response_model=ResponseSchema)
async def get_todos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取待办事项"""
    
    # 这里可以实现真实的待办逻辑
    # 例如：即将到期的合同、待审批的开票申请等
    
    todos = [
        {
            "id": 1,
            "title": "合同到期提醒",
            "description": "有3个合同将在7天内到期",
            "type": "warning",
            "date": "今天",
        },
        {
            "id": 2,
            "title": "开票申请待审批",
            "description": "有2条开票申请待处理",
            "type": "processing",
            "date": "今天",
        },
        {
            "id": 3,
            "title": "服务报告待提交",
            "description": "5个服务项目报告待提交",
            "type": "default",
            "date": "昨天",
        },
    ]
    
    return ResponseSchema(data=todos)


@router.get("/activities", response_model=ResponseSchema)
async def get_activities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取最近动态"""
    
    # 这里可以实现真实的动态查询
    # 例如：查询最近的操作日志
    
    activities = [
        {
            "id": 1,
            "user": "张三",
            "action": "创建了合同",
            "target": "安全生产评价合同-2024001",
            "time": "10分钟前",
        },
        {
            "id": 2,
            "user": "李四",
            "action": "完成了服务",
            "target": "XX化工年度安全检查",
            "time": "30分钟前",
        },
        {
            "id": 3,
            "user": "王五",
            "action": "申请了开票",
            "target": "发票申请-2024005",
            "time": "1小时前",
        },
    ]
    
    return ResponseSchema(data=activities)
