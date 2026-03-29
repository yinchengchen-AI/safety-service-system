"""
文档管理模型
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DocumentType(str, Enum):
    """文档类型"""
    CONTRACT = "contract"        # 合同文档
    REPORT = "report"            # 报告文档
    CERTIFICATE = "certificate"  # 资质证书
    TRAINING = "training"        # 培训资料
    POLICY = "policy"            # 政策法规
    OTHER = "other"              # 其他


class DocumentStatus(str, Enum):
    """文档状态"""
    ACTIVE = "active"        # 正常
    ARCHIVED = "archived"    # 已归档
    DISABLED = "disabled"    # 已禁用


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    # 文档信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="文档标题")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="文档描述")
    
    # 分类
    category_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("document_categories.id"), nullable=True, comment="分类ID")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="文档类型")
    
    # 文件信息
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="文件路径")
    file_size: Mapped[int] = mapped_column(default=0, nullable=False, comment="文件大小(字节)")
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="文件类型")
    file_ext: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件扩展名")
    
    # 版本
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False, comment="版本号")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("documents.id"), nullable=True, comment="父文档ID(版本链)")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default=DocumentStatus.ACTIVE, nullable=False, comment="状态")
    
    # 权限
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否公开")
    allow_download: Mapped[bool] = mapped_column(default=True, nullable=False, comment="允许下载")
    
    # 统计
    view_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览次数")
    download_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="下载次数")
    
    # 上传人
    uploader_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, comment="上传人ID")
    
    # 关联关系
    category: Mapped["DocumentCategory"] = relationship("DocumentCategory", lazy="selectin")
    uploader: Mapped["User"] = relationship("User", lazy="selectin")


class DocumentCategory(Base):
    """文档分类表"""
    __tablename__ = "document_categories"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分类名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类编码")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("document_categories.id"), nullable=True, comment="父分类ID")
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False, comment="排序")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    
    # 关联关系
    parent: Mapped["DocumentCategory"] = relationship("DocumentCategory", remote_side="DocumentCategory.id", back_populates="children")
    children: Mapped[list["DocumentCategory"]] = relationship("DocumentCategory", back_populates="parent")


class DocumentShare(Base):
    """文档分享表"""
    __tablename__ = "document_shares"
    
    document_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, comment="文档ID")
    
    # 分享链接
    share_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="分享码")
    share_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="分享链接")
    
    # 分享设置
    password: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="访问密码")
    expire_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期时间")
    max_views: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大浏览次数")
    
    # 统计
    view_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览次数")
    download_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="下载次数")
    
    # 分享人
    sharer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, comment="分享人ID")
