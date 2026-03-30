"""
Dashboard 统计接口
"""

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract

from app.api.deps import get_current_user, require_permissions
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User
from app.models.company import Company
from app.models.contract import Contract
from app.models.finance import Invoice, Payment
from app.models.service import Service
from app.models.system import LoginLog, OperationLog

router = APIRouter()


@router.get("/dashboard", response_model=ResponseSchema)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Dashboard 统计数据"""

    # 客户总数
    company_count_result = await db.execute(
        select(func.count(Company.id)).where(Company.is_deleted == False)
    )
    total_customers = company_count_result.scalar() or 0

    # 合同统计
    contract_result = await db.execute(
        select(func.count(Contract.id), func.coalesce(func.sum(Contract.amount), 0)).where(
            Contract.is_deleted == False
        )
    )
    contract_stats = contract_result.first()
    contract_count = contract_stats[0] if contract_stats else 0
    total_contract_amount = float(contract_stats[1]) if contract_stats else 0

    # 收款统计
    payment_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.is_deleted == False)
    )
    total_payment_amount = float(payment_result.scalar() or 0)

    # 进行中服务（执行中的合同）
    active_services_result = await db.execute(
        select(func.count(Contract.id)).where(
            Contract.status == "executing", Contract.is_deleted == False
        )
    )
    active_services = active_services_result.scalar() or 0

    # 开票统计
    invoice_count_result = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.is_deleted == False)
    )
    invoice_count = invoice_count_result.scalar() or 0

    # 待办任务数量
    pending_tasks = 0

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
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取待办事项"""
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
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取最近动态"""
    result = await db.execute(
        select(OperationLog)
        .where(OperationLog.status == "success")
        .order_by(OperationLog.operation_time.desc())
        .limit(10)
    )
    logs = result.scalars().all()

    activities = []
    for log in logs:
        time_diff = datetime.now() - log.operation_time
        if time_diff.days > 0:
            time_str = f"{time_diff.days}天前"
        elif time_diff.seconds // 3600 > 0:
            time_str = f"{time_diff.seconds // 3600}小时前"
        elif time_diff.seconds // 60 > 0:
            time_str = f"{time_diff.seconds // 60}分钟前"
        else:
            time_str = "刚刚"

        activities.append(
            {
                "id": log.id,
                "user": log.real_name or log.username or "系统",
                "action": log.description or log.action or "操作",
                "target": log.module or "系统",
                "time": time_str,
            }
        )

    return ResponseSchema(data=activities)


# ==================== 经营统计接口 ====================


@router.get("/business/overview", response_model=ResponseSchema)
async def get_business_overview(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取经营概览统计"""

    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    # 客户统计
    company_result = await db.execute(
        select(
            func.count(Company.id),
            func.count(Company.id).filter(Company.created_at >= start_dt),
            func.count(Company.id).filter(Company.created_at >= start_dt - timedelta(days=365)),
        ).where(Company.is_deleted == False)
    )
    company_stats = company_result.first()
    total_companies = company_stats[0] if company_stats else 0
    new_companies_this_period = company_stats[1] if company_stats else 0
    new_companies_last_period = company_stats[2] if company_stats else 0

    # 合同统计
    contract_result = await db.execute(
        select(
            func.count(Contract.id),
            func.coalesce(func.sum(Contract.amount), 0),
            func.count(Contract.id).filter(Contract.created_at >= start_dt),
            func.coalesce(func.sum(Contract.amount).filter(Contract.created_at >= start_dt), 0),
        ).where(Contract.is_deleted == False, Contract.created_at < end_dt)
    )
    contract_stats = contract_result.first()
    total_contracts = contract_stats[0] if contract_stats else 0
    total_contract_amount = float(contract_stats[1]) if contract_stats else 0
    new_contracts = contract_stats[2] if contract_stats else 0
    new_contract_amount = float(contract_stats[3]) if contract_stats else 0

    # 收款统计
    payment_result = await db.execute(
        select(
            func.coalesce(func.sum(Payment.amount), 0),
            func.coalesce(func.sum(Payment.amount).filter(Payment.payment_date >= start_dt), 0),
            func.count(Payment.id).filter(Payment.payment_date >= start_dt),
        ).where(Payment.is_deleted == False, Payment.payment_date < end_dt)
    )
    payment_stats = payment_result.first()
    total_payments = float(payment_stats[0]) if payment_stats else 0
    period_payments = float(payment_stats[1]) if payment_stats else 0
    payment_count = payment_stats[2] if payment_stats else 0

    # 服务统计
    service_result = await db.execute(
        select(
            func.count(Service.id),
            func.count(Service.id).filter(Service.status == "completed"),
            func.count(Service.id).filter(Service.status == "pending"),
            func.count(Service.id).filter(Service.status == "in_progress"),
        ).where(Service.is_deleted == False)
    )
    service_stats = service_result.first()
    total_services = service_stats[0] if service_stats else 0
    completed_services = service_stats[1] if service_stats else 0
    pending_services = service_stats[2] if service_stats else 0
    in_progress_services = service_stats[3] if service_stats else 0

    return ResponseSchema(
        data={
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "companies": {
                "total": total_companies,
                "new_this_period": new_companies_this_period,
                "new_last_period": new_companies_last_period,
                "growth_rate": round(
                    (new_companies_this_period - new_companies_last_period)
                    / max(new_companies_last_period, 1)
                    * 100,
                    2,
                ),
            },
            "contracts": {
                "total": total_contracts,
                "total_amount": total_contract_amount,
                "new_count": new_contracts,
                "new_amount": new_contract_amount,
                "avg_amount": round(total_contract_amount / max(total_contracts, 1), 2),
            },
            "payments": {
                "total": total_payments,
                "period_total": period_payments,
                "period_count": payment_count,
                "collection_rate": round(total_payments / max(total_contract_amount, 1) * 100, 2),
            },
            "services": {
                "total": total_services,
                "completed": completed_services,
                "pending": pending_services,
                "in_progress": in_progress_services,
                "completion_rate": round(completed_services / max(total_services, 1) * 100, 2),
            },
        }
    )


