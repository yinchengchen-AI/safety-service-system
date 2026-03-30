"""
财务管理接口 - 开票、收款
简化版：合同 -> 开票 -> 收款
"""

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.core.permissions import PermissionCode
from app.database import get_db
from app.models.contract import Contract
from app.models.finance import Invoice, InvoiceApplication, InvoiceStatus, Payment, PaymentStatus
from app.models.user import User
from app.schemas.base import ResponseSchema

router = APIRouter()


async def update_contract_finance_stats(db: AsyncSession, contract_id: int):
    """统一更新合同财务统计（已开票金额、已收款金额）

    此函数应在以下场景调用：
    1. 创建发票后
    2. 删除发票后
    3. 创建收款后
    4. 删除收款后
    """
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        return

    # 重新计算已开票金额
    invoice_result = await db.execute(
        select(func.coalesce(func.sum(Invoice.amount), Decimal("0"))).where(
            Invoice.contract_id == contract_id
        )
    )
    invoiced_amount = invoice_result.scalar()

    # 重新计算已收款金额
    payment_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), Decimal("0"))).where(
            Payment.contract_id == contract_id
        )
    )
    paid_amount = payment_result.scalar()

    # 更新合同
    contract.invoiced_amount = invoiced_amount
    contract.paid_amount = paid_amount

    await db.flush()


# ==================== 开票管理 ====================


