"""配置管理模块"""
import yaml
import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请复制 config.example.yaml 为 config.yaml 并填入配置"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'deepseek.api_key'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_deepseek_config(self) -> Dict[str, Any]:
        """获取 DeepSeek 配置"""
        return self.config.get('deepseek', {})
    
    def get_knowledge_base_config(self) -> Dict[str, Any]:
        """获取知识库配置"""
        return self.config.get('knowledge_base', {})
    
    def get_conversation_config(self) -> Dict[str, Any]:
        """获取对话配置"""
        return self.config.get('conversation', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})
