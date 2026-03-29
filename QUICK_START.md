# 快速开始指南

## 1. 环境准备

确保已安装：
- Docker & Docker Compose
- 或 Python 3.11+ 和 Node.js 18+

## 2. 使用 Docker 快速启动

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
- MinIO 控制台: http://localhost:9001 (minioadmin/minioadmin123)

## 3. 本地开发环境

### 后端开发

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
# 编辑 .env 文件

# 初始化数据库
python scripts/init_db.py

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 4. 默认登录账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 超级管理员 |
| test | test123 | 普通用户 |

## 5. 项目功能

### 已实现功能
- ✅ 用户登录/登出
- ✅ JWT 认证
- ✅ 用户管理 (CRUD)
- ✅ 角色管理 (RBAC权限)
- ✅ 部门管理
- ✅ 工作台 (数据统计、待办、动态)
- ✅ 客户管理
- ✅ 合同管理
- ✅ 开票管理

### 待开发功能
- 🚧 服务管理
- 🚧 收款管理
- 🚧 文档管理
- 🚧 通知公告
- 🚧 统计分析
- 🚧 系统日志

## 6. 常用命令

```bash
# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看数据库
docker-compose exec postgres psql -U postgres -d safety_service

# 查看Redis
docker-compose exec redis redis-cli

# 后端代码格式化
cd backend && black app && ruff check app

# 前端代码格式化
cd frontend && npm run format
```

## 7. 项目结构说明

```
safety-service-system/
├── backend/              # 后端项目 (Python FastAPI)
│   ├── app/
│   │   ├── api/v1/      # API路由
│   │   ├── core/        # 安全、权限、异常
│   │   ├── crud/        # 数据库操作
│   │   ├── models/      # SQLAlchemy模型
│   │   └── schemas/     # Pydantic模型
│   └── scripts/         # 初始化脚本
│
├── frontend/             # 前端项目 (React + TS)
│   └── src/
│       ├── api/         # API请求
│       ├── components/  # 组件
│       ├── pages/       # 页面
│       └── stores/      # 状态管理
│
└── docker-compose.yml    # Docker编排
```

## 8. 常见问题

### Q: 数据库连接失败？
A: 检查 `.env` 文件中的数据库连接字符串，确保 PostgreSQL 已启动。

### Q: 前端无法访问后端API？
A: 检查 `frontend/vite.config.ts` 中的代理配置，确保后端端口正确。

### Q: 如何重置管理员密码？
A: 运行 `python scripts/init_db.py` 重新初始化数据库。

### Q: 如何添加新模块？
A: 参考 `backend/app/models/` 和 `frontend/src/pages/` 中的现有模块。

## 9. 技术支持

如有问题，请查看：
- API 文档: http://localhost:8000/docs
- 项目状态: PROJECT_STATUS.md
- README: README.md
