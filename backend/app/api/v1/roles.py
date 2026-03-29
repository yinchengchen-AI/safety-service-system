"""
角色管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.crud.user import role_crud
from app.database import get_db
from app.schemas.base import PageResponseSchema, ResponseSchema
from app.schemas.user import RoleCreate, RoleQuery, RoleUpdate
from app.models.user import User, Role

router = APIRouter()


def build_role_response(role: Role) -> dict:
    """构建角色响应数据"""
    # 权限信息
    permissions = []
    for perm in role.permissions:
        permissions.append({
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "type": perm.type,
            "parent_id": perm.parent_id,
            "path": perm.path,
            "icon": perm.icon,
            "sort_order": perm.sort_order,
            "description": perm.description,
        })
    
    return {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "is_system": role.is_system,
        "sort_order": role.sort_order,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "permissions": permissions,
    }


@router.get("", response_model=ResponseSchema)
async def list_roles(
    query: RoleQuery = Depends(),
    current_user: User = Depends(require_permissions(["role:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取角色列表"""
    skip = (query.page - 1) * query.page_size
    
    roles = await role_crud.get_multi(db, skip=skip, limit=query.page_size)
    total = await role_crud.count(db)
    
    # 加载权限并构建响应数据
    role_list = []
    for role in roles:
        role_with_perms = await role_crud.get_with_permissions(db, role.id)
        role_list.append(build_role_response(role_with_perms))
    
    return ResponseSchema(
        data={
            "items": role_list,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "pages": (total + query.page_size - 1) // query.page_size
        }
    )


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(require_permissions(["role:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    # 检查编码是否已存在
    existing = await role_crud.get_by_code(db, role_in.code)
    if existing:
        return ResponseSchema(code=400, message="角色编码已存在")
    
    create_data = role_in.model_dump()
    permission_ids = create_data.pop("permission_ids", [])
    
    role = await role_crud.create_with_permissions(
        db,
        obj_in=create_data,
        permission_ids=permission_ids
    )
    
    # 重新加载角色以获取完整信息
    role = await role_crud.get_with_permissions(db, role.id)
    
    return ResponseSchema(data=build_role_response(role), message="创建成功")


@router.get("/{role_id}", response_model=ResponseSchema)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_permissions(["role:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取角色详情"""
    role = await role_crud.get_with_permissions(db, role_id)
    if not role:
        return ResponseSchema(code=404, message="角色不存在")
    
    return ResponseSchema(data=build_role_response(role))


@router.put("/{role_id}", response_model=ResponseSchema)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    current_user: User = Depends(require_permissions(["role:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    role = await role_crud.get_with_permissions(db, role_id)
    if not role:
        return ResponseSchema(code=404, message="角色不存在")
    
    # 系统内置角色不能修改
    if role.is_system:
        return ResponseSchema(code=403, message="系统内置角色不能修改")
    
    update_data = role_in.model_dump(exclude_unset=True)
    permission_ids = update_data.pop("permission_ids", None)
    
    role = await role_crud.update_with_permissions(
        db,
        db_obj=role,
        obj_in=update_data,
        permission_ids=permission_ids
    )
    
    # 重新加载角色以获取完整信息
    role = await role_crud.get_with_permissions(db, role.id)
    
    return ResponseSchema(data=build_role_response(role), message="更新成功")


@router.delete("/{role_id}", response_model=ResponseSchema)
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_permissions(["role:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    role = await role_crud.get(db, role_id)
    if not role:
        return ResponseSchema(code=404, message="角色不存在")
    
    # 系统内置角色不能删除
    if role.is_system:
        return ResponseSchema(code=403, message="系统内置角色不能删除")
    
    await role_crud.delete(db, id=role_id)
    
    return ResponseSchema(message="删除成功")
