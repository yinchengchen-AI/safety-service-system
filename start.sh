#!/bin/bash
# 安全生产服务管理系统 - 启动脚本

echo "=========================================="
echo "安全生产服务管理系统 - 启动脚本"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "1. 正在启动数据库和缓存服务..."
docker-compose up -d postgres redis minio

# 等待数据库启动
echo "2. 等待数据库启动..."
sleep 5

# 检查数据库是否就绪
echo "3. 检查数据库连接..."
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "   等待 PostgreSQL 就绪..."
    sleep 2
done
echo "   PostgreSQL 已就绪"

echo ""
echo "4. 后端服务启动说明:"
echo "   方式1 - Docker: docker-compose up -d backend"
echo "   方式2 - 本地开发:"
echo "     cd backend"
echo "     python -m venv venv"
echo "     source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo "     python scripts/init_db.py"
echo "     uvicorn app.main:app --reload"
echo ""

echo "5. 前端服务启动说明:"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""

echo "=========================================="
echo "默认账号:"
echo "  管理员: admin / admin123"
echo "  测试用户: test / test123"
echo "=========================================="
