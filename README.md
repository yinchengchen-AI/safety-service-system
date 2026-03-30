# 安全生产第三方服务业务管理系统

一个完整的业务管理系统，为安全生产第三方服务公司提供用户管理、客户管理、合同管理、服务管理、财务管理、文档管理、操作日志、通知公告、统计分析、登录日志等功能。

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - 高性能Web框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - 数据库
- **Redis** - 缓存
- **JWT** - 身份认证
- **Alembic** - 数据库迁移
- **MinIO** - 文件存储

### 前端
- **React 18** + **TypeScript**
- **Ant Design 5** - UI组件库
- **Zustand** - 状态管理
- **TanStack Query** - 数据获取
- **Vite** - 构建工具

## 快速开始

### 1. 使用 Docker Compose 启动（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd safety-service-system

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

服务启动后访问:
- 前端: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001

### 2. 本地开发环境

#### 一键启动（推荐开发方式）

```bash
# 1. 启动基础设施（PostgreSQL、Redis、MinIO）
./manage-infra.sh start

# 2. 启动前后端开发服务器
./dev-start.sh
```

#### 手动启动

**后端：**

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
# 编辑 .env 文件配置数据库等

# 初始化数据库
python scripts/init_db.py

# 启动服务
uvicorn app.main:app --reload
```

**前端：**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 功能模块

### 已完成功能

1. **用户角色权限管理 (RBAC)**
   - 用户管理：增删改查、启用禁用、重置密码
   - 角色管理：角色定义、权限分配
   - 权限控制：基于角色的权限控制
   - 部门管理：组织架构

2. **工作台**
   - 数据统计卡片
   - 待办事项
   - 最近动态
   - 快捷入口

3. **客户管理**
   - 企业客户信息（支持杭州市区县镇街级联选择）
   - 客户状态管理（潜在客户、合作中、暂停合作、流失客户）
   - 负责人分配

4. **合同管理**
   - 合同录入、编辑
   - 合同状态管理（草稿、待审批、已审批、已签订、执行中、已完成）
   - 服务次数和周期管理
   - 关联客户

5. **服务管理**
   - 服务记录管理
   - 服务状态跟踪（待执行、执行中、已完成、已取消）
   - 关联合同

6. **财务管理**
   - 开票管理：开票申请、审批流程
   - 收款管理：收款登记、账龄分析
   - 付款条款管理

7. **文档管理**
   - 文档上传、分类管理
   - 文档权限控制（公开/下载权限）
   - 在线预览（图片、PDF）
   - 浏览/下载统计

8. **文档管理**
   - 文档上传、分类管理
   - 文档权限控制（公开/下载权限）
   - 在线预览（图片、PDF）
   - 浏览/下载统计

9. **操作日志**
   - 自动记录所有业务操作
   - 支持按模块、操作类型、状态、时间筛选
   - 中文模块名称和操作描述

10. **通知公告**
    - 公告创建、编辑、发布、撤回、归档
    - 公告置顶、类型管理（普通/重要/紧急）
    - 阅读确认功能
    - 阅读统计和可视化

11. **统计分析**
    - 经营概览统计（客户、合同、收款、服务）
    - 业务趋势分析（按月统计）
    - 财务概览和月度报表
    - 数据可视化图表
    - 系统使用情况统计

12. **登录日志**
    - 登录记录列表查询
    - 多维度筛选（用户名、状态、时间）
    - 登录统计信息

### 待开发功能

- [ ] 报表导出 - 经营报表、财务报表、客户报表导出

## 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 超级管理员 |
| test | test123 | 普通用户 |

## 项目结构

```
safety-service-system/
├── backend/              # 后端项目
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心功能（安全、权限、中间件）
│   │   ├── crud/        # 数据库操作
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic模型
│   │   ├── services/    # 业务服务
│   │   ├── config.py    # 配置
│   │   ├── database.py  # 数据库连接
│   │   └── main.py      # 入口
│   ├── alembic/         # 数据库迁移
│   └── scripts/         # 初始化脚本
├── frontend/             # 前端项目
│   ├── src/
│   │   ├── api/         # API请求
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── stores/      # 状态管理
│   │   └── types/       # TypeScript类型
│   └── package.json
├── docker-compose.yml    # Docker编排
├── dev-start.sh          # 开发启动脚本
├── manage-infra.sh       # 基础设施管理脚本
└── README.md
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看自动生成的API文档（Swagger UI）。

## 开发计划

- [x] 项目架构搭建
- [x] 数据库设计
- [x] 用户认证授权
- [x] 用户角色权限管理
- [x] 前端框架搭建
- [x] 登录页面
- [x] 工作台
- [x] 客户管理
- [x] 合同管理
- [x] 开票管理
- [x] 收款管理
- [x] 服务管理
- [x] 操作日志
- [x] 文档管理
- [x] 通知公告
- [x] 统计分析
- [x] 登录日志
- [ ] 报表导出

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License
