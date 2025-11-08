#!/bin/bash
# 测试运行脚本

set -e

echo "================================"
echo "客服机器人测试套件"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    echo "请先安装 Python 3: apt-get install python3 python3-pip"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo ""

# 检查依赖
echo "检查测试依赖..."
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "安装测试依赖..."
    pip3 install -r requirements.txt
fi

echo "✓ 依赖已安装"
echo ""

# 运行单元测试
echo "================================"
echo "运行单元测试"
echo "================================"
python3 -m pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "================================"
echo "运行集成测试"
echo "================================"
python3 -m pytest tests/integration -v -m integration

echo ""
echo "================================"
echo "测试完成！"
echo "================================"
echo ""
echo "覆盖率报告已生成到: htmlcov/index.html"
echo ""
