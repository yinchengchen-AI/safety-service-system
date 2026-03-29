# Safety Service System - AGENTS.md

> 本文件面向 AI 编程助手，记录项目架构、技术栈、开发规范及常用操作。阅读者应对本项目一无所知。

---

## 项目概述

**安全生产第三方服务业务管理系统**（Safety Service Management System）是一套为安全生产第三方服务公司打造的全栈业务管理系统，采用 FastAPI + React 技术栈。

- **项目根目录**: `/Users/yinchengchen/code/safety-service-system`
- **后端目录**: `backend/`
- **前端目录**: `frontend/`
- **主要文档**: `README.md`、`PROJECT_STATUS.md`、`QUICK_START.md`、`CLAUDE.md`

### 已完成模块
- 用户角色权限管理（RBAC）
- 工作台（Dashboard）
- 客户管理
- 合同管理
- 开票管理

### 待开发模块
- 服务管理、收款管理、文档管理、通知公告、统计分析、系统日志

---

## 技术栈

### 后端
| 技术 | 版本/说明 |
|------|----------|
| Python | >= 3.11 |
| FastAPI | 0.110+ |
| SQLAlchemy | 2.0（异步 ORM） |
| PostgreSQL | 15+ |
| Redis | 7（缓存） |
| MinIO | 文件存储 |
| Alembic | 数据库迁移 |
| JWT | `python-jose` + `passlib`（SHA256 + salt） |
| Celery | 5.3+（任务队列，已配置） |
| 日志 | `loguru` |

### 前端
| 技术 | 版本/说明 |
|------|----------|
| React | 18 |
| TypeScript | 5 |
| Ant Design | 5 + `@ant-design/pro-components` |
| 状态管理 | Zustand（持久化到 localStorage） |
| 服务端状态 | TanStack Query（React Query） |
| 路由 | React Router 6 |
| 构建工具 | Vite 5 |
| 图表 | `@ant-design/charts` |

### 基础设施与部署
- **容器化**: Docker + Docker Compose
- **编排文件**:
  - `docker-compose.yml` — 全栈启动（含后端、前端、PostgreSQL、Redis、MinIO）
  - `docker-compose.infra.yml` — 仅启动基础设施
- **启动脚本**:
  - `dev-start.sh` — 本地开发一键启动（先启基础设施，再启后端+前端）
  - `manage-infra.sh` — 基础设施管理（start/stop/psql/redis-cli/test 等）
  - `start.sh` — 基础启动说明脚本

---

## 目录结构

