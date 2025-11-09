#!/bin/bash
# Docker 部署脚本 - 适用于支持 Docker 的云服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
IMAGE_NAME="chatbot"
CONTAINER_NAME="customer-service-bot"
APP_DIR="/opt/chatbot"
REPO_URL="https://github.com/Allaniiibigdevil/OpenHandsCreate.git"
BRANCH="guidebot"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}客服机器人 Docker 部署脚本${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker 未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose 未安装，正在安装...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 创建应用目录
echo -e "${YELLOW}[1/5] 准备应用目录...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆或更新代码
if [ -d ".git" ]; then
    echo -e "${YELLOW}[2/5] 更新代码...${NC}"
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo -e "${YELLOW}[2/5] 克隆代码...${NC}"
    git clone -b $BRANCH $REPO_URL .
fi

# 配置文件检查
echo -e "${YELLOW}[3/5] 检查配置文件...${NC}"
if [ ! -f "config.yaml" ]; then
    echo -e "${YELLOW}配置文件不存在，创建默认配置${NC}"
    cp config.example.yaml config.yaml
    echo -e "${RED}请编辑 $APP_DIR/config.yaml 填入配置${NC}"
fi

if [ ! -f "data/knowledge_base.json" ]; then
    cp data/knowledge_base.example.json data/knowledge_base.json
fi

# 停止旧容器
echo -e "${YELLOW}[4/5] 停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

# 构建并启动
echo -e "${YELLOW}[5/5] 构建并启动容器...${NC}"
docker-compose build
docker-compose up -d

# 检查状态
sleep 3
if docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "容器状态: ${GREEN}运行中${NC}"
    echo -e "容器名称: $CONTAINER_NAME"
    echo ""
    echo -e "常用命令:"
    echo -e "  查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  查看状态: ${YELLOW}docker-compose ps${NC}"
    echo -e "  重启容器: ${YELLOW}docker-compose restart${NC}"
    echo -e "  停止容器: ${YELLOW}docker-compose down${NC}"
    echo -e "  进入容器: ${YELLOW}docker exec -it $CONTAINER_NAME bash${NC}"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}❌ 部署失败${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo -e "请查看日志: ${YELLOW}docker-compose logs${NC}"
    exit 1
fi
