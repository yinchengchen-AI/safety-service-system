"""
系统管理模型 - 日志、配置
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class LogType(str, Enum):
    """日志类型"""
    LOGIN = "login"              # 登录
    LOGOUT = "logout"            # 登出
    CREATE = "create"            # 创建
    UPDATE = "update"            # 更新
    DELETE = "delete"            # 删除
    QUERY = "query"              # 查询
    EXPORT = "export"            # 导出
    IMPORT = "import"            # 导入
    OTHER = "other"              # 其他


class LoginLog(Base):
    """登录日志表"""
    __tablename__ = "login_logs"
    
    # 用户信息
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="用户ID")
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="用户名")
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="真实姓名")
    
    # 登录信息
    login_type: Mapped[str] = mapped_column(String(20), default="password", nullable=False, comment="登录方式")
    login_status: Mapped[str] = mapped_column(String(20), nullable=False, comment="登录状态: success/fail")
    
    # 设备信息
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="IP地址")
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="User-Agent")
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="浏览器")
    os: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="操作系统")
    device: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="设备")
    
    # 失败原因
    fail_reason: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="失败原因")
    
    # 登录时间
    login_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="登录时间")


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    # 用户信息
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, comment="用户ID")
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="用户名")
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="真实姓名")
    
    # 操作信息
    log_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="操作类型")
    module: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作模块")
    action: Mapped[str] = mapped_column(String(100), nullable=False, comment="操作动作")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="操作描述")
    
    # 请求信息
    request_method: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="请求方法")
    request_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="请求URL")
    request_params: Mapped[str | None] = mapped_column(Text, nullable=True, comment="请求参数")
    response_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="响应数据")
    
    # 设备信息
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="IP地址")
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="User-Agent")
    
    # 执行信息
    execution_time: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="执行时间(ms)")
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment="操作状态: success/fail")
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    
    # 操作时间
    operation_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="操作时间")


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    # 配置项
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="配置键")
    value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置值")
    
    # 描述
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="配置名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="配置描述")
    
    # 分组
    group: Mapped[str] = mapped_column(String(50), default="general", nullable=False, comment="配置分组")
    
    # 类型
    type: Mapped[str] = mapped_column(String(20), default="string", nullable=False, comment="值类型: string/int/float/bool/json")
    
    # 是否可编辑
    is_editable: Mapped[bool] = mapped_column(default=True, nullable=False, comment="是否可编辑")
    
    # 排序
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False, comment="排序")
