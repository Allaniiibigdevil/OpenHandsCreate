"""配置模块单元测试"""
import pytest
import os
from src.config import Config


class TestConfig:
    """配置类测试"""
    
    def test_load_config_success(self):
        """测试成功加载配置文件"""
        config = Config("tests/fixtures/test_config.yaml")
        assert config.config is not None
        assert isinstance(config.config, dict)
    
    def test_load_config_file_not_found(self):
        """测试配置文件不存在时抛出异常"""
        with pytest.raises(FileNotFoundError):
            Config("non_existent_config.yaml")
    
    def test_get_simple_key(self):
        """测试获取简单配置项"""
        config = Config("tests/fixtures/test_config.yaml")
        assert config.get("deepseek") is not None
    
    def test_get_nested_key(self):
        """测试获取嵌套配置项"""
        config = Config("tests/fixtures/test_config.yaml")
        api_key = config.get("deepseek.api_key")
        assert api_key == "test-api-key"
    
    def test_get_with_default(self):
        """测试获取不存在的配置项返回默认值"""
        config = Config("tests/fixtures/test_config.yaml")
        value = config.get("non.existent.key", "default_value")
        assert value == "default_value"
    
    def test_get_deepseek_config(self):
        """测试获取 DeepSeek 配置"""
        config = Config("tests/fixtures/test_config.yaml")
        deepseek_config = config.get_deepseek_config()
        
        assert deepseek_config["api_key"] == "test-api-key"
        assert deepseek_config["api_base"] == "https://api.test.com/v1"
        assert deepseek_config["model"] == "test-model"
        assert deepseek_config["max_tokens"] == 1000
        assert deepseek_config["temperature"] == 0.5
    
    def test_get_knowledge_base_config(self):
        """测试获取知识库配置"""
        config = Config("tests/fixtures/test_config.yaml")
        kb_config = config.get_knowledge_base_config()
        
        assert kb_config["data_path"] == "tests/fixtures/test_knowledge_base.json"
        assert kb_config["similarity_threshold"] == 0.7
        assert kb_config["max_results"] == 2
    
    def test_get_conversation_config(self):
        """测试获取对话配置"""
        config = Config("tests/fixtures/test_config.yaml")
        conv_config = config.get_conversation_config()
        
        assert conv_config["system_prompt"] == "Test system prompt"
        assert conv_config["max_history"] == 5
        assert conv_config["enable_knowledge_base"] is True
    
    def test_get_logging_config(self):
        """测试获取日志配置"""
        config = Config("tests/fixtures/test_config.yaml")
        log_config = config.get_logging_config()
        
        assert log_config["level"] == "DEBUG"
        assert log_config["file"] == "tests/logs/test.log"
