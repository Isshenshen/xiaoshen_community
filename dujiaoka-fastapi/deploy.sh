#!/bin/bash
# ============================================
# 部署脚本 - 独角发卡 FastAPI
# ============================================

set -e

echo "🚀 开始部署独角发卡 FastAPI..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，从模板创建...${NC}"
    cp env.example .env
    echo -e "${YELLOW}请编辑 .env 文件配置必要的环境变量${NC}"
    echo -e "${YELLOW}特别是 SECRET_KEY 和数据库配置${NC}"
    exit 1
fi

# 检查 SECRET_KEY
if grep -q "your-super-secret-key-change-me" .env 2>/dev/null; then
    echo -e "${RED}❌ 请在 .env 文件中设置安全的 SECRET_KEY${NC}"
    echo -e "${YELLOW}可以使用: openssl rand -hex 32${NC}"
    exit 1
fi

# 选择部署模式
echo ""
echo "请选择部署模式:"
echo "1) 开发环境 (带热重载)"
echo "2) 生产环境 (优化构建)"
echo ""
read -p "请输入选项 [1/2]: " mode

case $mode in
    1)
        echo -e "${GREEN}📦 启动开发环境...${NC}"
        docker-compose up -d
        ;;
    2)
        echo -e "${GREEN}📦 启动生产环境...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo ""
echo -e "${GREEN}📊 服务状态:${NC}"
docker-compose ps

# 健康检查
echo ""
echo -e "${YELLOW}🔍 健康检查...${NC}"

# 检查后端
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ 后端服务正常${NC}"
else
    echo -e "${RED}❌ 后端服务异常${NC}"
fi

# 检查前端
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo -e "${GREEN}✅ 前端服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  前端服务可能需要更长启动时间${NC}"
fi

echo ""
echo -e "${GREEN}🎉 部署完成!${NC}"
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost/"
echo "  - 后端 API: http://localhost:8000/"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "默认管理员账号:"
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo -e "${YELLOW}⚠️  首次部署请运行数据初始化:${NC}"
echo "  docker-compose exec backend python init_data.py"