```
safety-service-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # 全局依赖：get_current_user、权限检查
│   │   │   └── v1/              # API 路由（按模块拆分）
│   │   │       ├── __init__.py  # 路由聚合
│   │   │       ├── auth.py      # 认证接口
│   │   │       ├── users.py
│   │   │       ├── roles.py
│   │   │       ├── departments.py
│   │   │       ├── permissions.py
│   │   │       ├── companies.py
│   │   │       ├── contracts.py
│   │   │       ├── invoices.py
│   │   │       ├── finance.py
│   │   │       ├── dashboard.py
│   │   │       └── attachments.py
│   │   ├── core/                # 核心功能
│   │   │   ├── security.py      # JWT、密码哈希
│   │   │   ├── permissions.py   # PermissionCode 枚举、PermissionChecker
│   │   │   ├── middleware.py    # 请求日志、操作日志中间件
│   │   │   └── exceptions.py
│   │   ├── crud/                # 数据库操作
│   │   │   ├── base.py          # CRUDBase 泛型基类（软删除）
│   │   │   └── user.py
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── base.py          # Base 基类（含 id/created_at/updated_at/is_deleted）
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── contract.py
│   │   │   ├── service.py
│   │   │   ├── finance.py
│   │   │   ├── document.py
│   │   │   ├── attachment.py
│   │   │   ├── notice.py
│   │   │   └── system.py
│   │   ├── schemas/             # Pydantic Schema
│   │   │   ├── base.py          # ResponseSchema、PaginationSchema 等统一响应结构
│   │   │   └── user.py
│   │   ├── services/            # 业务服务层
│   │   │   └── minio_service.py
│   │   ├── config.py            # Pydantic Settings 配置
│   │   ├── database.py          # 同步/异步引擎、Session、get_db
│   │   ├── deps.py              # 向后兼容导出（实际逻辑在 api/deps.py）
│   │   └── main.py              # FastAPI 入口
│   ├── alembic/                 # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── init_db.py           # 数据库初始化（含默认账号）
│   ├── tests/                   # 测试目录
│   ├── uploads/                 # 本地文件上传目录
│   ├── pyproject.toml           # 项目配置、工具链配置
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios 封装 + 各模块 API
│   │   │   ├── api.ts           # axios 实例、拦截器（含 token 刷新队列）
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   └── ...
│   │   ├── components/          # 公共组件
│   │   │   ├── Layout/
│   │   │   │   ├── MainLayout.tsx   # 侧边栏 + 顶部导航
│   │   │   │   └── style.css
│   │   │   └── AttachmentList/
│   │   ├── pages/               # 页面（按模块组织）
│   │   │   ├── Dashboard/
│   │   │   ├── Login/
│   │   │   ├── UserManagement/
│   │   │   ├── CustomerManagement/
│   │   │   ├── ContractManagement/
│   │   │   ├── ServiceManagement/
│   │   │   ├── FinanceManagement/
│   │   │   ├── DocumentManagement/
│   │   │   └── Profile/
│   │   ├── stores/              # Zustand 状态管理
│   │   │   ├── authStore.ts     # 认证状态（含 persist + hydration 处理）
│   │   │   └── index.ts
│   │   ├── types/               # TypeScript 类型定义
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── hooks/
│   │   ├── App.tsx              # 路由定义 + 路由守卫
│   │   └── main.tsx             # React 挂载入口
│   ├── package.json
│   ├── vite.config.ts           # Vite 配置（含 /api 代理到 localhost:8000）
│   ├── tsconfig.json            # paths: @/* -> src/*
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.infra.yml
├── dev-start.sh
├── manage-infra.sh
└── start.sh
```

---

## 构建与运行命令

### 方式一：Docker Compose（完整环境）

```bash
# 启动所有服务（数据库、Redis、MinIO、后端、前端）
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止
docker-compose down
```

### 方式二：本地开发（推荐日常开发）

```bash
# 1. 启动基础设施
./manage-infra.sh start

# 2. 一键启动前后端（会创建 venv、安装依赖、初始化数据库）
./dev-start.sh
```

手动分步启动：

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 若 .env 不存在，可 cp ../.env.infra .env
python scripts/init_db.py
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### 常用命令速查

```bash
# 数据库迁移
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1

# 后端代码格式化
cd backend && black app && ruff check app

# 前端代码格式化
cd frontend && npm run format

# 进入 PostgreSQL
./manage-infra.sh psql

# 进入 Redis
./manage-infra.sh redis-cli
```

---

## 开发规范与代码风格

### 后端
- **格式化**: `black`，行宽 **100**
- **Lint**: `ruff`（规则: E, F, I, N, W, UP, B, C4, SIM）
- **类型检查**: `mypy`，`disallow_untyped_defs = true`
- **测试**: `pytest` + `pytest-asyncio`，测试目录 `backend/tests/`
- **导入风格**: 使用绝对导入（如 `from app.config import settings`）

### 前端
- **Lint**: `eslint`（`@typescript-eslint` + `react-hooks` + `react-refresh`）
- **格式化**: `prettier`，格式化 `src/**/*.{ts,tsx,css}`
- **路径别名**: `@/` 映射到 `src/`
- **组件组织**: 每个页面目录下包含 `index.tsx` + `style.css`

### 通用约定
- **语言**: 项目主要使用中文进行注释和文档编写。
- **API 响应格式**: 统一使用 `ResponseSchema[T]`（`code=200` 表示成功，`message` 为提示信息）。
- **权限编码格式**: `resource:action`，例如 `user:create`、`contract:approve`。
- **删除策略**: 后端所有模型继承 `Base`，默认使用**软删除**（`is_deleted = True`），`CRUDBase.delete()` 为软删除，`hard_delete()` 为硬删除。
- **模型基类字段**: `id`（BigInteger 自增）、`created_at`、`updated_at`、`is_deleted`。

