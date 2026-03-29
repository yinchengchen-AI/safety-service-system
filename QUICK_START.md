# 快速开始指南

## 1. 环境准备

确保已安装以下软件：
- **Docker & Docker Compose**（推荐）或
- **Python 3.11+** 和 **Node.js 18+**

## 2. 快速启动方式

### 方式一：一键启动（推荐本地开发）

```bash
# 1. 进入项目目录
cd safety-service-system

# 2. 启动基础设施（PostgreSQL、Redis、MinIO）
./manage-infra.sh start

# 3. 一键启动前后端开发服务器
./dev-start.sh
```

访问地址：
- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs
- MinIO 控制台: http://localhost:9001 (minioadmin/minioadmin123)

### 方式二：Docker Compose 启动

```bash
# 1. 进入项目目录
cd safety-service-system

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f backend
```

访问地址：
- 前端界面: http://localhost
- API 文档: http://localhost:8000/docs

### 方式三：手动启动

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 初始化数据库（创建表结构 + 默认账号）
python scripts/init_db.py

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 3. 默认登录账号

| 账号 | 密码 | 角色 | 说明 |
|------|------|------|------|
| admin | admin123 | 超级管理员 | 拥有所有权限，可删除日志 |
| test | test123 | 普通用户 | 基础查看权限 |

## 4. 已实现功能清单

### ✅ 核心功能
- **用户管理** - 增删改查、启用禁用、重置密码
- **角色管理** - 角色定义、权限分配
- **部门管理** - 组织架构管理
- **权限控制** - 基于 RBAC 的权限控制

### ✅ 业务功能
- **客户管理** - 企业客户信息、杭州市区县镇街级联选择
- **合同管理** - 合同录入、状态管理、关联客户
- **服务管理** - 服务记录、状态跟踪
- **开票管理** - 开票申请、审批流程
- **收款管理** - 收款登记、账龄分析

### ✅ 系统功能
- **工作台** - 数据统计、待办事项
- **操作日志** - 自动记录所有业务操作，支持筛选查询
- **附件管理** - 文件上传、预览、下载

## 5. 常用命令

### 基础设施管理

```bash
# 查看基础设施状态
./manage-infra.sh status

# 停止基础设施
./manage-infra.sh stop

# 进入 PostgreSQL
./manage-infra.sh psql

# 进入 Redis
./manage-infra.sh redis-cli
```

### Docker 命令

```bash
# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 重建并启动
docker-compose up -d --build
```

### 后端开发命令

```bash
cd backend

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1

# 代码格式化
black app
ruff check app

# 运行测试
pytest
```

### 前端开发命令

```bash
cd frontend

# 代码格式化
npm run format

# 类型检查
npx tsc --noEmit

# 构建生产版本
npm run build
```

## 6. 项目结构说明

```
safety-service-system/
├── backend/              # 后端项目 (Python FastAPI)
│   ├── app/
│   │   ├── api/v1/      # API路由
│   │   ├── core/        # 安全、权限、中间件
│   │   ├── crud/        # 数据库操作
│   │   ├── models/      # SQLAlchemy模型
│   │   ├── schemas/     # Pydantic模型
│   │   └── services/    # 业务服务
│   ├── alembic/         # 数据库迁移
│   └── scripts/         # 初始化脚本
│
├── frontend/             # 前端项目 (React + TS)
│   └── src/
│       ├── api/         # API请求
│       ├── components/  # 组件
│       ├── pages/       # 页面
│       └── stores/      # 状态管理
│
├── docker-compose.yml    # Docker编排
├── dev-start.sh          # 开发启动脚本
└── manage-infra.sh       # 基础设施管理
```

## 7. 开发 workflow

### 添加新模块的步骤

1. **后端**
   - 在 `backend/app/models/` 创建模型
   - 在 `backend/app/schemas/` 创建 schema
   - 在 `backend/app/api/v1/` 创建 API 路由
   - 在 `backend/app/api/v1/__init__.py` 注册路由

2. **前端**
   - 在 `frontend/src/api/` 创建 API 客户端
   - 在 `frontend/src/pages/` 创建页面
   - 在 `frontend/src/App.tsx` 注册路由
   - 更新菜单配置

3. **权限**
   - 在 `backend/app/core/permissions.py` 添加权限码
   - 在 API 中使用权限装饰器
   - 在前端菜单中配置权限

## 8. 常见问题

### Q: 数据库连接失败？
A: 
1. 检查 `.env` 文件中的数据库连接字符串
2. 确保 PostgreSQL 已启动：`./manage-infra.sh status`
3. 检查端口 5432 是否被占用

### Q: 前端无法访问后端API？
A:
1. 检查 `frontend/vite.config.ts` 中的代理配置
2. 确保后端服务已启动
3. 检查后端端口是否为 8000

### Q: 如何重置管理员密码？
A: 运行 `python scripts/init_db.py` 重新初始化数据库，或使用登录页面的忘记密码功能。

### Q: 如何查看操作日志？
A: 访问系统设置 -> 操作日志，可以查看所有业务操作的详细记录。

### Q: 如何添加新的操作模块到日志？
A: 在 `backend/app/core/middleware.py` 的 `MODULE_NAME_MAP` 中添加模块映射即可。

## 9. 技术支持

如有问题，请查看：
- API 文档: http://localhost:8000/docs
- 项目状态: PROJECT_STATUS.md
- 详细架构: AGENTS.md
- 开发指南: CLAUDE.md
