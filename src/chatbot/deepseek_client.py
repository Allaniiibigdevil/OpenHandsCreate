"""DeepSeek API 客户端"""
from openai import OpenAI
from typing import List, Dict, Optional


class DeepSeekClient:
    """DeepSeek API 客户端类"""
    
    def __init__(self, api_key: str, api_base: str, model: str = "deepseek-chat",
                 max_tokens: int = 2000, temperature: float = 0.7):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: API 密钥
            api_base: API 基础URL
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def chat(self, messages: List[Dict[str, str]], 
             system_prompt: Optional[str] = None) -> str:
        """
        发送对话请求
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            
        Returns:
            AI 回复内容
        """
        # 构建完整的消息列表
        full_messages = []
        
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        full_messages.extend(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"DeepSeek API 调用失败: {str(e)}")
    
    def chat_stream(self, messages: List[Dict[str, str]], 
                    system_prompt: Optional[str] = None):
        """
        流式对话请求
        
        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词
            
        Yields:
            AI 回复的文本片段
        """
        full_messages = []
        
        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        full_messages.extend(messages)
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise Exception(f"DeepSeek API 流式调用失败: {str(e)}")
