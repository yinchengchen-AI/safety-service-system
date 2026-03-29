"""
客户企业模型
"""
from enum import Enum

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CompanyScale(str, Enum):
    """企业规模"""
    SMALL = "small"      # 小型 (<50人)
    MEDIUM = "medium"    # 中型 (50-300人)
    LARGE = "large"      # 大型 (300-1000人)
    XLARGE = "xlarge"    # 超大型 (>1000人)


class CompanyStatus(str, Enum):
    """客户状态"""
    POTENTIAL = "potential"  # 潜在客户
    ACTIVE = "active"        # 合作中
    INACTIVE = "inactive"    # 暂停合作
    LOST = "lost"            # 流失客户


class Company(Base):
    """客户企业表"""
    __tablename__ = "companies"
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="企业名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="客户编码")
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="企业简称")
    
    # 企业信息
    unified_code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, comment="统一社会信用代码")
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="所属行业")
    scale: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="企业规模")
    
    # 联系信息
    province: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="省份")
    city: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="城市")
    district: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="区县")
    street: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="镇街")
    address: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="详细地址")
    
    # 业务信息
    status: Mapped[str] = mapped_column(String(20), default=CompanyStatus.POTENTIAL, nullable=False, comment="客户状态")
    source: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="客户来源")
    
    # 负责人员
    manager_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="客户经理ID")
    
    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
    
    # 关联关系
    manager: Mapped["User"] = relationship("User", lazy="selectin")
    contacts: Mapped[list["CompanyContact"]] = relationship("CompanyContact", back_populates="company", lazy="selectin")


class CompanyContact(Base):
    """企业联系人表"""
    __tablename__ = "company_contacts"
    
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, comment="企业ID")
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="邮箱")
    position: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="职位")
    department: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="部门")
    
    # 是否为默认联系人
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否主要联系人")
    
    # 关联关系
    company: Mapped["Company"] = relationship("Company", back_populates="contacts")
