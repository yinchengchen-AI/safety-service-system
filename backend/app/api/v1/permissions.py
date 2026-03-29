"""
权限管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user, require_permissions
from app.crud.user import permission_crud
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User, Permission

router = APIRouter()


def build_permission_response(perm: Permission) -> dict:
    """构建权限响应数据"""
    return {
        "id": perm.id,
        "name": perm.name,
        "code": perm.code,
        "type": perm.type,
        "parent_id": perm.parent_id,
        "path": perm.path,
        "icon": perm.icon,
        "sort_order": perm.sort_order,
        "description": perm.description,
        "created_at": perm.created_at,
        "updated_at": perm.updated_at,
    }


# 模块映射关系（用于构建树形结构）
MODULE_MAP = {
    "user": "用户管理",
    "role": "角色管理",
    "department": "部门管理",
    "company": "客户管理",
    "contract": "合同管理",
    "service": "服务管理",
    "invoice": "开票管理",
    "payment": "收款管理",
    "document": "文档管理",
    "system": "系统设置",
    "log": "系统日志",
    "statistics": "统计报表",
}


@router.get("/tree", response_model=ResponseSchema)
async def get_permission_tree(
    current_user: User = Depends(require_permissions(["role:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取权限树形列表（按模块分组）"""
    # 查询所有权限
    result = await db.execute(
        select(Permission).order_by(Permission.code)
    )
    all_perms = list(result.scalars().all())
    
    # 按模块分组构建树
    tree_data = []
    module_groups: dict[str, list] = {}
    
    for perm in all_perms:
        # 从 code 中提取模块名（如 user:view -> user）
        module_key = perm.code.split(":")[0] if ":" in perm.code else "other"
        module_name = MODULE_MAP.get(module_key, module_key)
        
        if module_key not in module_groups:
            module_groups[module_key] = {
                "id": f"module_{module_key}",
                "name": module_name,
                "code": module_key,
                "type": "module",
                "children": []
            }
        
        module_groups[module_key]["children"].append(build_permission_response(perm))
    
    # 转换为列表
    tree_data = list(module_groups.values())
    
    return ResponseSchema(data=tree_data)


@router.get("", response_model=ResponseSchema)
async def list_permissions(
    current_user: User = Depends(require_permissions(["role:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取所有权限列表（扁平结构）"""
    perms = await permission_crud.get_multi(db, skip=0, limit=1000)
    
    perm_list = [build_permission_response(perm) for perm in perms]
    
    return ResponseSchema(data=perm_list)


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: dict,
    current_user: User = Depends(require_permissions(["role:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建权限"""
    # 检查编码是否已存在
    existing = await permission_crud.get_by_code(db, data.get("code"))
    if existing:
        return ResponseSchema(code=400, message="权限编码已存在")
    
    perm = await permission_crud.create(db, obj_in=data)
    
    return ResponseSchema(data=build_permission_response(perm), message="创建成功")


@router.put("/{perm_id}", response_model=ResponseSchema)
async def update_permission(
    perm_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["role:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新权限"""
    perm = await permission_crud.get(db, perm_id)
    if not perm:
        return ResponseSchema(code=404, message="权限不存在")
    
    perm = await permission_crud.update(db, db_obj=perm, obj_in=data)
    
    return ResponseSchema(data=build_permission_response(perm), message="更新成功")


@router.delete("/{perm_id}", response_model=ResponseSchema)
async def delete_permission(
    perm_id: int,
    current_user: User = Depends(require_permissions(["role:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除权限"""
    perm = await permission_crud.get(db, perm_id)
    if not perm:
        return ResponseSchema(code=404, message="权限不存在")
    
    await permission_crud.delete(db, id=perm_id)
    
    return ResponseSchema(message="删除成功")
