"""
附件管理模型
用于合同、发票等业务的文件附件
"""
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Attachment(Base):
    """附件表"""
    __tablename__ = "attachments"
    
    # 文件名
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="存储路径(MinIO)")
    file_size: Mapped[int] = mapped_column(default=0, nullable=False, comment="文件大小(字节)")
    file_type: Mapped[str] = mapped_column(String(100), nullable=False, comment="MIME类型")
    file_ext: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件扩展名")
    
    # 关联业务对象
    ref_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="关联类型: contract/invoice")
    ref_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="关联对象ID")
    
    # 描述
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="文件描述")
    
    # 上传人
    uploader_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, comment="上传人ID")
    uploader: Mapped["User"] = relationship("User", lazy="selectin")