@router.get("/invoices", response_model=ResponseSchema)
async def list_invoices(
    contract_id: int = None,
    status: str = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_VIEW])),
    db: AsyncSession = Depends(get_db),
):
    """获取发票列表"""
    query = select(Invoice).options(selectinload(Invoice.contract), selectinload(Invoice.issuer))

    if contract_id:
        query = query.where(Invoice.contract_id == contract_id)
    if status:
        query = query.where(Invoice.status == status)

    # 获取总数
    count_query = select(func.count(Invoice.id))
    if contract_id:
        count_query = count_query.where(Invoice.contract_id == contract_id)
    if status:
        count_query = count_query.where(Invoice.status == status)

    result = await db.execute(count_query)
    total = result.scalar()

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Invoice.issue_date.desc())

    result = await db.execute(query)
    invoices = result.scalars().all()

    # 构建响应
    items = []
    for inv in invoices:
        items.append(
            {
                "id": inv.id,
                "invoice_no": inv.invoice_no,
                "invoice_code": inv.invoice_code,
                "type": inv.type,
                "amount": float(inv.amount),
                "paid_amount": float(inv.paid_amount),
                "tax_amount": float(inv.tax_amount) if inv.tax_amount else None,
                "status": inv.status,
                "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
                "buyer_name": inv.buyer_name,
                "contract": {
                    "id": inv.contract.id,
                    "name": inv.contract.name,
                    "code": inv.contract.code,
                }
                if inv.contract
                else None,
                "issuer": {
                    "id": inv.issuer.id,
                    "real_name": inv.issuer.real_name,
                }
                if inv.issuer
                else None,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
        )

    return ResponseSchema(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("/invoices", response_model=ResponseSchema)
async def create_invoice(
    data: dict,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """创建发票"""
    contract_id = data.get("contract_id")
    amount = Decimal(str(data.get("amount", 0)))

    # 检查合同
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        return ResponseSchema(code=404, message="合同不存在")

    # 校验开票金额
    if amount <= 0:
        return ResponseSchema(code=400, message="开票金额必须大于0")

    # 计算剩余可开票金额
    remaining = contract.amount - contract.invoiced_amount
    if amount > remaining:
        return ResponseSchema(code=400, message=f"开票金额超过剩余可开金额，剩余：{remaining}")

    # 创建发票
    invoice = Invoice(
        invoice_no=data.get("invoice_no"),
        invoice_code=data.get("invoice_code"),
        contract_id=contract_id,
        type=data.get("type", "special"),
        amount=amount,
        tax_amount=Decimal(str(data.get("tax_amount"))) if data.get("tax_amount") else None,
        issue_date=data.get("issue_date"),
        buyer_name=data.get("buyer_name", contract.company.name if contract.company else ""),
        buyer_tax_no=data.get("buyer_tax_no"),
        seller_name=data.get("seller_name"),
        seller_tax_no=data.get("seller_tax_no"),
        status="issued",
        issuer_id=current_user.id,
        remark=data.get("remark"),
    )

    db.add(invoice)
    await db.flush()

    # 统一更新合同财务统计
    await update_contract_finance_stats(db, contract_id)
    await db.refresh(invoice)

    return ResponseSchema(
        data={
            "id": invoice.id,
            "invoice_no": invoice.invoice_no,
            "amount": float(invoice.amount),
        },
        message="开票成功",
    )


@router.delete("/invoices/{invoice_id}", response_model=ResponseSchema)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """删除/作废发票"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id).options(selectinload(Invoice.contract))
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")

    # 检查是否已有收款
    if invoice.paid_amount > 0:
        return ResponseSchema(code=400, message="该发票已有收款记录，不能删除")

    # 删除发票
    await db.delete(invoice)
    await db.flush()

    # 统一更新合同财务统计
    await update_contract_finance_stats(db, contract.id)

    return ResponseSchema(message="删除成功")


# ==================== 收款管理 ====================


@router.get("/payments", response_model=ResponseSchema)
async def list_payments(
    contract_id: int = None,
    invoice_id: int = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(require_permissions([PermissionCode.PAYMENT_VIEW])),
    db: AsyncSession = Depends(get_db),
):
    """获取收款记录列表"""
    query = select(Payment).options(
        selectinload(Payment.contract),
        selectinload(Payment.invoice),
        selectinload(Payment.recorder),
    )

    if contract_id:
        query = query.where(Payment.contract_id == contract_id)
    if invoice_id:
        query = query.where(Payment.invoice_id == invoice_id)

    # 获取总数
    count_query = select(func.count(Payment.id))
    if contract_id:
        count_query = count_query.where(Payment.contract_id == contract_id)
    if invoice_id:
        count_query = count_query.where(Payment.invoice_id == invoice_id)

    result = await db.execute(count_query)
    total = result.scalar()

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Payment.payment_date.desc())

    result = await db.execute(query)
    payments = result.scalars().all()

    # 构建响应
    items = []
    for pay in payments:
        items.append(
            {
                "id": pay.id,
                "code": pay.code,
                "amount": float(pay.amount),
                "payment_date": pay.payment_date.isoformat() if pay.payment_date else None,
                "method": pay.method,
                "payer_name": pay.payer_name,
                "payer_account": pay.payer_account,
                "voucher_no": pay.voucher_no,
                "remark": pay.remark,
                "contract": {
                    "id": pay.contract.id,
                    "name": pay.contract.name,
                    "code": pay.contract.code,
                }
                if pay.contract
                else None,
                "invoice": {
                    "id": pay.invoice.id,
                    "invoice_no": pay.invoice.invoice_no,
                    "amount": float(pay.invoice.amount),
                }
                if pay.invoice
                else None,
                "recorder": {
                    "id": pay.recorder.id,
                    "real_name": pay.recorder.real_name,
                }
                if pay.recorder
                else None,
                "created_at": pay.created_at.isoformat() if pay.created_at else None,
            }
        )

    return ResponseSchema(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("/payments", response_model=ResponseSchema)
async def create_payment(
    data: dict,
    current_user: User = Depends(require_permissions([PermissionCode.PAYMENT_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """创建收款记录"""
    contract_id = data.get("contract_id")
    invoice_id = data.get("invoice_id")
    amount = Decimal(str(data.get("amount", 0)))

    # 检查合同
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        return ResponseSchema(code=404, message="合同不存在")

    # 校验收款金额
    if amount <= 0:
        return ResponseSchema(code=400, message="收款金额必须大于0")

    # 如果关联了发票，检查发票
    invoice = None
    if invoice_id:
        result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        invoice = result.scalar_one_or_none()

        if not invoice:
            return ResponseSchema(code=404, message="发票不存在")

        if invoice.contract_id != contract_id:
            return ResponseSchema(code=400, message="发票与合同不匹配")

        # 检查是否超收
        remaining = invoice.amount - invoice.paid_amount
        if amount > remaining:
            return ResponseSchema(code=400, message=f"收款金额超过发票未收金额，剩余：{remaining}")

    # 检查是否超过合同金额
    total_paid = contract.paid_amount + amount
    if total_paid > contract.amount:
        return ResponseSchema(
            code=400,
            message=f"收款总额不能超过合同金额，已收：{contract.paid_amount}，本次：{amount}，合同：{contract.amount}",
        )

    # 生成收款编号
    result = await db.execute(select(func.count(Payment.id)))
    count = result.scalar()
    code = f"SK{count + 1:06d}"

    # 创建收款记录
    payment = Payment(
        code=code,
        contract_id=contract_id,
        invoice_id=invoice_id,
        amount=amount,
        payment_date=data.get("payment_date"),
        method=data.get("method", "bank_transfer"),
        payer_name=data.get("payer_name"),
        payer_account=data.get("payer_account"),
        payer_bank=data.get("payer_bank"),
        receiver_account=data.get("receiver_account"),
        receiver_bank=data.get("receiver_bank"),
        voucher_no=data.get("voucher_no"),
        remark=data.get("remark"),
        recorder_id=current_user.id,
        status=PaymentStatus.CONFIRMED,
    )

    db.add(payment)
    await db.flush()

    # 统一更新合同财务统计
    await update_contract_finance_stats(db, contract_id)
    await db.refresh(payment)

    return ResponseSchema(
        data={
            "id": payment.id,
            "code": payment.code,
            "amount": float(payment.amount),
        },
        message="收款登记成功",
    )


@router.delete("/payments/{payment_id}", response_model=ResponseSchema)
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.PAYMENT_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """删除收款记录"""
    result = await db.execute(
        select(Payment)
        .where(Payment.id == payment_id)
        .options(selectinload(Payment.contract), selectinload(Payment.invoice))
    )
    payment = result.scalar_one_or_none()

    if not payment:
        return ResponseSchema(code=404, message="收款记录不存在")

    contract_id = payment.contract_id

    # 删除收款记录
    await db.delete(payment)
    await db.flush()

    # 统一更新合同财务统计
    await update_contract_finance_stats(db, contract_id)

    return ResponseSchema(message="删除成功")


# ==================== 财务统计 ====================


@router.get("/contracts/{contract_id}/finance-summary", response_model=ResponseSchema)
async def get_contract_finance_summary(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取合同财务汇总"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()

    if not contract:
        return ResponseSchema(code=404, message="合同不存在")

    # 获取发票列表
    result = await db.execute(select(Invoice).where(Invoice.contract_id == contract_id))
    invoices = result.scalars().all()

    # 获取收款列表
    result = await db.execute(select(Payment).where(Payment.contract_id == contract_id))
    payments = result.scalars().all()

    return ResponseSchema(
        data={
            "contract_id": contract.id,
            "contract_name": contract.name,
            "contract_amount": float(contract.amount),
            "invoiced_amount": float(contract.invoiced_amount),
            "paid_amount": float(contract.paid_amount),
            "uninvoiced_amount": float(contract.amount - contract.invoiced_amount),
            "unpaid_amount": float(contract.invoiced_amount - contract.paid_amount),
            "invoices": [
                {
                    "id": inv.id,
                    "invoice_no": inv.invoice_no,
                    "amount": float(inv.amount),
                    "paid_amount": float(inv.paid_amount),
                    "status": inv.status,
                }
                for inv in invoices
            ],
            "payments": [
                {
                    "id": pay.id,
                    "code": pay.code,
                    "amount": float(pay.amount),
                    "payment_date": pay.payment_date.isoformat() if pay.payment_date else None,
                }
                for pay in payments
            ],
        }
    )


# ==================== 发票状态变更 ====================


def validate_invoice_status_transition(old_status: str, new_status: str) -> tuple[bool, str]:
    """校验发票状态流转是否合法"""
    valid_transitions = {
        InvoiceStatus.PENDING: [InvoiceStatus.ISSUED, InvoiceStatus.CANCELLED],
        InvoiceStatus.ISSUED: [
            InvoiceStatus.SENT,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.RED_FLUSHED,
        ],
        InvoiceStatus.SENT: [InvoiceStatus.RECEIVED, InvoiceStatus.CANCELLED],
        InvoiceStatus.RECEIVED: [InvoiceStatus.RED_FLUSHED],
        InvoiceStatus.CANCELLED: [],
        InvoiceStatus.RED_FLUSHED: [],
    }
    allowed = valid_transitions.get(old_status, [])
    if new_status in allowed:
        return True, ""
    return False, f"不能从{old_status}状态变更为{new_status}状态"


@router.post("/invoices/{invoice_id}/send", response_model=ResponseSchema)
async def send_invoice(
    invoice_id: int,
    data: dict = None,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """发票寄送（issued -> sent）"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")

    if invoice.status != InvoiceStatus.ISSUED:
        return ResponseSchema(code=400, message=f"当前状态{invoice.status}不能寄送")

    invoice.status = InvoiceStatus.SENT
    if data:
        invoice.express_company = data.get("express_company")
        invoice.express_no = data.get("express_no")

    await db.flush()
    await db.refresh(invoice)

    return ResponseSchema(data={"id": invoice.id, "status": invoice.status}, message="发票已寄送")


@router.post("/invoices/{invoice_id}/receive", response_model=ResponseSchema)
async def receive_invoice(
    invoice_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """发票签收（sent -> received）"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")

    if invoice.status != InvoiceStatus.SENT:
        return ResponseSchema(code=400, message=f"当前状态{invoice.status}不能签收")

    invoice.status = InvoiceStatus.RECEIVED
    await db.flush()
    await db.refresh(invoice)

    return ResponseSchema(data={"id": invoice.id, "status": invoice.status}, message="发票已签收")


@router.post("/invoices/{invoice_id}/cancel", response_model=ResponseSchema)
async def cancel_invoice(
    invoice_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.INVOICE_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """作废发票"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id).options(selectinload(Invoice.payments))
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")

    if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.RED_FLUSHED]:
        return ResponseSchema(code=400, message="发票已作废或已红冲")

    if len(invoice.payments) > 0:
        return ResponseSchema(code=400, message="发票已有收款记录，不能作废")

    invoice.status = InvoiceStatus.CANCELLED
    await db.flush()

    await update_contract_finance_stats(db, invoice.contract_id)

    return ResponseSchema(data={"id": invoice.id, "status": invoice.status}, message="发票已作废")


# ==================== 收款状态变更 ====================


def validate_payment_status_transition(old_status: str, new_status: str) -> tuple[bool, str]:
    """校验收款状态流转是否合法"""
    valid_transitions = {
        PaymentStatus.PENDING: [PaymentStatus.CONFIRMED, PaymentStatus.CANCELLED],
        PaymentStatus.CONFIRMED: [PaymentStatus.VERIFIED, PaymentStatus.CANCELLED],
        PaymentStatus.VERIFIED: [PaymentStatus.CANCELLED],
        PaymentStatus.CANCELLED: [],
    }
    allowed = valid_transitions.get(old_status, [])
    if new_status in allowed:
        return True, ""
    return False, f"不能从{old_status}状态变更为{new_status}状态"


@router.post("/payments/{payment_id}/verify", response_model=ResponseSchema)
async def verify_payment(
    payment_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.PAYMENT_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """核销收款（confirmed -> verified）"""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        return ResponseSchema(code=404, message="收款记录不存在")

    if payment.status != PaymentStatus.CONFIRMED:
        return ResponseSchema(code=400, message=f"当前状态{payment.status}不能核销")

    payment.status = PaymentStatus.VERIFIED
    await db.flush()
    await db.refresh(payment)

    return ResponseSchema(data={"id": payment.id, "status": payment.status}, message="收款已核销")


@router.post("/payments/{payment_id}/cancel", response_model=ResponseSchema)
async def cancel_payment(
    payment_id: int,
    current_user: User = Depends(require_permissions([PermissionCode.PAYMENT_CREATE])),
    db: AsyncSession = Depends(get_db),
):
    """取消收款"""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if not payment:
        return ResponseSchema(code=404, message="收款记录不存在")

    if payment.status == PaymentStatus.CANCELLED:
        return ResponseSchema(code=400, message="收款已取消")

    payment.status = PaymentStatus.CANCELLED
    await db.flush()

    await update_contract_finance_stats(db, payment.contract_id)

    return ResponseSchema(data={"id": payment.id, "status": payment.status}, message="收款已取消")


# ==================== 合同过期检查 ====================


@router.post("/contracts/check-expired", response_model=ResponseSchema)
async def check_expired_contracts(
    current_user: User = Depends(require_permissions([PermissionCode.CONTRACT_VIEW])),
    db: AsyncSession = Depends(get_db),
):
    """手动检查并更新过期合同状态"""
    from datetime import date as date_type
    from app.models.contract import ContractStatus

    today = date_type.today()

    result = await db.execute(
        select(Contract).where(
            Contract.end_date < today,
            Contract.status.in_([ContractStatus.SIGNED, ContractStatus.EXECUTING]),
        )
    )
    expired_contracts = result.scalars().all()

    updated_count = 0
    for contract in expired_contracts:
        contract.status = ContractStatus.EXPIRED
        updated_count += 1

    await db.flush()

    return ResponseSchema(
        data={"updated_count": updated_count}, message=f"已更新{updated_count}个过期合同"
    )
