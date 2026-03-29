"""
API路由V1版本
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth, users, roles, departments, permissions, 
    companies, contracts, invoices, dashboard, attachments, finance, logs
)

api_router = APIRouter(prefix="/v1")

# 认证相关
api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])

# 用户管理
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(departments.router, prefix="/departments", tags=["部门管理"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])

# 客户管理
api_router.include_router(companies.router, prefix="/companies", tags=["客户管理"])

# 合同管理
api_router.include_router(contracts.router, prefix="/contracts", tags=["合同管理"])

# 开票管理
api_router.include_router(invoices.router, prefix="/invoices", tags=["开票管理"])

# Dashboard 统计
api_router.include_router(dashboard.router, prefix="/statistics", tags=["统计分析"])

# 附件管理
api_router.include_router(attachments.router, prefix="/attachments", tags=["附件管理"])

# 财务管理（开票、收款）
api_router.include_router(finance.router, prefix="/finance", tags=["财务管理"])

# 日志管理
api_router.include_router(logs.router, prefix="/logs", tags=["日志管理"])
