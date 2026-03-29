#!/bin/bash
# 基础设施启动脚本 - PostgreSQL, Redis, MinIO

set -e

echo "=========================================="
echo "  基础设施服务启动脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo "[1/5] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}错误: Docker 服务未运行${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 环境正常${NC}"

# 检查 Docker Compose
echo ""
echo "[2/5] 检查 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}警告: docker-compose 未找到，尝试使用 docker compose${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi
echo -e "${GREEN}✓ Docker Compose 可用${NC}"

# 创建网络和数据目录
echo ""
echo "[3/5] 准备数据目录..."
mkdir -p init-scripts
echo -e "${GREEN}✓ 数据目录准备完成${NC}"

# 拉取镜像
echo ""
echo "[4/5] 拉取所需镜像..."
echo "    这可能需要几分钟，请耐心等待..."

# 尝试拉取镜像，如果失败则跳过（可能已存在）
docker pull postgres:15-alpine 2>/dev/null || echo -e "${YELLOW}  ⚠ postgres 镜像拉取失败或已存在${NC}"
docker pull redis:7-alpine 2>/dev/null || echo -e "${YELLOW}  ⚠ redis 镜像拉取失败或已存在${NC}"
docker pull minio/minio:latest 2>/dev/null || echo -e "${YELLOW}  ⚠ minio 镜像拉取失败或已存在${NC}"

echo -e "${GREEN}✓ 镜像准备完成${NC}"

# 启动服务
echo ""
echo "[5/5] 启动基础设施服务..."
$COMPOSE_CMD -f docker-compose.infra.yml down 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.infra.yml up -d

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  基础设施服务启动成功!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "服务访问信息:"
echo ""
echo "  📦 PostgreSQL 数据库"
echo "     主机: localhost:5432"
echo "     数据库: safety_service"
echo "     用户名: postgres"
echo "     密码: postgres123"
echo ""
echo "  🔴 Redis 缓存"
echo "     主机: localhost:6379"
echo "     密码: redis123"
echo ""
echo "  📁 MinIO 文件存储"
echo "     API 地址: http://localhost:9000"
echo "     控制台: http://localhost:9001"
echo "     Access Key: minioadmin"
echo "     Secret Key: minioadmin123"
echo ""
echo "常用命令:"
echo "  查看状态: docker-compose -f docker-compose.infra.yml ps"
echo "  查看日志: docker-compose -f docker-compose.infra.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose.infra.yml down"
echo ""
echo "数据库连接测试:"
echo "  docker exec -it safety-service-db psql -U postgres -d safety_service -c '\\l'"
echo ""
