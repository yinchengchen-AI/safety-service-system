"""
认证接口
"""
from datetime import timedelta
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.crud.user import user_crud
from app.database import get_db
from app.schemas.base import ResponseSchema
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserPasswordUpdate,
    UserProfileOut,
    UserProfileUpdate,
    UserResetPassword,
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=ResponseSchema[LoginResponse])
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查询用户
    user = await user_crud.get_by_username(db, login_data.username)
    
    if not user or not verify_password(login_data.password, user.password_hash):
        # 记录登录失败日志
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # 更新登录信息
    from datetime import datetime
    user.last_login_at = datetime.now()
    user.last_login_ip = request.client.host if request.client else None
    user.login_fail_count = 0
    await db.flush()
    
    # 构建响应
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
    
    # 手动构建部门信息，避免 ORM 懒加载问题
    dept_info = None
    if user.department:
        dept_info = {
            "id": user.department.id,
            "name": user.department.name,
            "code": user.department.code,
            "parent_id": user.department.parent_id,
            "sort_order": user.department.sort_order,
            "description": user.department.description,
        }
    
    user_profile = UserProfileOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        phone=user.phone,
        email=user.email,
        avatar=user.avatar,
        department=dept_info,
        roles=[role.name for role in user.roles],
        permissions=list(permissions)
    )
    
    return ResponseSchema(
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile
        )
    )


@router.post("/refresh", response_model=ResponseSchema[dict])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌"""
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据"
        )
    
    # 验证用户是否存在
    user = await user_crud.get(db, int(user_id))
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return ResponseSchema(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    )


@router.get("/profile", response_model=ResponseSchema[UserProfileOut])
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    permissions = set()
    for role in current_user.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
    
    # 手动构建部门信息
    dept_info = None
    if current_user.department:
        dept_info = {
            "id": current_user.department.id,
            "name": current_user.department.name,
            "code": current_user.department.code,
            "parent_id": current_user.department.parent_id,
            "sort_order": current_user.department.sort_order,
            "description": current_user.department.description,
        }
    
    return ResponseSchema(
        data=UserProfileOut(
            id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            phone=current_user.phone,
            email=current_user.email,
            avatar=current_user.avatar,
            department=dept_info,
            roles=[role.name for role in current_user.roles],
            permissions=list(permissions)
        )
    )


@router.put("/password", response_model=ResponseSchema)
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.flush()
    
    return ResponseSchema(message="密码修改成功")


@router.post("/logout", response_model=ResponseSchema)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出（前端清除token即可）"""
    # 这里可以添加token黑名单逻辑
    return ResponseSchema(message="登出成功")


@router.put("/profile", response_model=ResponseSchema[UserProfileOut])
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户个人资料"""
    # 更新用户信息
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.flush()
    await db.refresh(current_user)
    
    # 构建响应
    permissions = set()
    for role in current_user.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
    
    dept_info = None
    if current_user.department:
        dept_info = {
            "id": current_user.department.id,
            "name": current_user.department.name,
            "code": current_user.department.code,
            "parent_id": current_user.department.parent_id,
            "sort_order": current_user.department.sort_order,
            "description": current_user.department.description,
        }
    
    return ResponseSchema(
        data=UserProfileOut(
            id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            phone=current_user.phone,
            email=current_user.email,
            avatar=current_user.avatar,
            department=dept_info,
            roles=[role.name for role in current_user.roles],
            permissions=list(permissions)
        ),
        message="个人资料更新成功"
    )


@router.post("/avatar", response_model=ResponseSchema)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传用户头像"""
    # 验证文件类型
    allowed_extensions = {"jpg", "jpeg", "png", "gif"}
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}"
        )
    
    # 验证文件大小 (最大 5MB)
    max_size = 5 * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制（最大5MB）"
        )
    
    # 创建上传目录
    upload_dir = os.path.join(os.getcwd(), "uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 删除旧头像（如果存在且不是默认头像）
    if current_user.avatar:
        old_filename = current_user.avatar.split("/")[-1]
        old_file_path = os.path.join(upload_dir, old_filename)
        if os.path.exists(old_file_path) and old_filename.startswith(f"{current_user.id}_"):
            os.remove(old_file_path)
    
    # 更新用户头像URL
    avatar_url = f"/api/uploads/avatars/{unique_filename}"
    current_user.avatar = avatar_url
    await db.flush()
    
    return ResponseSchema(
        data={"avatar_url": avatar_url},
        message="头像上传成功"
    )
