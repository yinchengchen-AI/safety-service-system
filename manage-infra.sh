#!/bin/bash
# 基础设施管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPOSE_FILE="docker-compose.infra.yml"

# 显示帮助信息
show_help() {
    echo "=========================================="
    echo "  基础设施管理脚本"
    echo "=========================================="
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start       启动所有基础设施服务"
    echo "  stop        停止所有基础设施服务"
    echo "  restart     重启所有基础设施服务"
    echo "  status      查看服务状态"
    echo "  logs        查看服务日志"
    echo "  clean       清理数据和卷（谨慎使用）"
    echo "  psql        进入 PostgreSQL 命令行"
    echo "  redis-cli   进入 Redis 命令行"
    echo "  test        测试服务连接"
    echo "  help        显示帮助信息"
    echo ""
}

# 启动服务
start_services() {
    echo -e "${BLUE}启动基础设施服务...${NC}"
    docker-compose -f $COMPOSE_FILE up -d
    
    echo ""
    echo -e "${GREEN}服务启动成功！${NC}"
    echo ""
    echo "访问地址:"
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis:      localhost:6379"
    echo "  MinIO API:  localhost:9000"
    echo "  MinIO 控制台: http://localhost:9001"
    echo ""
}

# 停止服务
stop_services() {
    echo -e "${YELLOW}停止基础设施服务...${NC}"
    docker-compose -f $COMPOSE_FILE down
    echo -e "${GREEN}服务已停止${NC}"
}

# 重启服务
restart_services() {
    echo -e "${YELLOW}重启基础设施服务...${NC}"
    docker-compose -f $COMPOSE_FILE restart
    echo -e "${GREEN}服务已重启${NC}"
}

# 查看状态
show_status() {
    echo -e "${BLUE}服务状态:${NC}"
    echo ""
    docker-compose -f $COMPOSE_FILE ps
    echo ""
}

# 查看日志
show_logs() {
    docker-compose -f $COMPOSE_FILE logs -f
}

# 清理数据
clean_data() {
    echo -e "${RED}警告: 这将删除所有数据！${NC}"
    read -p "确定要继续吗？(yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose -f $COMPOSE_FILE down -v
        echo -e "${GREEN}数据已清理${NC}"
    else
        echo "操作已取消"
    fi
}

# 进入 PostgreSQL
enter_psql() {
    docker exec -it safety-service-db psql -U postgres -d safety_service
}

# 进入 Redis
enter_redis() {
    docker exec -it safety-service-redis redis-cli -a redis123
}

# 测试连接
test_connection() {
    echo -e "${BLUE}测试服务连接...${NC}"
    echo ""
    
    # 测试 PostgreSQL
    echo -n "PostgreSQL: "
    if docker exec safety-service-db pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 连接正常${NC}"
    else
        echo -e "${RED}✗ 连接失败${NC}"
    fi
    
    # 测试 Redis
    echo -n "Redis:      "
    if docker exec safety-service-redis redis-cli -a redis123 ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 连接正常${NC}"
    else
        echo -e "${RED}✗ 连接失败${NC}"
    fi
    
    # 测试 MinIO
    echo -n "MinIO:      "
    if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 连接正常${NC}"
    else
        echo -e "${RED}✗ 连接失败${NC}"
    fi
    
    echo ""
}

# 主逻辑
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_data
        ;;
    psql)
        enter_psql
        ;;
    redis-cli)
        enter_redis
        ;;
    test)
        test_connection
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        echo "使用 '$0 help' 查看帮助"
        exit 1
        ;;
esac
