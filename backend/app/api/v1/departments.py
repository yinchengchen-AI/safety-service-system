"""
部门管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user, require_permissions
from app.crud.user import dept_crud
from app.database import get_db
from app.schemas.base import ResponseSchema, ListResponseSchema
from app.models.user import User, Department

router = APIRouter()


def build_dept_response(dept: Department) -> dict:
    """构建部门响应数据"""
    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "parent_id": dept.parent_id,
        "sort_order": dept.sort_order,
        "description": dept.description,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
    }


@router.get("", response_model=ResponseSchema)
async def list_departments(
    current_user: User = Depends(require_permissions(["department:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取部门列表（树形结构）"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # 获取顶级部门（过滤已删除）
    result = await db.execute(
        select(Department)
        .where(Department.parent_id == None, Department.is_deleted == False)
        .options(selectinload(Department.children))
        .order_by(Department.sort_order)
    )
    top_depts = result.scalars().all()
    
    # 构建树形结构（过滤已删除的子部门）
    def build_tree(dept_list):
        result = []
        for dept in dept_list:
            if dept.is_deleted:
                continue
            node = build_dept_response(dept)
            if dept.children:
                node["children"] = [
                    build_dept_response(child) 
                    for child in dept.children 
                    if not child.is_deleted
                ]
            result.append(node)
        return result
    
    tree_data = build_tree(top_depts)
    
    return ResponseSchema(data=tree_data)


@router.get("/flat", response_model=ResponseSchema)
async def list_departments_flat(
    current_user: User = Depends(require_permissions(["department:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取部门列表（扁平结构，用于下拉选择）"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Department)
        .where(Department.is_deleted == False)
        .order_by(Department.sort_order)
    )
    depts = result.scalars().all()
    
    dept_list = [build_dept_response(dept) for dept in depts]
    
    return ResponseSchema(data=dept_list)


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: dict,
    current_user: User = Depends(require_permissions(["department:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建部门"""
    # 检查编码是否已存在
    existing = await dept_crud.get_by_code(db, data.get("code"))
    if existing:
        return ResponseSchema(code=400, message="部门编码已存在")
    
    dept = await dept_crud.create(db, obj_in=data)
    
    return ResponseSchema(data=build_dept_response(dept), message="创建成功")


@router.put("/{dept_id}", response_model=ResponseSchema)
async def update_department(
    dept_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["department:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新部门"""
    dept = await dept_crud.get(db, dept_id)
    if not dept:
        return ResponseSchema(code=404, message="部门不存在")
    
    dept = await dept_crud.update(db, db_obj=dept, obj_in=data)
    
    return ResponseSchema(data=build_dept_response(dept), message="更新成功")


@router.delete("/{dept_id}", response_model=ResponseSchema)
async def delete_department(
    dept_id: int,
    current_user: User = Depends(require_permissions(["department:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除部门"""
    dept = await dept_crud.get(db, dept_id)
    if not dept:
        return ResponseSchema(code=404, message="部门不存在")
    
    await dept_crud.delete(db, id=dept_id)
    
    return ResponseSchema(message="删除成功")
