"""
合同管理模型
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ContractStatus(str, Enum):
    """合同状态"""
    DRAFT = "draft"              # 草稿
    PENDING = "pending"          # 待审批
    APPROVED = "approved"        # 已审批
    SIGNED = "signed"            # 已签订
    EXECUTING = "executing"      # 执行中
    COMPLETED = "completed"      # 已完成
    TERMINATED = "terminated"    # 已终止
    EXPIRED = "expired"          # 已过期


class ContractType(str, Enum):
    """合同类型"""
    SAFETY_EVALUATION = "safety_evaluation"      # 安全评价
    SAFETY_CONSULTING = "safety_consulting"      # 安全咨询
    SAFETY_TRAINING = "safety_training"          # 安全培训
    HAZARD_ASSESSMENT = "hazard_assessment"      # 隐患排查
    EMERGENCY_PLAN = "emergency_plan"            # 应急预案
    OTHER = "other"                              # 其他


class Contract(Base):
    """合同表"""
    __tablename__ = "contracts"
    
    # 合同编号
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="合同编号")
    
    # 合同信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="合同名称")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="合同类型")
    
    # 金额
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, comment="合同金额")
    
    # 财务统计（冗余字段，便于查询）
    invoiced_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"), nullable=False, comment="已开票金额")
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"), nullable=False, comment="已收款金额")
    
    # 客户
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("companies.id"), nullable=False, comment="客户ID")
    
    # 期限
    sign_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="签订日期")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="开始日期")
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="结束日期")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default=ContractStatus.DRAFT, nullable=False, comment="合同状态")
    
    # 服务内容
    service_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="服务内容")
    service_cycle: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="服务周期")
    service_times: Mapped[int] = mapped_column(default=1, nullable=False, comment="服务次数")
    
    # 付款条款
    payment_terms: Mapped[str | None] = mapped_column(Text, nullable=True, comment="付款条款")
    
    # 负责人员
    manager_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="负责人ID")
    
    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    
    # 关联关系
    company: Mapped["Company"] = relationship("Company", lazy="selectin")
    manager: Mapped["User"] = relationship("User", lazy="selectin")
    attachments: Mapped[list["ContractAttachment"]] = relationship("ContractAttachment", back_populates="contract", lazy="selectin")
    status_history: Mapped[list["ContractStatusHistory"]] = relationship("ContractStatusHistory", back_populates="contract", lazy="selectin")
    
    # 开票和收款关联
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="contract", lazy="selectin")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="contract", lazy="selectin")


class ContractAttachment(Base):
    """合同附件表"""
    __tablename__ = "contract_attachments"
    
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, comment="合同ID")
    
    # 文件信息
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="文件路径")
    file_size: Mapped[int] = mapped_column(default=0, nullable=False, comment="文件大小(字节)")
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="文件类型")
    
    # 关联关系
    contract: Mapped["Contract"] = relationship("Contract", back_populates="attachments")


class ContractStatusHistory(Base):
    """合同状态变更历史表"""
    __tablename__ = "contract_status_history"
    
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, comment="合同ID")
    
    # 变更信息
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="原状态")
    new_status: Mapped[str] = mapped_column(String(20), nullable=False, comment="新状态")
    
    # 操作人
    operator_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="操作人ID")
    operator_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="操作人姓名")
    
    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    
    # 关联关系
    contract: Mapped["Contract"] = relationship("Contract", back_populates="status_history")
