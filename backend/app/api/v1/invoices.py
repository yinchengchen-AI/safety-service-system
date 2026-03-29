"""
开票管理接口
"""
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User
from app.models.finance import InvoiceApplication, Invoice, InvoiceStatus
from app.models.contract import Contract

router = APIRouter()


def build_invoice_app_response(app: InvoiceApplication) -> dict:
    """构建开票申请响应数据"""
    return {
        "id": app.id,
        "code": app.code,
        "contract_id": app.contract_id,
        "invoice_type": app.invoice_type,
        "amount": float(app.amount) if app.amount else 0,
        "buyer_name": app.buyer_name,
        "buyer_tax_no": app.buyer_tax_no,
        "buyer_address": app.buyer_address,
        "buyer_bank": app.buyer_bank,
        "seller_name": app.seller_name,
        "seller_tax_no": app.seller_tax_no,
        "status": app.status,
        "applicant_id": app.applicant_id,
        "approver_id": app.approver_id,
        "approve_time": app.approve_time.isoformat() if app.approve_time else None,
        "approve_comment": app.approve_comment,
        "remark": app.remark,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
        "contract": {
            "id": app.contract.id,
            "name": app.contract.name,
            "code": app.contract.code
        } if app.contract else None,
        "applicant": {
            "id": app.applicant.id,
            "real_name": app.applicant.real_name
        } if app.applicant else None
    }


def build_invoice_response(inv: Invoice) -> dict:
    """构建发票响应数据"""
    return {
        "id": inv.id,
        "invoice_no": inv.invoice_no,
        "invoice_code": inv.invoice_code,
        "contract_id": inv.contract_id,
        "application_id": inv.application_id,
        "type": inv.type,
        "amount": float(inv.amount) if inv.amount else 0,
        "tax_amount": float(inv.tax_amount) if inv.tax_amount else None,
        "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
        "buyer_name": inv.buyer_name,
        "buyer_tax_no": inv.buyer_tax_no,
        "seller_name": inv.seller_name,
        "seller_tax_no": inv.seller_tax_no,
        "status": inv.status,
        "send_date": inv.send_date.isoformat() if inv.send_date else None,
        "express_company": inv.express_company,
        "express_no": inv.express_no,
        "issuer_id": inv.issuer_id,
        "remark": inv.remark,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        "contract": {
            "id": inv.contract.id,
            "name": inv.contract.name
        } if inv.contract else None,
        "issuer": {
            "id": inv.issuer.id,
            "real_name": inv.issuer.real_name
        } if inv.issuer else None
    }


@router.get("/applications", response_model=ResponseSchema)
async def list_invoice_applications(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    status: str = None,
    current_user: User = Depends(require_permissions(["invoice:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取开票申请列表"""
    query = select(InvoiceApplication).options(
        selectinload(InvoiceApplication.contract),
        selectinload(InvoiceApplication.applicant)
    )
    
    if keyword:
        query = query.where(
            (InvoiceApplication.code.ilike(f"%{keyword}%")) |
            (InvoiceApplication.buyer_name.ilike(f"%{keyword}%"))
        )
    
    if status:
        query = query.where(InvoiceApplication.status == status)
    
    # 获取总数
    count_query = select(func.count(InvoiceApplication.id))
    if keyword:
        count_query = count_query.where(
            (InvoiceApplication.code.ilike(f"%{keyword}%")) |
            (InvoiceApplication.buyer_name.ilike(f"%{keyword}%"))
        )
    if status:
        count_query = count_query.where(InvoiceApplication.status == status)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(InvoiceApplication.created_at.desc())
    
    result = await db.execute(query)
    apps = result.scalars().all()
    
    return ResponseSchema(data={
        "items": [build_invoice_app_response(a) for a in apps],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("", response_model=ResponseSchema)
async def list_invoices(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    status: str = None,
    current_user: User = Depends(require_permissions(["invoice:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取发票列表"""
    query = select(Invoice).options(
        selectinload(Invoice.contract),
        selectinload(Invoice.issuer)
    )
    
    if keyword:
        query = query.where(
            (Invoice.invoice_no.ilike(f"%{keyword}%")) |
            (Invoice.buyer_name.ilike(f"%{keyword}%"))
        )
    
    if status:
        query = query.where(Invoice.status == status)
    
    # 获取总数
    count_query = select(func.count(Invoice.id))
    if keyword:
        count_query = count_query.where(
            (Invoice.invoice_no.ilike(f"%{keyword}%")) |
            (Invoice.buyer_name.ilike(f"%{keyword}%"))
        )
    if status:
        count_query = count_query.where(Invoice.status == status)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Invoice.issue_date.desc())
    
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    return ResponseSchema(data={
        "items": [build_invoice_response(inv) for inv in invoices],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.post("/applications", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_invoice_application(
    data: dict,
    current_user: User = Depends(require_permissions(["invoice:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建开票申请"""
    # 检查申请编号
    result = await db.execute(
        select(InvoiceApplication).where(InvoiceApplication.code == data.get("code"))
    )
    if result.scalar_one_or_none():
        return ResponseSchema(code=400, message="申请编号已存在")
    
    # 设置申请人
    data["applicant_id"] = current_user.id
    
    app = InvoiceApplication(**data)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    
    return ResponseSchema(data=build_invoice_app_response(app), message="申请提交成功")


@router.post("/{application_id}/approve", response_model=ResponseSchema)
async def approve_invoice_application(
    application_id: int,
    data: dict = None,
    current_user: User = Depends(require_permissions(["invoice:approve"])),
    db: AsyncSession = Depends(get_db)
):
    """审批开票申请"""
    result = await db.execute(
        select(InvoiceApplication).where(InvoiceApplication.id == application_id)
    )
    app = result.scalar_one_or_none()
    
    if not app:
        return ResponseSchema(code=404, message="申请不存在")
    
    app.status = "approved"
    app.approver_id = current_user.id
    app.approve_time = datetime.now()
    if data and data.get("comment"):
        app.approve_comment = data.get("comment")
    
    await db.commit()
    await db.refresh(app)
    
    return ResponseSchema(data=build_invoice_app_response(app), message="审批通过")


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: dict,
    current_user: User = Depends(require_permissions(["invoice:create"])),
    db: AsyncSession = Depends(get_db)
):
    """开具发票"""
    # 检查发票号码
    result = await db.execute(
        select(Invoice).where(Invoice.invoice_no == data.get("invoice_no"))
    )
    if result.scalar_one_or_none():
        return ResponseSchema(code=400, message="发票号码已存在")
    
    data["issuer_id"] = current_user.id
    
    invoice = Invoice(**data)
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    
    return ResponseSchema(data=build_invoice_response(invoice), message="开票成功")


@router.put("/{invoice_id}", response_model=ResponseSchema)
async def update_invoice(
    invoice_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["invoice:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新发票"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")
    
    for key, value in data.items():
        if hasattr(invoice, key) and key != "id":
            setattr(invoice, key, value)
    
    await db.commit()
    await db.refresh(invoice)
    
    return ResponseSchema(data=build_invoice_response(invoice), message="更新成功")


@router.delete("/{invoice_id}", response_model=ResponseSchema)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(require_permissions(["invoice:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除发票"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        return ResponseSchema(code=404, message="发票不存在")
    
    await db.delete(invoice)
    await db.commit()
    
    return ResponseSchema(message="删除成功")
