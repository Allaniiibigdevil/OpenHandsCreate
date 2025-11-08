"""Pytest 配置和共享 fixtures"""
import pytest
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def test_config_path():
    """测试配置文件路径"""
    return "tests/fixtures/test_config.yaml"


@pytest.fixture
def test_kb_path():
    """测试知识库文件路径"""
    return "tests/fixtures/test_knowledge_base.json"


@pytest.fixture
def sample_messages():
    """示例消息列表"""
    return [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
        {"role": "user", "content": "我想了解产品信息"}
    ]


@pytest.fixture
def sample_kb_entries():
    """示例知识库条目"""
    return [
        {
            "question": "产品价格是多少？",
            "answer": "产品价格为 999 元",
            "category": "价格",
            "keywords": ["价格", "多少钱", "费用"]
        },
        {
            "question": "如何联系客服？",
            "answer": "客服电话：400-123-4567",
            "category": "联系方式",
            "keywords": ["客服", "联系", "电话"]
        }
    ]


@pytest.fixture
def mock_api_response():
    """Mock API 响应数据"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "这是测试响应"
                },
                "finish_reason": "stop"
            }
        ]
    }
