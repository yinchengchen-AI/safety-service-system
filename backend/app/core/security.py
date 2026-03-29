"""
安全相关功能 - JWT、密码哈希
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - 使用 SHA256 + salt"""
    # 从存储的哈希中提取 salt
    if ":" not in hashed_password:
        return False
    salt, stored_hash = hashed_password.split(":", 1)
    # 计算输入密码的哈希
    pwd_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return secrets.compare_digest(pwd_hash, stored_hash)


def get_password_hash(password: str) -> str:
    """获取密码哈希 - 使用 SHA256 + salt"""
    # 生成随机 salt
    salt = secrets.token_hex(16)
    # 计算哈希
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{pwd_hash}"


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
