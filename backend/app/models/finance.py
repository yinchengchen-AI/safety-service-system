"""
财务管理模型 - 开票、收款
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InvoiceStatus(str, Enum):
    """发票状态"""

    PENDING = "pending"  # 待开具
    ISSUED = "issued"  # 已开具
    SENT = "sent"  # 已寄送
    RECEIVED = "received"  # 已签收
    CANCELLED = "cancelled"  # 已作废
    RED_FLUSHED = "red_flushed"  # 已红冲


class InvoiceType(str, Enum):
    """发票类型"""

    SPECIAL = "special"  # 增值税专用发票
    NORMAL = "normal"  # 增值税普通发票
    ELECTRONIC = "electronic"  # 电子发票


class PaymentStatus(str, Enum):
    """收款状态"""

    PENDING = "pending"  # 待收款
    PARTIAL = "partial"  # 部分收款
    RECEIVED = "received"  # 已收齐
    OVERDUE = "overdue"  # 已逾期
    WRITTEN_OFF = "written_off"  # 已核销


class PaymentMethod(str, Enum):
    """支付方式"""

    BANK_TRANSFER = "bank_transfer"  # 银行转账
    CASH = "cash"  # 现金
    CHECK = "check"  # 支票
    ONLINE = "online"  # 在线支付
    OTHER = "other"  # 其他


class InvoiceApplication(Base):
    """开票申请表"""

    __tablename__ = "invoice_applications"

    # 申请编号
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="申请编号")

    # 关联合同
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contracts.id"), nullable=False, comment="合同ID"
    )

    # 开票信息
    invoice_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="发票类型")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, comment="开票金额")

    # 购方信息
    buyer_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="购方名称")
    buyer_tax_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="购方税号")
    buyer_address: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="购方地址电话"
    )
    buyer_bank: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="购方开户行及账号"
    )

    # 销方信息（默认本公司）
    seller_name: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="销方名称")
    seller_tax_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="销方税号")

    # 申请状态
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, comment="状态: pending/approved/rejected"
    )

    # 申请人
    applicant_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, comment="申请人ID"
    )

    # 审批信息
    approver_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, comment="审批人ID"
    )
    approve_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="审批时间"
    )
    approve_comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审批意见")

    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    contract: Mapped["Contract"] = relationship("Contract", lazy="selectin")
    applicant: Mapped["User"] = relationship("User", foreign_keys=[applicant_id], lazy="selectin")
    approver: Mapped["User"] = relationship("User", foreign_keys=[approver_id], lazy="selectin")


class Invoice(Base):
    """发票表"""

    __tablename__ = "invoices"

    # 发票号码
    invoice_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="发票号码"
    )
    invoice_code: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="发票代码")

    # 关联
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contracts.id"), nullable=False, comment="合同ID"
    )
    application_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("invoice_applications.id"), nullable=True, comment="申请ID"
    )

    # 发票信息
    type: Mapped[str] = mapped_column(String(20), nullable=False, comment="发票类型")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, comment="发票金额")
    tax_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, comment="税额"
    )

    # 开票日期
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开票日期")

    # 购方信息
    buyer_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="购方名称")
    buyer_tax_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="购方税号")

    # 销方信息
    seller_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="销方名称")
    seller_tax_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="销方税号")

    # 状态
    status: Mapped[str] = mapped_column(
        String(20), default=InvoiceStatus.PENDING, nullable=False, comment="状态"
    )

    # 收款统计（冗余字段，便于查询）
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), default=Decimal("0"), nullable=False, comment="已收款金额"
    )

    # 寄送信息
    send_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="寄送日期")
    express_company: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="快递公司"
    )
    express_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="快递单号")

    # 开票人
    issuer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, comment="开票人ID"
    )

    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    contract: Mapped["Contract"] = relationship(
        "Contract", back_populates="invoices", lazy="selectin"
    )
    issuer: Mapped["User"] = relationship("User", lazy="selectin")

    # 关联收款
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="invoice")


class InvoiceItem(Base):
    """发票明细表"""

    __tablename__ = "invoice_items"

    invoice_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, comment="发票ID"
    )

    # 明细信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="项目名称")
    specification: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="规格型号"
    )
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="单位")
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True, comment="数量")
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True, comment="单价")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, comment="金额")
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="税率")
    tax_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, comment="税额"
    )


class PaymentPlan(Base):
    """回款计划表"""

    __tablename__ = "payment_plans"

    # 关联合同
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contracts.id"), nullable=False, comment="合同ID"
    )

    # 计划信息
    plan_no: Mapped[int] = mapped_column(default=1, nullable=False, comment="期数")
    plan_date: Mapped[date] = mapped_column(Date, nullable=False, comment="计划回款日期")
    plan_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, comment="计划回款金额"
    )

    # 实际回款
    actual_amount: Mapped[Decimal] = mapped_column(default=0, nullable=False, comment="已回款金额")
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="实际回款日期")

    # 状态
    status: Mapped[str] = mapped_column(
        String(20), default=PaymentStatus.PENDING, nullable=False, comment="状态"
    )

    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    contract: Mapped["Contract"] = relationship("Contract", lazy="selectin")


class PaymentStatus(str, Enum):
    """收款状态"""

    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    VERIFIED = "verified"  # 已核销
    CANCELLED = "cancelled"  # 已取消


class Payment(Base):
    """收款记录表"""

    __tablename__ = "payments"

    # 收款编号
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="收款编号")

    # 关联
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("contracts.id"), nullable=False, comment="合同ID"
    )
    plan_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("payment_plans.id"), nullable=True, comment="回款计划ID"
    )
    invoice_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("invoices.id"), nullable=True, comment="关联发票ID"
    )

    # 收款状态
    status: Mapped[str] = mapped_column(
        String(20), default=PaymentStatus.PENDING, nullable=False, comment="收款状态"
    )

    # 收款信息
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, comment="收款金额")
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, comment="收款日期")
    method: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="收款方式")

    # 付款方信息
    payer_name: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="付款方名称")
    payer_account: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="付款账号"
    )
    payer_bank: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="付款银行")

    # 我方账户
    receiver_account: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="收款账号"
    )
    receiver_bank: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="收款银行"
    )

    # 凭证
    voucher_no: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="凭证号")

    # 登记人
    recorder_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True, comment="登记人ID"
    )

    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    contract: Mapped["Contract"] = relationship(
        "Contract", back_populates="payments", lazy="selectin"
    )
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments", lazy="selectin")
    recorder: Mapped["User"] = relationship("User", lazy="selectin")
