# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

安全生产第三方服务业务管理系统 (Safety Service Management System) - A full-stack business management system for safety production service companies, built with FastAPI backend and React frontend.

**Current Status**: 11+ modules completed including user management, customer management, contract management, service management, finance management, document management, and operation logs.

## Architecture

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
- **Entry point**: `backend/app/main.py` - FastAPI application with CORS, logging, and operation log middleware
- **Database**: SQLAlchemy 2.0 async ORM with PostgreSQL
- **Authentication**: JWT-based auth with RBAC (Role-Based Access Control)
- **API structure**: RESTful APIs under `backend/app/api/v1/`
- **Models**: 11 domain modules in `backend/app/models/` (user, company, contract, service, finance, document, notice, system, attachment)
- **Permissions**: Enum-based permission codes in `backend/app/core/permissions.py` with PermissionChecker dependency
- **Operation Logs**: Automatic logging via middleware in `backend/app/core/middleware.py` with Chinese module names and descriptions

### Frontend (React 18 + TypeScript + Ant Design)
- **State management**: Zustand for global state, TanStack Query for server state
- **UI**: Ant Design 5 with Pro Components for advanced tables/forms
- **Routing**: React Router 6 with auth guards
- **API layer**: Axios-based API clients in `frontend/src/api/`
- **Form Style**: Block-based form design (color-coded sections)

### Infrastructure
- **Containerization**: Docker Compose orchestrates PostgreSQL, Redis, MinIO, backend, and frontend
- **File storage**: MinIO for document management
- **Caching**: Redis for session and data caching
- **Database migrations**: Alembic
- **Scripts**: `dev-start.sh` and `manage-infra.sh` for development workflow

## Development Commands

### Quick Start (Recommended)

```bash
# Start infrastructure (PostgreSQL, Redis, MinIO)
./manage-infra.sh start

# Start development servers (backend + frontend)
./dev-start.sh
```

### Backend

```bash
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database with default users (admin/admin123, test/test123)
python scripts/init_db.py

# Run development server
uvicorn app.main:app --reload

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Code quality (if dev dependencies installed)
black .
ruff check .
mypy app/
pytest
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint and format
npm run lint
npm run format

# Type check
npx tsc --noEmit
```

### Docker

```bash
# Start all services (recommended for full stack)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Infrastructure Management

```bash
# Check infrastructure status
./manage-infra.sh status

# Stop infrastructure
./manage-infra.sh stop

# Access PostgreSQL
./manage-infra.sh psql

# Access Redis
./manage-infra.sh redis-cli
```

## Key Patterns

### Backend API Development
- All API routes go in `backend/app/api/v1/`
- Use CRUD base classes from `backend/app/crud/base.py`
- Pydantic schemas in `backend/app/schemas/`
- Permission checks via `PermissionChecker` dependency injection
- Database sessions via `get_db()` dependency from `backend/app/database.py`
- Operation logs are automatically recorded by middleware

### Frontend Page Development
- Pages in `frontend/src/pages/` follow module structure (e.g., `UserManagement/UserList/`)
- Each page has `index.tsx` and `style.css`
- Use ProTable/ProForm from `@ant-design/pro-components` for CRUD interfaces
- API calls through centralized clients in `frontend/src/api/`
- Auth state managed by `authStore` (Zustand)
- **Form Design**: Use block-based layout with color-coded sections (green for basic, blue for business, orange for location, purple for other)

### Permission System
- Permission codes defined in `PermissionCode` enum
- Format: `resource:action` (e.g., `user:create`, `contract:approve`)
- Superuser bypasses all permission checks
- Regular users inherit permissions from assigned roles

### Operation Log System
- Module names mapped to Chinese in `backend/app/core/middleware.py` `MODULE_NAME_MAP`
- Descriptions auto-generated based on HTTP method and action
- Logs include: user, module, action, description, request info, execution time, status

## Access Points

- Frontend: http://localhost:5173 (dev) or http://localhost (docker)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Default Credentials

- Admin: `admin` / `admin123` (superuser, all permissions)
- Test User: `test` / `test123` (view-only permissions)

## Module Status

**Completed**: 
- User/Role/Permission management
- Dashboard
- Customer management (with Hangzhou district/street cascader)
- Contract management (block-style form)
- Invoice management
- Payment management
- Service management (block-style form)
- Document management (upload, categories, permissions, preview)
- Operation logs (Chinese module names & descriptions)
- Attachment management

**In Progress**: 
- Notifications
- Statistics
- Login logs

## Code Style Guidelines

### Backend
- Use async/await for all database operations
- Use type hints (Python 3.11+)
- Follow PEP 8 style guide
- Use absolute imports (`from app.models import ...`)

### Frontend
- Use TypeScript strict mode
- Use functional components with hooks
- Follow Ant Design design patterns
- Use CSS modules or styled-components for styles

## Git Workflow

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add xxx feature"

# Push to remote
git push origin main
```

**Note**: Dependencies (venv, node_modules) and logs are excluded from git via `.gitignore`.
