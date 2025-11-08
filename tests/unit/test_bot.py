"""机器人逻辑单元测试"""
import pytest
from unittest.mock import Mock, MagicMock
from src.chatbot.bot import ChatBot
from src.chatbot.deepseek_client import DeepSeekClient
from src.knowledge_base import KnowledgeBase


class TestChatBot:
    """机器人类测试"""
    
    @pytest.fixture
    def mock_client(self):
        """创建 Mock DeepSeek 客户端"""
        client = Mock(spec=DeepSeekClient)
        client.chat.return_value = "这是机器人的回复"
        client.chat_stream.return_value = iter(["这是", "流式", "回复"])
        return client
    
    @pytest.fixture
    def mock_kb(self):
        """创建 Mock 知识库"""
        kb = Mock(spec=KnowledgeBase)
        kb.get_context.return_value = "知识库上下文信息"
        kb.search.return_value = [
            {
                "question": "测试问题",
                "answer": "测试答案",
                "similarity": 0.9
            }
        ]
        return kb
    
    @pytest.fixture
    def bot(self, mock_client, mock_kb):
        """创建机器人实例"""
        return ChatBot(
            deepseek_client=mock_client,
            knowledge_base=mock_kb,
            system_prompt="你是一个测试机器人",
            max_history=5,
            enable_knowledge_base=True
        )
    
    def test_bot_initialization(self, bot, mock_client, mock_kb):
        """测试机器人初始化"""
        assert bot.client == mock_client
        assert bot.kb == mock_kb
        assert bot.system_prompt == "你是一个测试机器人"
        assert bot.max_history == 5
        assert bot.enable_knowledge_base is True
        assert bot.conversation_history == []
    
    def test_chat_basic(self, bot, mock_client):
        """测试基本对话"""
        response = bot.chat("你好")
        
        assert response == "这是机器人的回复"
        assert len(bot.conversation_history) == 2  # 用户消息 + 助手回复
        assert bot.conversation_history[0]["role"] == "user"
        assert bot.conversation_history[0]["content"] == "你好"
        assert bot.conversation_history[1]["role"] == "assistant"
        assert bot.conversation_history[1]["content"] == "这是机器人的回复"
    
    def test_chat_with_knowledge_base(self, bot, mock_client, mock_kb):
        """测试带知识库的对话"""
        bot.chat("测试问题")
        
        # 验证知识库被查询
        mock_kb.get_context.assert_called_once_with("测试问题")
        
        # 验证 DeepSeek 客户端被调用
        mock_client.chat.assert_called_once()
        call_args = mock_client.chat.call_args
        
        # 验证系统提示词包含知识库上下文
        system_prompt = call_args.kwargs['system_prompt']
        assert "知识库上下文信息" in system_prompt
    
    def test_chat_without_knowledge_base(self, mock_client):
        """测试不使用知识库的对话"""
        bot = ChatBot(
            deepseek_client=mock_client,
            knowledge_base=None,
            system_prompt="测试",
            enable_knowledge_base=False
        )
        
        bot.chat("你好")
        
        # 验证系统提示词不包含知识库信息
        call_args = mock_client.chat.call_args
        system_prompt = call_args.kwargs['system_prompt']
        assert "知识库" not in system_prompt
    
    def test_chat_history_management(self, bot):
        """测试对话历史管理"""
        # 发送多条消息
        for i in range(3):
            bot.chat(f"消息 {i}")
        
        # 验证历史记录
        assert len(bot.conversation_history) == 6  # 3条用户消息 + 3条助手回复
    
    def test_chat_max_history_limit(self, mock_client):
        """测试对话历史长度限制"""
        bot = ChatBot(
            deepseek_client=mock_client,
            knowledge_base=None,
            max_history=2
        )
        
        # 发送多条消息
        for i in range(5):
            bot.chat(f"消息 {i}")
        
        # 验证传递给 API 的消息数量不超过限制
        call_args = mock_client.chat.call_args
        messages = call_args.kwargs.get('messages', call_args.args[0] if call_args.args else [])
        assert len(messages) <= 2
    
    def test_chat_api_error(self, bot, mock_client):
        """测试 API 调用失败"""
        mock_client.chat.side_effect = Exception("API 错误")
        
        response = bot.chat("测试")
        
        assert "出现错误" in response
        assert "API 错误" in response
    
    def test_chat_stream_basic(self, bot, mock_client):
        """测试流式对话"""
        chunks = list(bot.chat_stream("你好"))
        
        assert chunks == ["这是", "流式", "回复"]
        assert len(bot.conversation_history) == 2
        assert bot.conversation_history[1]["content"] == "这是流式回复"
    
    def test_chat_stream_with_knowledge_base(self, bot, mock_kb):
        """测试带知识库的流式对话"""
        list(bot.chat_stream("测试问题"))
        
        # 验证知识库被查询
        mock_kb.get_context.assert_called_once_with("测试问题")
    
    def test_chat_stream_api_error(self, bot, mock_client):
        """测试流式 API 调用失败"""
        mock_client.chat_stream.side_effect = Exception("流式错误")
        
        chunks = list(bot.chat_stream("测试"))
        
        assert len(chunks) == 1
        assert "出现错误" in chunks[0]
    
    def test_clear_history(self, bot):
        """测试清空对话历史"""
        bot.chat("消息1")
        bot.chat("消息2")
        
        assert len(bot.conversation_history) > 0
        
        bot.clear_history()
        
        assert len(bot.conversation_history) == 0
    
    def test_get_history(self, bot):
        """测试获取对话历史"""
        bot.chat("测试消息")
        
        history = bot.get_history()
        
        assert isinstance(history, list)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        
        # 验证返回的是副本
        history.append({"role": "test", "content": "test"})
        assert len(bot.conversation_history) == 2
    
    def test_search_knowledge_base(self, bot, mock_kb):
        """测试直接搜索知识库"""
        results = bot.search_knowledge_base("测试查询")
        
        mock_kb.search.assert_called_once_with("测试查询")
        assert len(results) == 1
        assert results[0]["question"] == "测试问题"
    
    def test_search_knowledge_base_without_kb(self, mock_client):
        """测试没有知识库时的搜索"""
        bot = ChatBot(
            deepseek_client=mock_client,
            knowledge_base=None
        )
        
        results = bot.search_knowledge_base("测试")
        
        assert results == []
    
    def test_conversation_context_preservation(self, bot, mock_client):
        """测试对话上下文保持"""
        bot.chat("我叫张三")
        bot.chat("我叫什么名字？")
        
        # 验证第二次调用包含第一次的上下文
        call_args = mock_client.chat.call_args
        messages = call_args.kwargs.get('messages', call_args.args[0] if call_args.args else [])
        
        assert len(messages) >= 2
        assert any("张三" in msg.get("content", "") for msg in messages)
