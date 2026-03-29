"""
用户管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.crud.user import user_crud, role_crud
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User, Role
from app.models.company import Company
from app.models.contract import Contract

router = APIRouter()


@router.get("", response_model=ResponseSchema)
async def list_users(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    dept_id: int = None,
    current_user: User = Depends(require_permissions(["user:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    skip = (page - 1) * page_size
    
    # 构建查询
    query = select(User).options(
        selectinload(User.department),
        selectinload(User.roles)
    )
    
    if keyword:
        query = query.where(
            (User.username.ilike(f"%{keyword}%")) |
            (User.real_name.ilike(f"%{keyword}%"))
        )
    
    if dept_id:
        query = query.where(User.department_id == dept_id)
    
    # 获取总数
    count_query = select(func.count(User.id))
    if keyword:
        count_query = count_query.where(
            (User.username.ilike(f"%{keyword}%")) |
            (User.real_name.ilike(f"%{keyword}%"))
        )
    if dept_id:
        count_query = count_query.where(User.department_id == dept_id)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.offset(skip).limit(page_size)
    query = query.order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # 构建响应
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "email": user.email,
            "avatar": user.avatar,
            "status": user.status,
            "is_superuser": user.is_superuser,
            "department_id": user.department_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "department": {
                "id": user.department.id,
                "name": user.department.name
            } if user.department else None,
            "roles": [{"id": role.id, "name": role.name} for role in user.roles]
        }
        user_list.append(user_dict)
    
    return ResponseSchema(data={
        "items": user_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/{user_id}", response_model=ResponseSchema)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permissions(["user:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.department), selectinload(User.roles))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return ResponseSchema(code=404, message="用户不存在")
    
    user_dict = {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "email": user.email,
        "avatar": user.avatar,
        "status": user.status,
        "is_superuser": user.is_superuser,
        "department_id": user.department_id,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "department": {
            "id": user.department.id,
            "name": user.department.name
        } if user.department else None,
        "roles": [{"id": role.id, "name": role.name} for role in user.roles]
    }
    
    return ResponseSchema(data=user_dict)


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: dict,
    current_user: User = Depends(require_permissions(["user:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    # 检查用户名是否已存在
    existing = await user_crud.get_by_username(db, data.get("username"))
    if existing:
        return ResponseSchema(code=400, message="用户名已存在")
    
    # 创建用户
    user = await user_crud.create(db, obj_in=data)
    
    return ResponseSchema(data={
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "status": user.status
    }, message="创建成功")


@router.put("/{user_id}", response_model=ResponseSchema)
async def update_user(
    user_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["user:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    user = await user_crud.get(db, user_id)
    if not user:
        return ResponseSchema(code=404, message="用户不存在")
    
    # 更新字段
    for key, value in data.items():
        if hasattr(user, key) and key not in ["id", "created_at", "password_hash"]:
            setattr(user, key, value)
    
    await db.flush()
    await db.refresh(user)
    
    return ResponseSchema(data={
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "email": user.email,
    }, message="更新成功")


@router.delete("/{user_id}", response_model=ResponseSchema)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permissions(["user:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    user = await user_crud.get(db, user_id)
    if not user:
        return ResponseSchema(code=404, message="用户不存在")
    
    if user.id == current_user.id:
        return ResponseSchema(code=400, message="不能删除自己")
    
    await user_crud.delete(db, id=user_id)
    
    return ResponseSchema(message="删除成功")


# ==================== 个人中心统计接口 ====================

@router.get("/statistics/mine", response_model=ResponseSchema)
async def get_my_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的统计数据"""
    # 负责客户数
    company_result = await db.execute(
        select(func.count(Company.id))
        .where(Company.manager_id == current_user.id, Company.is_deleted == False)
    )
    company_count = company_result.scalar()
    
    # 处理合同数
    contract_result = await db.execute(
        select(func.count(Contract.id))
        .where(Contract.manager_id == current_user.id, Contract.is_deleted == False)
    )
    contract_count = contract_result.scalar()
    
    return ResponseSchema(data={
        "company_count": company_count,
        "contract_count": contract_count
    })


@router.get("/logs/mine", response_model=ResponseSchema)
async def get_my_logs(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的操作日志"""
    # 这里简化处理，实际应该从操作日志表查询
    # 暂时返回模拟数据
    logs = [
        {"id": 1, "action": "登录系统", "time": "2024-01-15 09:30:00", "ip": "192.168.1.100"},
        {"id": 2, "action": "查看客户列表", "time": "2024-01-15 09:35:00", "ip": "192.168.1.100"},
        {"id": 3, "action": "修改客户信息", "time": "2024-01-15 10:15:30", "ip": "192.168.1.100"},
        {"id": 4, "action": "创建合同", "time": "2024-01-15 14:20:00", "ip": "192.168.1.100"},
        {"id": 5, "action": "导出报表", "time": "2024-01-14 16:45:00", "ip": "192.168.1.100"},
    ]
    
    return ResponseSchema(data={
        "items": logs,
        "total": len(logs),
        "page": page,
        "page_size": page_size,
        "pages": 1
    })
