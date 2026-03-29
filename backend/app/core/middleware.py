"""
中间件 - 日志、异常处理等
"""
import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token
from app.database import AsyncSessionLocal
from app.models.system import LoginLog, OperationLog


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 获取请求信息
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        logger.info(f"Request: {method} {url} from {client_ip}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"Response: {method} {url} - {response.status_code} - {process_time:.3f}s"
            )
            
            # 添加处理时间头
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error: {method} {url} - {str(e)} - {process_time:.3f}s")
            raise


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""
    
    # 不需要记录日志的路径
    EXCLUDE_PATHS = ["/api/v1/auth/login", "/api/v1/auth/refresh", "/health", "/docs", "/openapi.json"]
    
    # 敏感字段，需要脱敏
    SENSITIVE_FIELDS = ["password", "token", "secret", "credit_card", "id_card"]
    
    # 模块名称映射（中文）- 覆盖所有业务模块
    MODULE_NAME_MAP = {
        # 用户权限模块
        "users": "用户",
        "roles": "角色",
        "departments": "部门",
        "permissions": "权限",
        # 客户管理
        "companies": "企业客户",
        "company_contacts": "客户联系人",
        # 合同管理
        "contracts": "合同",
        "contract_attachments": "合同附件",
        "contract_status_history": "合同状态记录",
        # 服务管理
        "services": "服务",
        "service_schedules": "服务计划",
        "service_records": "服务记录",
        "service_reports": "服务报告",
        # 财务管理
        "invoices": "开票申请",
        "invoice_applications": "开票申请",
        "invoice_items": "开票明细",
        "payments": "收款",
        "payment_plans": "收款计划",
        # 文档管理
        "documents": "文档",
        "document_categories": "文档分类",
        "document_shares": "文档分享",
        "attachments": "附件",
        # 系统管理
        "notices": "通知公告",
        "notice_read_status": "公告阅读状态",
        "logs": "日志",
        "login_logs": "登录日志",
        "operation_logs": "操作日志",
        "system_configs": "系统配置",
        "statistics": "统计数据",
        "dashboard": "工作台",
        # 认证
        "auth": "认证",
        "profile": "个人资料",
    }
    
    # 动作名称映射（中文）
    ACTION_NAME_MAP = {
        "login": "登录",
        "logout": "登出",
        "profile": "查看个人资料",
        "password": "修改密码",
        "avatar": "上传头像",
        "refresh": "刷新令牌",
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要记录
        path = request.url.path
        if any(path.startswith(exclude) for exclude in self.EXCLUDE_PATHS):
            return await call_next(request)
        
        start_time = time.time()
        
        # 获取用户信息
        user_id = None
        username = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                username = payload.get("username")
        
        # 执行请求
        response = await call_next(request)
        
        # 计算执行时间
        execution_time = int((time.time() - start_time) * 1000)
        
        # 记录操作日志
        try:
            await self._save_operation_log(
                request=request,
                response=response,
                user_id=user_id,
                username=username,
                execution_time=execution_time
            )
        except Exception as e:
            logger.error(f"保存操作日志失败: {e}")
        
        return response
    
    async def _save_operation_log(
        self,
        request: Request,
        response: Response,
        user_id: str | None,
        username: str | None,
        execution_time: int
    ):
        """保存操作日志"""
        # 确定操作类型
        method = request.method
        log_type = self._get_log_type(method)
        
        # 解析模块和动作
        # 路径格式: /api/v1/{module}/{action_or_id}
        path_parts = request.url.path.strip("/").split("/")
        module, action = self._parse_module_and_action(path_parts)
        
        # 转换为中文模块名
        module_cn = self.MODULE_NAME_MAP.get(module, module)
        
        # 生成中文描述
        description = self._generate_description(method, module_cn, action, path_parts)
        
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")
        
        # 创建日志记录
        log = OperationLog(
            user_id=int(user_id) if user_id else None,
            username=username,
            log_type=log_type,
            module=module_cn,  # 使用中文模块名
            action=action,
            description=description,  # 使用中文描述
            request_method=method,
            request_url=str(request.url),
            ip_address=client_ip,
            user_agent=user_agent,
            execution_time=execution_time,
            status="success" if response.status_code < 400 else "fail"
        )
        
        # 异步保存到数据库
        async with AsyncSessionLocal() as session:
            session.add(log)
            await session.commit()
    
    def _parse_module_and_action(self, path_parts: list) -> tuple:
        """
        解析路径获取模块和动作
        路径格式: /api/v1/{module}/{action_or_id}
        示例: 
          - /api/v1/users -> module=users, action=list
          - /api/v1/users/123 -> module=users, action=detail
          - /api/v1/users/123/roles -> module=roles, action=detail (子资源)
          - /api/v1/auth/login -> module=auth, action=login
        """
        if len(path_parts) < 3:
            return "unknown", "unknown"
        
        # 跳过前缀 (api, v1)
        # 找到版本号后的第一个路径段作为模块
        try:
            # 查找 v1/v2 版本标记
            version_idx = -1
            for i, part in enumerate(path_parts):
                if part.startswith('v') and part[1:].isdigit():
                    version_idx = i
                    break
            
            if version_idx >= 0 and version_idx + 1 < len(path_parts):
                # 模块是版本号后的第一段
                module = path_parts[version_idx + 1]
                # 动作是后面的一段（如果有的话）
                if version_idx + 2 < len(path_parts):
                    action = path_parts[version_idx + 2]
                else:
                    action = "list" if len(path_parts) == version_idx + 2 else "unknown"
            else:
                # 没有版本号，取倒数第二段作为模块
                module = path_parts[-2] if len(path_parts) >= 2 else path_parts[-1]
                action = path_parts[-1] if len(path_parts) >= 2 else "list"
        except Exception:
            module = path_parts[-2] if len(path_parts) >= 2 else "unknown"
            action = path_parts[-1] if path_parts else "unknown"
        
        return module, action
    
    def _get_log_type(self, method: str) -> str:
        """根据HTTP方法获取操作类型"""
        type_map = {
            "GET": "query",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        return type_map.get(method, "other")
    
    def _generate_description(self, method: str, module_cn: str, action: str, path_parts: list) -> str:
        """生成中文操作描述"""
        # 动作类型映射 - 组合后格式: 动作 + 模块
        # 例如: list + 用户 -> 查询用户列表
        action_map = {
            "create": "创建新",
            "update": "更新",
            "delete": "删除",
            "list": "查询",
            "detail": "查看",
            "export": "导出",
            "import": "导入",
            "approve": "审批通过",
            "reject": "驳回",
            "submit": "提交",
            "cancel": "取消",
            "enable": "启用",
            "disable": "禁用",
            "reset": "重置",
            "assign": "分配",
            "transfer": "转移",
            "upload": "上传",
            "download": "下载",
            "preview": "预览",
            "search": "搜索",
            "login": "登录系统",
            "logout": "退出系统",
            "profile": "查看个人资料",
            "password": "修改密码",
            "avatar": "上传头像",
            "refresh": "刷新令牌",
            "modules": "获取模块列表",
        }
        
        # 特殊路径处理
        full_path = "/".join(path_parts)
        
        # 处理数字ID（如 /users/123 -> 查看用户详情）
        if action.isdigit():
            return f"查看{module_cn}详情(ID:{action})"
        
        # 处理子资源（如 /users/123/roles -> 查看用户角色）
        if len(path_parts) >= 5:
            # /api/v1/users/123/roles 这种格式
            parent_resource = path_parts[-3]  # users
            sub_resource = path_parts[-1]      # roles
            parent_cn = self.MODULE_NAME_MAP.get(parent_resource, parent_resource)
            sub_cn = self.MODULE_NAME_MAP.get(sub_resource, sub_resource)
            return f"查看{parent_cn}的{sub_cn}"
        
        # 从动作映射获取描述
        if action in action_map:
            action_cn = action_map[action]
            # 如果动作映射已经包含完整语义，直接使用
            if action in ["login", "logout", "profile", "password", "avatar", "refresh", "modules"]:
                return action_cn
            # list动作特殊处理: "查询用户列表"
            if action == "list":
                return f"{action_cn}{module_cn}列表"
            # 否则组合动作和模块: "创建新用户", "更新用户"
            return f"{action_cn}{module_cn}"
        
        # 默认根据 HTTP 方法生成
        method_map = {
            "GET": "查询",
            "POST": "创建",
            "PUT": "更新",
            "PATCH": "更新",
            "DELETE": "删除"
        }
        method_cn = method_map.get(method, "操作")
        return f"{method_cn}{module_cn}"


class CORSMiddleware:
    """CORS中间件配置（在main.py中配置）"""
    pass