@router.get("/business/trend", response_model=ResponseSchema)
async def get_business_trend(
    period: str = Query("month", description="统计周期: day/week/month/year"),
    months: int = Query(12, ge=1, le=24, description="查询月数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务趋势数据"""

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)

    # 按月统计合同金额
    contract_trend_result = await db.execute(
        select(
            extract("year", Contract.created_at).label("year"),
            extract("month", Contract.created_at).label("month"),
            func.count(Contract.id).label("count"),
            func.coalesce(func.sum(Contract.amount), 0).label("amount"),
        )
        .where(
            Contract.is_deleted == False,
            Contract.created_at >= start_date,
            Contract.created_at < end_date,
        )
        .group_by(extract("year", Contract.created_at), extract("month", Contract.created_at))
        .order_by("year", "month")
    )

    contract_trend = []
    for row in contract_trend_result.all():
        contract_trend.append(
            {
                "period": f"{int(row.year)}-{int(row.month):02d}",
                "count": int(row.count),
                "amount": float(row.amount),
            }
        )

    # 按月统计收款金额
    payment_trend_result = await db.execute(
        select(
            extract("year", Payment.payment_date).label("year"),
            extract("month", Payment.payment_date).label("month"),
            func.count(Payment.id).label("count"),
            func.coalesce(func.sum(Payment.amount), 0).label("amount"),
        )
        .where(
            Payment.is_deleted == False,
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date,
        )
        .group_by(extract("year", Payment.payment_date), extract("month", Payment.payment_date))
        .order_by("year", "month")
    )

    payment_trend = []
    for row in payment_trend_result.all():
        payment_trend.append(
            {
                "period": f"{int(row.year)}-{int(row.month):02d}",
                "count": int(row.count),
                "amount": float(row.amount),
            }
        )

    # 按月统计新增客户
    company_trend_result = await db.execute(
        select(
            extract("year", Company.created_at).label("year"),
            extract("month", Company.created_at).label("month"),
            func.count(Company.id).label("count"),
        )
        .where(
            Company.is_deleted == False,
            Company.created_at >= start_date,
            Company.created_at < end_date,
        )
        .group_by(extract("year", Company.created_at), extract("month", Company.created_at))
        .order_by("year", "month")
    )

    company_trend = []
    for row in company_trend_result.all():
        company_trend.append(
            {"period": f"{int(row.year)}-{int(row.month):02d}", "count": int(row.count)}
        )

    return ResponseSchema(
        data={
            "contract_trend": contract_trend,
            "payment_trend": payment_trend,
            "company_trend": company_trend,
        }
    )


@router.get("/business/distribution", response_model=ResponseSchema)
async def get_business_distribution(
    type: str = Query(
        "contract", description="分布类型: contract_status/company_type/service_type/payment_method"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务分布数据"""

    data = []

    if type == "contract_status":
        result = await db.execute(
            select(
                Contract.status,
                func.count(Contract.id).label("count"),
                func.coalesce(func.sum(Contract.amount), 0).label("amount"),
            )
            .where(Contract.is_deleted == False)
            .group_by(Contract.status)
        )

        status_names = {
            "draft": "草稿",
            "pending": "待审批",
            "approved": "已审批",
            "signed": "已签订",
            "executing": "执行中",
            "completed": "已完成",
            "cancelled": "已取消",
        }

        for row in result.all():
            data.append(
                {
                    "name": status_names.get(row.status, row.status),
                    "value": int(row.count),
                    "amount": float(row.amount),
                    "status": row.status,
                }
            )

    elif type == "company_type":
        result = await db.execute(
            select(Company.type, func.count(Company.id).label("count"))
            .where(Company.is_deleted == False)
            .group_by(Company.type)
        )

        type_names = {
            "manufacturing": "制造业",
            "chemical": "化工",
            "mining": "矿业",
            "construction": "建筑",
            "transportation": "交通运输",
            "other": "其他",
        }

        for row in result.all():
            data.append(
                {
                    "name": type_names.get(row.type, row.type or "未分类"),
                    "value": int(row.count),
                    "type": row.type,
                }
            )

    elif type == "payment_method":
        result = await db.execute(
            select(
                Payment.payment_method,
                func.count(Payment.id).label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("amount"),
            )
            .where(Payment.is_deleted == False)
            .group_by(Payment.payment_method)
        )

        method_names = {
            "bank_transfer": "银行转账",
            "cash": "现金",
            "check": "支票",
            "wechat": "微信支付",
            "alipay": "支付宝",
            "other": "其他",
        }

        for row in result.all():
            data.append(
                {
                    "name": method_names.get(row.payment_method, row.payment_method or "未分类"),
                    "value": int(row.count),
                    "amount": float(row.amount),
                    "method": row.payment_method,
                }
            )

    return ResponseSchema(data=data)


@router.get("/business/top-customers", response_model=ResponseSchema)
async def get_top_customers(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 top 客户（按合同金额）"""

    result = await db.execute(
        select(
            Company.id,
            Company.name,
            func.count(Contract.id).label("contract_count"),
            func.coalesce(func.sum(Contract.amount), 0).label("total_amount"),
        )
        .join(Contract, Contract.company_id == Company.id)
        .where(Company.is_deleted == False, Contract.is_deleted == False)
        .group_by(Company.id, Company.name)
        .order_by(func.sum(Contract.amount).desc())
        .limit(limit)
    )

    customers = []
    for row in result.all():
        customers.append(
            {
                "id": row.id,
                "name": row.name,
                "contract_count": int(row.contract_count),
                "total_amount": float(row.total_amount),
            }
        )

    return ResponseSchema(data=customers)


# ==================== 财务报表接口 ====================


@router.get("/finance/overview", response_model=ResponseSchema)
async def get_finance_overview(
    year: Optional[int] = Query(None, description="年份，默认当前年"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务概览"""

    if not year:
        year = datetime.now().year

    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    # 年度合同金额
    contract_result = await db.execute(
        select(func.coalesce(func.sum(Contract.amount), 0)).where(
            Contract.is_deleted == False,
            Contract.created_at >= start_date,
            Contract.created_at < end_date,
        )
    )
    annual_contract_amount = float(contract_result.scalar() or 0)

    # 年度收款金额
    payment_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.is_deleted == False,
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date,
        )
    )
    annual_payment_amount = float(payment_result.scalar() or 0)

    # 年度开票金额
    invoice_result = await db.execute(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.is_deleted == False,
            Invoice.created_at >= start_date,
            Invoice.created_at < end_date,
        )
    )
    annual_invoice_amount = float(invoice_result.scalar() or 0)

    # 应收账款
    receivable_result = await db.execute(
        select(func.coalesce(func.sum(Contract.amount), 0)).where(
            Contract.is_deleted == False, Contract.status.in_(["signed", "executing", "completed"])
        )
    )
    total_receivable = float(receivable_result.scalar() or 0)

    total_paid = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.is_deleted == False)
    )
    total_paid_amount = float(total_paid.scalar() or 0)

    outstanding_receivable = total_receivable - total_paid_amount

    return ResponseSchema(
        data={
            "year": year,
            "contract": {
                "annual_amount": annual_contract_amount,
                "total_receivable": total_receivable,
            },
            "payment": {
                "annual_amount": annual_payment_amount,
                "total_collected": total_paid_amount,
                "outstanding": outstanding_receivable,
                "collection_rate": round(total_paid_amount / max(total_receivable, 1) * 100, 2),
            },
            "invoice": {"annual_amount": annual_invoice_amount},
        }
    )


@router.get("/finance/monthly", response_model=ResponseSchema)
async def get_finance_monthly(
    year: Optional[int] = Query(None, description="年份，默认当前年"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取月度财务报表数据"""

    if not year:
        year = datetime.now().year

    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    # 按月统计合同金额
    contract_monthly = await db.execute(
        select(
            extract("month", Contract.created_at).label("month"),
            func.coalesce(func.sum(Contract.amount), 0).label("amount"),
        )
        .where(
            Contract.is_deleted == False,
            Contract.created_at >= start_date,
            Contract.created_at < end_date,
        )
        .group_by(extract("month", Contract.created_at))
        .order_by("month")
    )

    contract_data = {int(row.month): float(row.amount) for row in contract_monthly.all()}

    # 按月统计收款金额
    payment_monthly = await db.execute(
        select(
            extract("month", Payment.payment_date).label("month"),
            func.coalesce(func.sum(Payment.amount), 0).label("amount"),
        )
        .where(
            Payment.is_deleted == False,
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date,
        )
        .group_by(extract("month", Payment.payment_date))
        .order_by("month")
    )

    payment_data = {int(row.month): float(row.amount) for row in payment_monthly.all()}

    # 组装月度数据
    monthly_data = []
    for month in range(1, 13):
        monthly_data.append(
            {
                "month": f"{year}-{month:02d}",
                "month_name": f"{month}月",
                "contract_amount": contract_data.get(month, 0),
                "payment_amount": payment_data.get(month, 0),
            }
        )

    return ResponseSchema(data={"year": year, "monthly": monthly_data})


@router.get("/system/usage", response_model=ResponseSchema)
async def get_system_usage(
    days: int = Query(30, ge=1, le=90, description="查询天数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取系统使用情况统计"""

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 登录次数统计
    login_result = await db.execute(
        select(
            func.count(LoginLog.id).label("total"),
            func.count(LoginLog.id).filter(LoginLog.login_status == "success").label("success"),
            func.count(LoginLog.id).filter(LoginLog.login_status == "fail").label("fail"),
        ).where(LoginLog.login_time >= start_date, LoginLog.login_time < end_date)
    )
    login_stats = login_result.first()

    # 操作次数统计
    operation_result = await db.execute(
        select(
            func.count(OperationLog.id).label("total"),
            func.count(OperationLog.id).filter(OperationLog.status == "success").label("success"),
            func.count(OperationLog.id).filter(OperationLog.status == "fail").label("fail"),
        ).where(OperationLog.operation_time >= start_date, OperationLog.operation_time < end_date)
    )
    operation_stats = operation_result.first()

    # 活跃用户统计
    active_users = await db.execute(
        select(func.count(func.distinct(OperationLog.user_id))).where(
            OperationLog.operation_time >= start_date, OperationLog.operation_time < end_date
        )
    )

    # 模块使用热度
    module_hot = await db.execute(
        select(OperationLog.module, func.count(OperationLog.id).label("count"))
        .where(
            OperationLog.operation_time >= start_date,
            OperationLog.operation_time < end_date,
            OperationLog.module.isnot(None),
        )
        .group_by(OperationLog.module)
        .order_by(func.count(OperationLog.id).desc())
        .limit(10)
    )

    return ResponseSchema(
        data={
            "period": {
                "days": days,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
            "login": {
                "total": login_stats[0] if login_stats else 0,
                "success": login_stats[1] if login_stats else 0,
                "fail": login_stats[2] if login_stats else 0,
            },
            "operation": {
                "total": operation_stats[0] if operation_stats else 0,
                "success": operation_stats[1] if operation_stats else 0,
                "fail": operation_stats[2] if operation_stats else 0,
            },
            "active_users": active_users.scalar() or 0,
            "module_hot": [
                {"module": row.module, "count": int(row.count)} for row in module_hot.all()
            ],
        }
    )
