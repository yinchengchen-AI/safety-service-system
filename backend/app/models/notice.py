"""
通知公告模型
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NoticeType(str, Enum):
    """公告类型"""
    NORMAL = "normal"      # 普通公告
    IMPORTANT = "important"  # 重要公告
    URGENT = "urgent"      # 紧急公告


class NoticeStatus(str, Enum):
    """公告状态"""
    DRAFT = "draft"        # 草稿
    PUBLISHED = "published"  # 已发布
    WITHDRAWN = "withdrawn"  # 已撤回
    ARCHIVED = "archived"    # 已归档


class Notice(Base):
    """公告表"""
    __tablename__ = "notices"
    
    # 公告信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="公告标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="公告内容")
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="摘要")
    
    # 类型和状态
    type: Mapped[str] = mapped_column(String(20), default=NoticeType.NORMAL, nullable=False, comment="公告类型")
    status: Mapped[str] = mapped_column(String(20), default=NoticeStatus.DRAFT, nullable=False, comment="公告状态")
    
    # 发布时间
    publish_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="发布时间")
    expire_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="过期时间")
    
    # 置顶
    is_top: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否置顶")
    top_expire_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="置顶过期时间")
    
    # 附件
    attachment: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="附件路径")
    
    # 统计
    view_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览次数")
    
    # 发布人
    publisher_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, comment="发布人ID")
    
    # 关联关系
    publisher: Mapped["User"] = relationship("User", lazy="selectin")


class NoticeReadStatus(Base):
    """公告阅读状态表"""
    __tablename__ = "notice_read_status"
    
    notice_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("notices.id", ondelete="CASCADE"), nullable=False, comment="公告ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    
    # 阅读信息
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否已读")
    read_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="阅读时间")
    
    # 唯一约束
    __table_args__ = (
        {"comment": "公告阅读状态表"},
    )
