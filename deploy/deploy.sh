#!/bin/bash
# 自动部署脚本 - 适用于云服务器（阿里云/腾讯云/AWS 等）

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
APP_NAME="chatbot"
APP_DIR="/opt/chatbot"
REPO_URL="https://github.com/Allaniiibigdevil/OpenHandsCreate.git"
BRANCH="guidebot"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}客服机器人自动部署脚本${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 用户或 sudo 运行此脚本${NC}"
    exit 1
fi

# 1. 安装依赖
echo -e "${YELLOW}[1/7] 安装系统依赖...${NC}"
apt-get update -qq
apt-get install -y git python3 python3-pip python3-venv -qq

# 2. 创建应用目录
echo -e "${YELLOW}[2/7] 创建应用目录...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# 3. 克隆或更新代码
if [ -d ".git" ]; then
    echo -e "${YELLOW}[3/7] 更新代码...${NC}"
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo -e "${YELLOW}[3/7] 克隆代码...${NC}"
    git clone -b $BRANCH $REPO_URL .
fi

# 4. 创建虚拟环境并安装依赖
echo -e "${YELLOW}[4/7] 安装 Python 依赖...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q

# 5. 配置文件检查
echo -e "${YELLOW}[5/7] 检查配置文件...${NC}"
if [ ! -f "config.yaml" ]; then
    echo -e "${RED}错误: config.yaml 不存在${NC}"
    echo -e "${YELLOW}请复制 config.example.yaml 为 config.yaml 并填入配置${NC}"
    cp config.example.yaml config.yaml
    echo -e "${YELLOW}配置文件已创建，请编辑 $APP_DIR/config.yaml${NC}"
    exit 1
fi

if [ ! -f "data/knowledge_base.json" ]; then
    echo -e "${YELLOW}知识库文件不存在，使用示例文件${NC}"
    cp data/knowledge_base.example.json data/knowledge_base.json
fi

# 6. 创建 systemd 服务
echo -e "${YELLOW}[6/7] 配置 systemd 服务...${NC}"
cat > /etc/systemd/system/chatbot.service <<EOF
[Unit]
Description=Customer Service ChatBot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$APP_DIR/logs/chatbot.log
StandardError=append:$APP_DIR/logs/chatbot.error.log

[Install]
WantedBy=multi-user.target
EOF

# 7. 启动服务
echo -e "${YELLOW}[7/7] 启动服务...${NC}"
systemctl daemon-reload
systemctl enable chatbot
systemctl restart chatbot

# 检查服务状态
sleep 2
if systemctl is-active --quiet chatbot; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ 部署成功！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "服务状态: ${GREEN}运行中${NC}"
    echo -e "应用目录: $APP_DIR"
    echo -e "日志文件: $APP_DIR/logs/chatbot.log"
    echo ""
    echo -e "常用命令:"
    echo -e "  查看状态: ${YELLOW}systemctl status chatbot${NC}"
    echo -e "  查看日志: ${YELLOW}tail -f $APP_DIR/logs/chatbot.log${NC}"
    echo -e "  重启服务: ${YELLOW}systemctl restart chatbot${NC}"
    echo -e "  停止服务: ${YELLOW}systemctl stop chatbot${NC}"
else
    echo -e "${RED}================================${NC}"
    echo -e "${RED}❌ 部署失败${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo -e "请查看日志: ${YELLOW}journalctl -u chatbot -n 50${NC}"
    exit 1
fi
