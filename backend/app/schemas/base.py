"""
基础Schema
"""
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """基础Schema"""
    model_config = ConfigDict(from_attributes=True)


class BaseOutSchema(BaseSchema):
    """基础输出Schema"""
    id: int
    created_at: datetime
    updated_at: datetime


class PaginationSchema(BaseSchema, Generic[T]):
    """分页Schema"""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class ResponseSchema(BaseSchema, Generic[T]):
    """统一响应Schema"""
    code: int = 200
    message: str = "success"
    data: T | None = None


class ListResponseSchema(BaseSchema, Generic[T]):
    """列表响应Schema"""
    code: int = 200
    message: str = "success"
    data: list[T] | None = None


class PageResponseSchema(BaseSchema, Generic[T]):
    """分页响应Schema"""
    code: int = 200
    message: str = "success"
    data: PaginationSchema[T] | None = None
