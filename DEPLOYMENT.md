# 部署指南

本文档提供客服机器人的完整部署方案，支持多种部署方式。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [部署方式](#部署方式)
3. [Docker 部署](#docker-部署)
4. [云服务器部署](#云服务器部署)
5. [自动化部署](#自动化部署)
6. [配置说明](#配置说明)
7. [故障排查](#故障排查)

---

## 🚀 快速开始

### 前置要求

- **操作系统**: Linux (Ubuntu 20.04+, CentOS 7+)
- **Python**: 3.9+ (非 Docker 部署)
- **Docker**: 20.10+ (Docker 部署)
- **内存**: 最低 512MB，推荐 1GB+
- **磁盘**: 最低 1GB

---

## 🎯 部署方式

### 方式对比

| 部署方式 | 难度 | 推荐场景 | 优点 | 缺点 |
|---------|------|---------|------|------|
| **Docker** | ⭐⭐ | 生产环境 | 隔离性好、易管理 | 需要 Docker |
| **直接部署** | ⭐⭐⭐ | 开发/测试 | 简单直接 | 环境依赖多 |
| **自动化部署** | ⭐ | CI/CD | 全自动 | 需配置 |

---

## 🐳 Docker 部署（推荐）

### 方法 1: 使用部署脚本（最简单）

```bash
# 1. 下载部署脚本
curl -O https://raw.githubusercontent.com/Allaniiibigdevil/OpenHandsCreate/guidebot/deploy/docker-deploy.sh

# 2. 运行部署脚本
chmod +x docker-deploy.sh
sudo bash docker-deploy.sh
```

脚本会自动：
- ✅ 安装 Docker 和 Docker Compose
- ✅ 克隆代码
- ✅ 构建镜像
- ✅ 启动容器

### 方法 2: 手动部署

```bash
# 1. 克隆代码
git clone -b guidebot https://github.com/Allaniiibigdevil/OpenHandsCreate.git
cd OpenHandsCreate

# 2. 配置文件
cp config.example.yaml config.yaml
cp data/knowledge_base.example.json data/knowledge_base.json

# 编辑配置文件
vim config.yaml  # 填入 DeepSeek API 密钥

# 3. 启动容器
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### Docker 常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启容器
docker-compose restart

# 停止容器
docker-compose down

# 进入容器
docker exec -it customer-service-bot bash

# 更新代码并重启
git pull origin guidebot
docker-compose build
docker-compose up -d
```

---

## 🖥️ 云服务器部署

### 支持的云平台

- ✅ 阿里云 ECS
- ✅ 腾讯云 CVM
- ✅ AWS EC2
- ✅ Azure VM
- ✅ Google Cloud Compute Engine

### 方法 1: 使用部署脚本（推荐）

```bash
# 1. SSH 登录服务器
ssh root@your-server-ip

# 2. 下载并运行部署脚本
curl -O https://raw.githubusercontent.com/Allaniiibigdevil/OpenHandsCreate/guidebot/deploy/deploy.sh
chmod +x deploy.sh
sudo bash deploy.sh
```

脚本会自动：
- ✅ 安装系统依赖
- ✅ 克隆代码
- ✅ 创建虚拟环境
- ✅ 安装 Python 依赖
- ✅ 配置 systemd 服务
- ✅ 启动服务

### 方法 2: 手动部署

#### 步骤 1: 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y git python3 python3-pip
```

#### 步骤 2: 克隆代码

```bash
sudo mkdir -p /opt/chatbot
cd /opt/chatbot
sudo git clone -b guidebot https://github.com/Allaniiibigdevil/OpenHandsCreate.git .
```

#### 步骤 3: 配置环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置文件
cp config.example.yaml config.yaml
cp data/knowledge_base.example.json data/knowledge_base.json

# 编辑配置
vim config.yaml  # 填入 API 密钥
```

#### 步骤 4: 配置 systemd 服务

```bash
# 复制服务文件
sudo cp deploy/chatbot.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start chatbot
sudo systemctl enable chatbot

# 查看状态
sudo systemctl status chatbot
```

### Systemd 服务管理

```bash
# 启动服务
sudo systemctl start chatbot

# 停止服务
sudo systemctl stop chatbot

# 重启服务
sudo systemctl restart chatbot

# 查看状态
sudo systemctl status chatbot

# 查看日志
sudo journalctl -u chatbot -f

# 查看应用日志
tail -f /opt/chatbot/logs/chatbot.log
```

---

## 🤖 自动化部署（GitHub Actions）

### 配置步骤

#### 1. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

```
Settings → Secrets and variables → Actions → New repository secret
```

**必需的 Secrets**:

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `SERVER_HOST` | 服务器 IP 地址 | `123.45.67.89` |
| `SERVER_USER` | SSH 用户名 | `root` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `SERVER_PORT` | SSH 端口（可选） | `22` |

**可选的 Secrets（Docker Hub）**:

| Secret 名称 | 说明 |
|------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码/Token |

#### 2. 生成 SSH 密钥

```bash
# 在本地生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "deploy@chatbot"

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/id_rsa.pub root@your-server-ip

# 复制私钥内容到 GitHub Secrets
cat ~/.ssh/id_rsa
```

#### 3. 触发部署

自动部署会在以下情况触发：

- ✅ 推送到 `main` 分支
- ✅ 创建版本标签（如 `v1.0.0`）
- ✅ 手动触发（Actions 页面）

```bash
# 推送代码触发部署
git push origin main

# 创建版本标签触发部署
git tag v1.0.0
git push origin v1.0.0

# 或在 GitHub Actions 页面手动触发
```

#### 4. 查看部署状态

访问 GitHub 仓库的 Actions 页面查看部署进度和日志。

---

## ⚙️ 配置说明

### 必需配置

#### 1. DeepSeek API 配置

编辑 `config.yaml`:

```yaml
deepseek:
  api_key: "your-deepseek-api-key-here"  # 必填
  api_base: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
```

获取 API 密钥: [DeepSeek 官网](https://platform.deepseek.com/)

#### 2. 知识库配置

编辑 `data/knowledge_base.json`:

```json
[
  {
    "question": "你们的营业时间？",
    "answer": "周一至周五 9:00-18:00",
    "category": "基本信息",
    "keywords": ["营业时间", "工作时间"]
  }
]
```

### 可选配置

#### 环境变量

```bash
# 设置时区
export TZ=Asia/Shanghai

# 设置日志级别
export LOG_LEVEL=INFO
```

#### 资源限制

Docker Compose 中已配置：
- CPU: 0.5-1 核
- 内存: 256MB-512MB

可根据实际需求调整 `docker-compose.yml`。

---

## 🔍 故障排查

### 常见问题

#### 1. 配置文件不存在

**错误**:
```
FileNotFoundError: 配置文件不存在: config.yaml
```

**解决**:
```bash
cp config.example.yaml config.yaml
vim config.yaml  # 填入配置
```

#### 2. API 调用失败

**错误**:
```
DeepSeek API 调用失败: Unauthorized
```

**解决**:
- 检查 API 密钥是否正确
- 确认 API 额度是否充足
- 检查网络连接

#### 3. 容器无法启动

**检查日志**:
```bash
docker-compose logs
```

**常见原因**:
- 配置文件未挂载
- 端口冲突
- 资源不足

#### 4. 服务无法启动

**检查状态**:
```bash
sudo systemctl status chatbot
sudo journalctl -u chatbot -n 50
```

**常见原因**:
- Python 依赖未安装
- 配置文件错误
- 权限问题

### 日志位置

| 部署方式 | 日志位置 |
|---------|---------|
| Docker | `docker-compose logs` |
| Systemd | `/opt/chatbot/logs/chatbot.log` |
| Systemd 错误 | `journalctl -u chatbot` |

### 性能监控

```bash
# 查看容器资源使用
docker stats customer-service-bot

# 查看系统资源
htop

# 查看进程
ps aux | grep python
```

---

## 🔐 安全建议

### 1. 配置文件安全

```bash
# 设置配置文件权限
chmod 600 config.yaml

# 不要将配置文件提交到 Git
echo "config.yaml" >> .gitignore
```

### 2. 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (如需)
sudo ufw allow 443/tcp  # HTTPS (如需)
sudo ufw enable
```

### 3. 定期更新

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade

# 更新应用
cd /opt/chatbot
git pull origin guidebot
sudo systemctl restart chatbot
```

---

## 📊 监控和维护

### 健康检查

```bash
# Docker 健康检查
docker inspect customer-service-bot | grep Health

# 服务状态检查
curl -f http://localhost:8000/health || echo "Service down"
```

### 日志轮转

编辑 `/etc/logrotate.d/chatbot`:

```
/opt/chatbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 备份

```bash
# 备份配置和数据
tar -czf chatbot-backup-$(date +%Y%m%d).tar.gz \
    /opt/chatbot/config.yaml \
    /opt/chatbot/data/knowledge_base.json
```

---

## 🆘 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/Allaniiibigdevil/OpenHandsCreate/issues)
- **文档**: [README.md](README.md)
- **测试报告**: [TEST_RESULTS.md](TEST_RESULTS.md)

---

## 📝 更新日志

### v1.0.0 (2025-11-09)
- ✅ 初始版本
- ✅ Docker 部署支持
- ✅ Systemd 服务支持
- ✅ GitHub Actions 自动部署
- ✅ 完整部署文档

---

**部署成功后，记得测试机器人功能！** 🎉
