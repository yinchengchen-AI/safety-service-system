"""
服务管理模型
"""
from datetime import date, datetime
from enum import Enum

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ServiceStatus(str, Enum):
    """服务状态"""
    PLANNED = "planned"          # 计划中
    SCHEDULED = "scheduled"      # 已排期
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消


class ServiceType(str, Enum):
    """服务类型"""
    ON_SITE = "on_site"          # 现场服务
    REMOTE = "remote"            # 远程服务
    TRAINING = "training"        # 培训服务
    CONSULTING = "consulting"    # 咨询服务
    AUDIT = "audit"              # 审核服务


class Service(Base):
    """服务项目表"""
    __tablename__ = "services"
    
    # 服务编号
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="服务编号")
    
    # 服务信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="服务名称")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="服务类型")
    
    # 关联合同
    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contracts.id"), nullable=False, comment="合同ID")
    
    # 服务期限
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="计划开始日期")
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="计划结束日期")
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="实际开始日期")
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="实际结束日期")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default=ServiceStatus.PLANNED, nullable=False, comment="服务状态")
    
    # 服务内容
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="服务描述")
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True, comment="服务要求")
    deliverables: Mapped[str | None] = mapped_column(Text, nullable=True, comment="交付成果")
    
    # 负责人员
    manager_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="服务负责人ID")
    
    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    
    # 关联关系
    contract: Mapped["Contract"] = relationship("Contract", lazy="selectin")
    manager: Mapped["User"] = relationship("User", lazy="selectin")
    schedules: Mapped[list["ServiceSchedule"]] = relationship("ServiceSchedule", back_populates="service", lazy="selectin")
    records: Mapped[list["ServiceRecord"]] = relationship("ServiceRecord", back_populates="service", lazy="selectin")
    reports: Mapped[list["ServiceReport"]] = relationship("ServiceReport", back_populates="service", lazy="selectin")


class ServiceSchedule(Base):
    """服务排期表"""
    __tablename__ = "service_schedules"
    
    service_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, comment="服务ID")
    
    # 排期信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="排期标题")
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, comment="计划日期")
    scheduled_time: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="计划时间")
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="预计时长(分钟)")
    
    # 服务人员
    staff_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="服务人员ID")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default=ServiceStatus.PLANNED, nullable=False, comment="状态")
    
    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    
    # 关联关系
    service: Mapped["Service"] = relationship("Service", back_populates="schedules")
    staff: Mapped["User"] = relationship("User", lazy="selectin")


class ServiceRecord(Base):
    """服务执行记录表"""
    __tablename__ = "service_records"
    
    service_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, comment="服务ID")
    schedule_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("service_schedules.id"), nullable=True, comment="排期ID")
    
    # 执行信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="记录标题")
    record_date: Mapped[date] = mapped_column(Date, nullable=False, comment="记录日期")
    
    # 服务内容
    work_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="工作内容")
    findings: Mapped[str | None] = mapped_column(Text, nullable=True, comment="发现问题")
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True, comment="整改建议")
    
    # 客户确认
    client_confirm: Mapped[bool] = mapped_column(default=False, nullable=False, comment="客户是否确认")
    client_confirm_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="客户确认时间")
    client_sign: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="客户签名")
    
    # 评价
    satisfaction: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="满意度(1-5)")
    evaluation: Mapped[str | None] = mapped_column(Text, nullable=True, comment="评价内容")
    
    # 记录人
    recorder_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="记录人ID")
    
    # 关联关系
    service: Mapped["Service"] = relationship("Service", back_populates="records")
    recorder: Mapped["User"] = relationship("User", lazy="selectin")


class ServiceReport(Base):
    """服务报告表"""
    __tablename__ = "service_reports"
    
    service_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, comment="服务ID")
    
    # 报告信息
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="报告编号")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="报告标题")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="报告类型")
    
    # 报告内容
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="报告摘要")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="报告内容")
    conclusions: Mapped[str | None] = mapped_column(Text, nullable=True, comment="结论建议")
    
    # 文件
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="报告文件路径")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, comment="状态")
    
    # 编制人
    author_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="编制人ID")
    
    # 审核
    reviewer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="审核人ID")
    review_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审核时间")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审核意见")
    
    # 关联关系
    service: Mapped["Service"] = relationship("Service", back_populates="reports")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], lazy="selectin")
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id], lazy="selectin")
