"""
用户、角色、权限模型
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# 关联表
user_role_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permission_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"      # 正常
    INACTIVE = "inactive"  # 禁用
    LOCKED = "locked"      # 锁定


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    # 基本信息
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="真实姓名")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="邮箱")
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="头像URL")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE, nullable=False, comment="状态")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否超级管理员")
    
    # 部门关联
    department_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("departments.id"), nullable=True, comment="部门ID")
    
    # 安全
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="最后登录IP")
    login_fail_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="登录失败次数")
    
    # 关联关系
    department: Mapped["Department"] = relationship("Department", back_populates="users", lazy="selectin")
    roles: Mapped[list["Role"]] = relationship("Role", secondary=user_role_table, back_populates="users", lazy="selectin")
    
    def has_permission(self, permission_code: str) -> bool:
        """检查是否有指定权限"""
        if self.is_superuser:
            return True
        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False
    
    def has_role(self, role_code: str) -> bool:
        """检查是否有指定角色"""
        if self.is_superuser:
            return True
        return any(role.code == role_code for role in self.roles)


class Department(Base):
    """部门表"""
    __tablename__ = "departments"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="部门编码")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("departments.id"), nullable=True, comment="父部门ID")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    
    # 关联关系
    parent: Mapped["Department"] = relationship("Department", remote_side="Department.id", back_populates="children")
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent")
    users: Mapped[list["User"]] = relationship("User", back_populates="department")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色编码")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否系统内置")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")
    
    # 关联关系
    users: Mapped[list["User"]] = relationship("User", secondary=user_role_table, back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship("Permission", secondary=role_permission_table, back_populates="roles", lazy="selectin")


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="权限名称")
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="权限编码")
    type: Mapped[str] = mapped_column(String(20), nullable=False, comment="类型: menu/button/api")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("permissions.id"), nullable=True, comment="父权限ID")
    path: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="路由路径/API路径")
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="图标")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    
    # 关联关系
    parent: Mapped["Permission"] = relationship("Permission", remote_side="Permission.id", back_populates="children")
    children: Mapped[list["Permission"]] = relationship("Permission", back_populates="parent")
    roles: Mapped[list["Role"]] = relationship("Role", secondary=role_permission_table, back_populates="permissions")
