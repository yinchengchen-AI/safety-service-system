"""
MinIO 文件存储服务
"""
from io import BytesIO
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinIOService:
    """MinIO 服务类"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        file_size: int = -1
    ) -> str:
        """
        上传文件
        
        Args:
            file_data: 文件数据
            object_name: 对象名称（路径）
            content_type: 文件类型
            file_size: 文件大小
            
        Returns:
            文件路径
        """
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                length=file_size,
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"上传文件失败: {e}")
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """
        获取预签名 URL（用于下载/预览）
        
        Args:
            object_name: 对象名称
            expires: 过期时间（秒）
            
        Returns:
            预签名 URL
        """
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
        except S3Error as e:
            raise Exception(f"生成链接失败: {e}")
    
    def delete_file(self, object_name: str) -> bool:
        """
        删除文件
        
        Args:
            object_name: 对象名称
            
        Returns:
            是否成功
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"删除文件失败: {e}")
            return False
    
    def get_file(self, object_name: str) -> BytesIO:
        """
        获取文件内容
        
        Args:
            object_name: 对象名称
            
        Returns:
            文件内容
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return BytesIO(response.read())
        except S3Error as e:
            raise Exception(f"获取文件失败: {e}")


# 全局实例
minio_service = MinIOService()
