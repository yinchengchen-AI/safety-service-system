# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

安全生产第三方服务业务管理系统 (Safety Service Management System) - A full-stack business management system for safety production service companies, built with FastAPI backend and React frontend.

## Architecture

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
- **Entry point**: `backend/app/main.py` - FastAPI application with CORS, logging, and operation log middleware
- **Database**: SQLAlchemy 2.0 async ORM with PostgreSQL
- **Authentication**: JWT-based auth with RBAC (Role-Based Access Control)
- **API structure**: RESTful APIs under `backend/app/api/v1/`
- **Models**: 9 domain modules in `backend/app/models/` (user, company, contract, service, finance, document, notice, system)
- **Permissions**: Enum-based permission codes in `backend/app/core/permissions.py` with PermissionChecker dependency

### Frontend (React 18 + TypeScript + Ant Design)
- **State management**: Zustand for global state, TanStack Query for server state
- **UI**: Ant Design 5 with Pro Components for advanced tables/forms
- **Routing**: React Router 6 with auth guards
- **API layer**: Axios-based API clients in `frontend/src/api/`

### Infrastructure
- **Containerization**: Docker Compose orchestrates PostgreSQL, Redis, MinIO, backend, and frontend
- **File storage**: MinIO for document management
- **Caching**: Redis for session and data caching
- **Database migrations**: Alembic

## Development Commands

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

## Key Patterns

### Backend API Development
- All API routes go in `backend/app/api/v1/`
- Use CRUD base classes from `backend/app/crud/base.py`
- Pydantic schemas in `backend/app/schemas/`
- Permission checks via `PermissionChecker` dependency injection
- Database sessions via `get_db()` dependency from `backend/app/database.py`

### Frontend Page Development
- Pages in `frontend/src/pages/` follow module structure (e.g., `UserManagement/UserList/`)
- Each page has `index.tsx` and `style.css`
- Use ProTable/ProForm from `@ant-design/pro-components` for CRUD interfaces
- API calls through centralized clients in `frontend/src/api/`
- Auth state managed by `authStore` (Zustand)

### Permission System
- Permission codes defined in `PermissionCode` enum
- Format: `resource:action` (e.g., `user:create`, `contract:approve`)
- Superuser bypasses all permission checks
- Regular users inherit permissions from assigned roles

## Access Points

- Frontend: http://localhost (port 80)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Default Credentials

- Admin: `admin` / `admin123` (superuser, all permissions)
- Test User: `test` / `test123` (view-only permissions)

## Module Status

**Completed**: User/Role/Permission management, Dashboard, Customer management, Contract management, Invoice management

**In Progress**: Service management, Payment management, Document management, Notifications, Statistics, System logs
