# 安全生产第三方服务业务管理系统

一个完整的业务管理系统，为安全生产第三方服务公司提供用户管理、合同管理、服务管理、财务管理、文档管理等功能。

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - 高性能Web框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - 数据库
- **Redis** - 缓存
- **JWT** - 身份认证
- **Alembic** - 数据库迁移

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

### 2. 本地开发环境

#### 后端

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

#### 前端

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

### 待开发功能

3. **客户管理**
   - 企业客户信息
   - 联系人管理

4. **合同管理**
   - 合同录入、审批、变更
   - 到期预警

5. **服务管理**
   - 服务计划、排期
   - 服务执行记录

6. **财务管理**
   - 开票管理
   - 收款管理
   - 账龄分析

7. **文档管理**
   - 文档上传、分类
   - 权限控制

8. **通知公告**
   - 公告发布
   - 阅读确认

9. **统计分析**
   - 经营看板
   - 财务报表

10. **系统日志**
    - 登录日志
    - 操作日志

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
│   │   ├── core/        # 核心功能（安全、权限等）
│   │   ├── crud/        # 数据库操作
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic模型
│   │   ├── config.py    # 配置
│   │   ├── database.py  # 数据库连接
│   │   └── main.py      # 入口
│   ├── alembic/         # 数据库迁移
│   └── scripts/         # 脚本
├── frontend/             # 前端项目
│   ├── src/
│   │   ├── api/         # API请求
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── stores/      # 状态管理
│   │   └── types/       # TypeScript类型
│   └── package.json
├── docker-compose.yml    # Docker编排
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
- [ ] 客户管理
- [ ] 合同管理
- [ ] 服务管理
- [ ] 财务管理
- [ ] 文档管理
- [ ] 通知公告
- [ ] 统计分析
- [ ] 系统日志

## 许可证

MIT License
