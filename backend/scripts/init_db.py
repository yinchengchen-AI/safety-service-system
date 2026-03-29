"""
数据库初始化脚本
创建表结构和初始数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_engine, AsyncSessionLocal
from app.models import Base, User, Role, Permission, Department
from app.core.security import get_password_hash


async def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 数据库表创建完成")
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("✓ 数据库已初始化，跳过")
            return
        
        # 创建部门
        dept = Department(
            name="系统管理部",
            code="admin_dept",
            sort_order=1,
            description="系统管理部门"
        )
        session.add(dept)
        await session.flush()
        print(f"✓ 创建部门: {dept.name}")
        
        # 创建权限
        permissions_data = [
            # 用户管理
            {"name": "查看用户", "code": "user:view", "type": "button"},
            {"name": "创建用户", "code": "user:create", "type": "button"},
            {"name": "编辑用户", "code": "user:update", "type": "button"},
            {"name": "删除用户", "code": "user:delete", "type": "button"},
            # 角色管理
            {"name": "查看角色", "code": "role:view", "type": "button"},
            {"name": "创建角色", "code": "role:create", "type": "button"},
            {"name": "编辑角色", "code": "role:update", "type": "button"},
            {"name": "删除角色", "code": "role:delete", "type": "button"},
            # 客户管理
            {"name": "查看客户", "code": "company:view", "type": "button"},
            {"name": "创建客户", "code": "company:create", "type": "button"},
            {"name": "编辑客户", "code": "company:update", "type": "button"},
            {"name": "删除客户", "code": "company:delete", "type": "button"},
            # 合同管理
            {"name": "查看合同", "code": "contract:view", "type": "button"},
            {"name": "创建合同", "code": "contract:create", "type": "button"},
            {"name": "编辑合同", "code": "contract:update", "type": "button"},
            {"name": "删除合同", "code": "contract:delete", "type": "button"},
            {"name": "审批合同", "code": "contract:approve", "type": "button"},
            # 服务管理
            {"name": "查看服务", "code": "service:view", "type": "button"},
            {"name": "创建服务", "code": "service:create", "type": "button"},
            {"name": "编辑服务", "code": "service:update", "type": "button"},
            {"name": "删除服务", "code": "service:delete", "type": "button"},
            # 财务管理
            {"name": "查看开票", "code": "invoice:view", "type": "button"},
            {"name": "申请开票", "code": "invoice:create", "type": "button"},
            {"name": "审批开票", "code": "invoice:approve", "type": "button"},
            {"name": "查看收款", "code": "payment:view", "type": "button"},
            {"name": "登记收款", "code": "payment:create", "type": "button"},
            # 文档管理
            {"name": "查看文档", "code": "document:view", "type": "button"},
            {"name": "上传文档", "code": "document:create", "type": "button"},
            {"name": "编辑文档", "code": "document:update", "type": "button"},
            {"name": "删除文档", "code": "document:delete", "type": "button"},
            # 系统管理
            {"name": "系统配置", "code": "system:config", "type": "button"},
            {"name": "查看日志", "code": "log:view", "type": "button"},
            {"name": "统计报表", "code": "statistics:view", "type": "button"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            perm = Permission(**perm_data)
            session.add(perm)
            permissions.append(perm)
        
        await session.flush()
        print(f"✓ 创建 {len(permissions)} 个权限")
        
        # 创建管理员角色
        admin_role = Role(
            name="管理员",
            code="admin",
            description="系统管理员，拥有所有权限",
            is_system=True,
            sort_order=1,
            permissions=permissions
        )
        session.add(admin_role)
        
        # 创建普通用户角色
        user_role = Role(
            name="普通用户",
            code="user",
            description="普通用户，拥有基本权限",
            is_system=True,
            sort_order=2,
            permissions=[p for p in permissions if ":view" in p.code]
        )
        session.add(user_role)
        
        await session.flush()
        print(f"✓ 创建角色: {admin_role.name}, {user_role.name}")
        
        # 创建超级管理员用户
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            phone="13800138000",
            email="admin@safety.com",
            is_superuser=True,
            status="active",
            department_id=dept.id,
            roles=[admin_role]
        )
        session.add(admin_user)
        
        # 创建测试用户
        test_user = User(
            username="test",
            password_hash=get_password_hash("test123"),
            real_name="测试用户",
            phone="13800138001",
            email="test@safety.com",
            is_superuser=False,
            status="active",
            department_id=dept.id,
            roles=[user_role]
        )
        session.add(test_user)
        
        await session.commit()
        print(f"✓ 创建用户: {admin_user.username}, {test_user.username}")
        print(f"✓ 管理员密码: admin123")
        print(f"✓ 测试用户密码: test123")
    
    print("\n数据库初始化完成!")


if __name__ == "__main__":
    asyncio.run(init_db())
