"""
数据模型导出
"""
from app.models.base import Base
from app.models.user import User, Role, Permission, Department, user_role_table, role_permission_table
from app.models.company import Company, CompanyContact
from app.models.contract import Contract, ContractAttachment, ContractStatusHistory
from app.models.service import Service, ServiceSchedule, ServiceRecord, ServiceReport
from app.models.finance import Invoice, InvoiceItem, InvoiceApplication, Payment, PaymentPlan
from app.models.document import Document, DocumentCategory, DocumentShare
from app.models.attachment import Attachment
from app.models.notice import Notice, NoticeReadStatus
from app.models.system import OperationLog, LoginLog, SystemConfig

__all__ = [
    "Base",
    # 用户权限
    "User", "Role", "Permission", "Department",
    "user_role_table", "role_permission_table",
    # 客户
    "Company", "CompanyContact",
    # 合同
    "Contract", "ContractAttachment", "ContractStatusHistory",
    # 服务
    "Service", "ServiceSchedule", "ServiceRecord", "ServiceReport",
    # 财务
    "Invoice", "InvoiceItem", "InvoiceApplication", "Payment", "PaymentPlan",
    # 文档
    "Document", "DocumentCategory", "DocumentShare",
    # 附件
    "Attachment",
    # 公告
    "Notice", "NoticeReadStatus",
    # 系统
    "OperationLog", "LoginLog", "SystemConfig",
]
