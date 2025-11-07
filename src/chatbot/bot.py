"""客服机器人主逻辑"""
from typing import List, Dict, Optional
from .deepseek_client import DeepSeekClient
from ..knowledge_base.kb_manager import KnowledgeBase


class ChatBot:
    """客服机器人类"""
    
    def __init__(self, deepseek_client: DeepSeekClient,
                 knowledge_base: Optional[KnowledgeBase] = None,
                 system_prompt: str = "",
                 max_history: int = 10,
                 enable_knowledge_base: bool = True):
        """
        初始化客服机器人
        
        Args:
            deepseek_client: DeepSeek API 客户端
            knowledge_base: 知识库管理器
            system_prompt: 系统提示词
            max_history: 对话历史保留条数
            enable_knowledge_base: 是否启用知识库增强
        """
        self.client = deepseek_client
        self.kb = knowledge_base
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.enable_knowledge_base = enable_knowledge_base
        self.conversation_history: List[Dict[str, str]] = []
    
    def chat(self, user_message: str) -> str:
        """
        处理用户消息并返回回复
        
        Args:
            user_message: 用户消息
            
        Returns:
            机器人回复
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 构建完整的提示词
        full_prompt = self.system_prompt
        
        # 如果启用知识库，尝试获取相关上下文
        if self.enable_knowledge_base and self.kb:
            kb_context = self.kb.get_context(user_message)
            if kb_context:
                full_prompt += f"\n\n{kb_context}\n\n请基于以上知识库信息回答用户问题。"
        
        # 保持对话历史在限制范围内
        messages = self.conversation_history[-self.max_history:]
        
        # 调用 DeepSeek API
        try:
            response = self.client.chat(
                messages=messages,
                system_prompt=full_prompt
            )
            
            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            return response
        
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            return error_msg
    
    def chat_stream(self, user_message: str):
        """
        流式处理用户消息
        
        Args:
            user_message: 用户消息
            
        Yields:
            机器人回复的文本片段
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 构建完整的提示词
        full_prompt = self.system_prompt
        
        # 如果启用知识库，尝试获取相关上下文
        if self.enable_knowledge_base and self.kb:
            kb_context = self.kb.get_context(user_message)
            if kb_context:
                full_prompt += f"\n\n{kb_context}\n\n请基于以上知识库信息回答用户问题。"
        
        # 保持对话历史在限制范围内
        messages = self.conversation_history[-self.max_history:]
        
        # 调用 DeepSeek API 流式接口
        try:
            full_response = ""
            for chunk in self.client.chat_stream(
                messages=messages,
                system_prompt=full_prompt
            ):
                full_response += chunk
                yield chunk
            
            # 添加完整回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
        
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            yield error_msg
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """
        直接搜索知识库
        
        Args:
            query: 查询文本
            
        Returns:
            匹配的知识库条目列表
        """
        if not self.kb:
            return []
        
        return self.kb.search(query)
