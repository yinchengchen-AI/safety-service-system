"""
客户管理接口
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permissions
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.models.user import User
from app.models.company import Company, CompanyStatus

router = APIRouter()


def build_company_response(company: Company) -> dict:
    """构建客户响应数据"""
    return {
        "id": company.id,
        "name": company.name,
        "code": company.code,
        "short_name": company.short_name,
        "unified_code": company.unified_code,
        "industry": company.industry,
        "scale": company.scale,
        "province": company.province,
        "city": company.city,
        "district": company.district,
        "street": company.street,
        "address": company.address,
        "status": company.status,
        "source": company.source,
        "manager_id": company.manager_id,
        "remark": company.remark,
        "created_at": company.created_at,
        "updated_at": company.updated_at,
        "manager": {
            "id": company.manager.id,
            "real_name": company.manager.real_name
        } if company.manager else None
    }


@router.get("", response_model=ResponseSchema)
async def list_companies(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    status: str = None,
    district: str = None,
    street: str = None,
    current_user: User = Depends(require_permissions(["company:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取客户列表"""
    # 构建查询
    query = select(Company).options(selectinload(Company.manager))
    
    # 关键词搜索
    if keyword:
        query = query.where(
            (Company.name.ilike(f"%{keyword}%")) |
            (Company.code.ilike(f"%{keyword}%"))
        )
    
    # 状态筛选
    if status:
        query = query.where(Company.status == status)
    
    # 区县筛选
    if district:
        query = query.where(Company.district == district)
    
    # 镇街筛选
    if street:
        query = query.where(Company.street == street)
    
    # 获取总数
    count_query = select(func.count(Company.id))
    if keyword:
        count_query = count_query.where(
            (Company.name.ilike(f"%{keyword}%")) |
            (Company.code.ilike(f"%{keyword}%"))
        )
    if status:
        count_query = count_query.where(Company.status == status)
    if district:
        count_query = count_query.where(Company.district == district)
    if street:
        count_query = count_query.where(Company.street == street)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Company.created_at.desc())
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return ResponseSchema(data={
        "items": [build_company_response(c) for c in companies],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })


@router.get("/{company_id}", response_model=ResponseSchema)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_permissions(["company:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取客户详情"""
    result = await db.execute(
        select(Company)
        .where(Company.id == company_id)
        .options(selectinload(Company.manager))
    )
    company = result.scalar_one_or_none()
    
    if not company:
        return ResponseSchema(code=404, message="客户不存在")
    
    return ResponseSchema(data=build_company_response(company))


@router.post("", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: dict,
    current_user: User = Depends(require_permissions(["company:create"])),
    db: AsyncSession = Depends(get_db)
):
    """创建客户"""
    # 必填字段校验
    if not data.get("name"):
        return ResponseSchema(code=400, message="企业名称不能为空")
    if not data.get("code"):
        return ResponseSchema(code=400, message="客户编码不能为空")
    
    # 检查编码是否已存在
    result = await db.execute(
        select(Company).where(Company.code == data.get("code"))
    )
    if result.scalar_one_or_none():
        return ResponseSchema(code=400, message="客户编码已存在")
    
    # 检查统一社会信用代码
    if data.get("unified_code"):
        result = await db.execute(
            select(Company).where(Company.unified_code == data.get("unified_code"))
        )
        if result.scalar_one_or_none():
            return ResponseSchema(code=400, message="统一社会信用代码已存在")
    
    company = Company(**data)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    
    return ResponseSchema(data=build_company_response(company), message="创建成功")


@router.put("/{company_id}", response_model=ResponseSchema)
async def update_company(
    company_id: int,
    data: dict,
    current_user: User = Depends(require_permissions(["company:update"])),
    db: AsyncSession = Depends(get_db)
):
    """更新客户"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        return ResponseSchema(code=404, message="客户不存在")
    
    # 更新字段
    for key, value in data.items():
        if hasattr(company, key):
            setattr(company, key, value)
    
    await db.commit()
    await db.refresh(company)
    
    return ResponseSchema(data=build_company_response(company), message="更新成功")


@router.delete("/{company_id}", response_model=ResponseSchema)
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_permissions(["company:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """删除客户"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        return ResponseSchema(code=404, message="客户不存在")
    
    await db.delete(company)
    await db.commit()
    
    return ResponseSchema(message="删除成功")


# ==================== 统计接口 ====================

@router.get("/statistics/by-district", response_model=ResponseSchema)
async def get_statistics_by_district(
    current_user: User = Depends(require_permissions(["company:view"])),
    db: AsyncSession = Depends(get_db)
):
    """按区县统计客户数量"""
    result = await db.execute(
        select(
            Company.district,
            func.count(Company.id).label("count")
        )
        .where(Company.district.is_not(None), Company.is_deleted == False)
        .group_by(Company.district)
        .order_by(func.count(Company.id).desc())
    )
    
    data = [{"district": row[0], "count": row[1]} for row in result.all()]
    
    return ResponseSchema(data=data)


@router.get("/statistics/by-street", response_model=ResponseSchema)
async def get_statistics_by_street(
    district: str = None,
    current_user: User = Depends(require_permissions(["company:view"])),
    db: AsyncSession = Depends(get_db)
):
    """按镇街统计客户数量
    
    Args:
        district: 可选，指定区县筛选
    """
    query = select(
        Company.district,
        Company.street,
        func.count(Company.id).label("count")
    ).where(Company.street.is_not(None), Company.is_deleted == False)
    
    if district:
        query = query.where(Company.district == district)
    
    query = query.group_by(Company.district, Company.street)
    query = query.order_by(func.count(Company.id).desc())
    
    result = await db.execute(query)
    
    data = [{
        "district": row[0],
        "street": row[1],
        "count": row[2]
    } for row in result.all()]
    
    return ResponseSchema(data=data)


@router.get("/statistics/district-detail", response_model=ResponseSchema)
async def get_district_detail_statistics(
    current_user: User = Depends(require_permissions(["company:view"])),
    db: AsyncSession = Depends(get_db)
):
    """获取区县详细统计（包含下属镇街）"""
    # 获取所有区县
    result = await db.execute(
        select(Company.district)
        .where(Company.district.is_not(None), Company.is_deleted == False)
        .distinct()
    )
    districts = [row[0] for row in result.all()]
    
    # 为每个区县获取镇街统计
    data = []
    for district in districts:
        # 区县总数
        total_result = await db.execute(
            select(func.count(Company.id))
            .where(Company.district == district, Company.is_deleted == False)
        )
        total = total_result.scalar()
        
        # 镇街分布
        street_result = await db.execute(
            select(Company.street, func.count(Company.id))
            .where(
                Company.district == district,
                Company.street.is_not(None),
                Company.is_deleted == False
            )
            .group_by(Company.street)
            .order_by(func.count(Company.id).desc())
        )
        streets = [{"street": row[0], "count": row[1]} for row in street_result.all()]
        
        data.append({
            "district": district,
            "total": total,
            "streets": streets
        })
    
    # 按总数排序
    data.sort(key=lambda x: x["total"], reverse=True)
    
    return ResponseSchema(data=data)