---

## 核心架构模式

### 后端 API 开发模式
1. 所有路由放在 `backend/app/api/v1/`
2. 使用 `backend/app/api/deps.py` 中的依赖进行认证和权限校验：
   - `get_current_user` — 获取当前用户
   - `PermissionRequired(["user:create"])` — 权限检查（超级管理员自动 bypass）
3. 数据库操作继承 `CRUDBase`（`backend/app/crud/base.py`）
4. Pydantic Schema 放在 `backend/app/schemas/`
5. 数据库会话通过 `get_db()` 依赖注入，使用 SQLAlchemy 2.0 异步会话

### 前端页面开发模式
1. 页面放在 `frontend/src/pages/`，按模块分子目录
2. 使用 `ProTable` / `ProForm`（来自 `@ant-design/pro-components`）做 CRUD 界面
3. API 调用通过 `frontend/src/api/` 下的模块进行
4. 认证状态使用 `authStore`（Zustand + persist），token 刷新逻辑在 `api.ts` 拦截器中实现
5. 路由守卫在 `App.tsx` 中实现，`MainLayout.tsx` 负责侧边栏菜单和面包屑

### 权限系统
- 权限码定义在 `backend/app/core/permissions.py` 的 `PermissionCode` 枚举
- 前端菜单项也绑定 `permission` 字段用于控制显示
- 超级管理员（`is_superuser = true`）绕过所有权限检查

---

## 测试说明

- 后端测试使用 `pytest`，配置在 `pyproject.toml` 中：
  - `asyncio_mode = "auto"`
  - 测试路径: `testpaths = ["tests"]`
- 运行命令:
  ```bash
  cd backend
  pytest
  ```
- 目前 `backend/tests/` 目录存在，但测试覆盖率有限，新增模块时应补充对应测试。

---

## 安全与认证

### JWT 认证
- Access Token 有效期: **8 小时**（`ACCESS_TOKEN_EXPIRE_MINUTES = 480`）
- Refresh Token 有效期: **7 天**
- 算法: `HS256`
- Secret Key 通过环境变量 `SECRET_KEY` 注入

### 密码策略
- 使用 SHA256 + 随机 salt（非 bcrypt），格式: `salt:hash`
- 最小长度: 6 位（`PASSWORD_MIN_LENGTH = 6`）

### 默认账号
| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 超级管理员 |
| test | test123 | 普通用户 |

### 文件上传
- 本地头像上传保存到 `backend/uploads/avatars/`
- 其他附件支持 MinIO 存储
- 允许扩展名: `jpg, jpeg, png, gif, pdf, doc, docx, xls, xlsx, ppt, pptx, txt, zip, rar`
- 最大上传大小: 100MB

### 敏感信息脱敏
- `OperationLogMiddleware` 会自动记录操作日志
- 敏感字段（`password`, `token`, `secret` 等）在日志中已做脱敏处理
- 登录、刷新 token 等路径不记录操作日志

---

## 访问端口

| 服务 | 地址 |
|------|------|
| 前端（Docker） | http://localhost |
| 前端（本地开发） | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档（Swagger） | http://localhost:8000/docs |
| MinIO 控制台 | http://localhost:9001（minioadmin / minioadmin123） |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## 给 AI 助手的特别提示

1. **修改模型后务必生成迁移**: 若更改了 `backend/app/models/` 下的模型，运行 `alembic revision --autogenerate -m "xxx"` 并检查生成的迁移脚本。
2. **新增模块参考现有模块**: 用户管理（`users.py` / `roles.py`）和客户管理（`companies.py`）是最完整的参考实现。
3. **前端页面结构**: 每个新页面建议放在 `frontend/src/pages/{ModuleName}/{PageName}/`，包含 `index.tsx` + `style.css`。
4. **权限码一致性**: 新增后端权限时，同步更新 `PermissionCode` 枚举、前端菜单配置以及路由/按钮的权限控制。
5. **保持中文注释风格**: 新增代码的注释和文档建议继续使用中文，与现有代码保持一致。

---

*最后更新: 2026-03-29*
