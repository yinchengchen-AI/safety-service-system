#!/bin/bash
# 开发环境一键启动脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  开发环境一键启动"
echo "=========================================="
echo ""

# 检查基础设施
echo -e "${BLUE}[1/3] 检查基础设施...${NC}"
if ! docker ps | grep -q "safety-service-db"; then
    echo -e "${YELLOW}  基础设施未启动，正在启动...${NC}"
    ./manage-infra.sh start
else
    echo -e "${GREEN}  ✓ 基础设施已运行${NC}"
fi

# 初始化后端
echo ""
echo -e "${BLUE}[2/3] 初始化后端...${NC}"
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "  创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果未安装）
if ! pip show fastapi > /dev/null 2>&1; then
    echo "  安装后端依赖..."
    python -m pip install -r requirements.txt -q
fi

# 复制环境变量
if [ ! -f ".env" ]; then
    echo "  创建环境变量文件..."
    cp ../.env.infra .env
fi

# 初始化数据库
echo "  初始化数据库..."
python scripts/init_db.py 2>/dev/null || echo "  数据库已初始化，跳过"

echo -e "${GREEN}  ✓ 后端准备完成${NC}"

# 启动后端（后台）
echo "  启动后端服务..."
nohup venv/bin/uvicorn app.main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
echo $! > ../.backend.pid
echo -e "${GREEN}  ✓ 后端已启动 (PID: $(cat ../.backend.pid))${NC}"

cd ..

# 启动前端
echo ""
echo -e "${BLUE}[3/3] 启动前端...${NC}"
cd frontend

# 安装依赖（如果未安装）
if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖..."
    npm install
fi

echo -e "${GREEN}  ✓ 前端准备完成${NC}"

cd ..

# 创建日志目录
mkdir -p logs

# 显示访问信息
echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  所有服务已启动！${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "访问地址:"
echo "  🌐 前端界面:  http://localhost:5173"
echo "  📡 后端API:   http://localhost:8000"
echo "  📚 API文档:   http://localhost:8000/docs"
echo ""
echo "默认账号:"
echo "  管理员: admin / admin123"
echo "  测试用户: test / test123"
echo ""
echo "日志文件:"
echo "  后端日志: tail -f logs/backend.log"
echo ""
echo "停止服务:"
echo "  后端: kill $(cat .backend.pid)"
echo "  基础设施: ./manage-infra.sh stop"
echo ""

# 启动前端（前台）
cd frontend && npm run dev
