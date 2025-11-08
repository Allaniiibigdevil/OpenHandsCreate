"""完整对话流程集成测试"""
import pytest
from unittest.mock import Mock, patch
from src.chatbot import ChatBot, DeepSeekClient
from src.knowledge_base import KnowledgeBase


@pytest.mark.integration
class TestFullConversation:
    """完整对话流程测试"""
    
    @pytest.fixture
    def kb(self):
        """创建真实的知识库实例"""
        return KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            similarity_threshold=0.6,
            max_results=3
        )
    
    @pytest.fixture
    @patch('src.chatbot.deepseek_client.OpenAI')
    def bot(self, mock_openai, kb):
        """创建机器人实例（Mock API）"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "根据知识库信息，产品使用说明：步骤1、步骤2、步骤3"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 创建真实的 DeepSeek 客户端
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com",
            model="test-model"
        )
        
        # 创建机器人
        return ChatBot(
            deepseek_client=client,
            knowledge_base=kb,
            system_prompt="你是一个客服机器人",
            max_history=10,
            enable_knowledge_base=True
        )
    
    def test_conversation_with_knowledge_base(self, bot, kb):
        """测试带知识库的完整对话流程"""
        # 用户提问
        user_message = "如何使用产品？"
        response = bot.chat(user_message)
        
        # 验证响应
        assert response is not None
        assert len(response) > 0
        
        # 验证对话历史
        history = bot.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == user_message
        assert history[1]["role"] == "assistant"
    
    def test_multi_turn_conversation(self, bot):
        """测试多轮对话"""
        # 第一轮
        response1 = bot.chat("你好")
        assert response1 is not None
        
        # 第二轮
        response2 = bot.chat("如何使用产品？")
        assert response2 is not None
        
        # 第三轮
        response3 = bot.chat("退款政策是什么？")
        assert response3 is not None
        
        # 验证历史记录
        history = bot.get_history()
        assert len(history) == 6  # 3轮对话，每轮2条消息
    
    def test_knowledge_base_search_integration(self, bot):
        """测试知识库搜索集成"""
        # 直接搜索知识库
        results = bot.search_knowledge_base("产品使用")
        
        assert len(results) > 0
        assert any("产品" in r["question"] for r in results)
        assert all("similarity" in r for r in results)
    
    def test_conversation_context_with_kb(self, bot):
        """测试对话上下文与知识库结合"""
        # 第一轮：询问产品使用
        bot.chat("如何使用产品？")
        
        # 第二轮：追问（依赖上下文）
        response = bot.chat("还有其他注意事项吗？")
        
        # 验证历史包含上下文
        history = bot.get_history()
        assert len(history) == 4
        assert "产品" in history[0]["content"]
    
    def test_clear_and_restart_conversation(self, bot):
        """测试清空历史并重新开始对话"""
        # 进行一些对话
        bot.chat("第一条消息")
        bot.chat("第二条消息")
        
        assert len(bot.get_history()) == 4
        
        # 清空历史
        bot.clear_history()
        assert len(bot.get_history()) == 0
        
        # 重新开始对话
        bot.chat("新的对话")
        assert len(bot.get_history()) == 2


@pytest.mark.integration
class TestKnowledgeBaseIntegration:
    """知识库集成测试"""
    
    @pytest.fixture
    def kb(self):
        """创建知识库实例"""
        return KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            similarity_threshold=0.6,
            max_results=3
        )
    
    def test_search_and_context_generation(self, kb):
        """测试搜索和上下文生成"""
        # 搜索
        results = kb.search("产品使用")
        assert len(results) > 0
        
        # 生成上下文
        context = kb.get_context("产品使用")
        assert context is not None
        assert "以下是相关的知识库信息" in context
        
        # 验证上下文包含搜索结果
        for result in results:
            assert result["question"] in context
            assert result["answer"] in context
    
    def test_multiple_queries(self, kb):
        """测试多次查询"""
        queries = ["产品使用", "退款政策", "测试问题"]
        
        for query in queries:
            results = kb.search(query)
            # 每个查询都应该有结果或返回空列表
            assert isinstance(results, list)
    
    def test_similarity_ranking(self, kb):
        """测试相似度排序"""
        results = kb.search("产品")
        
        if len(results) > 1:
            # 验证结果按相似度降序排列
            similarities = [r["similarity"] for r in results]
            assert similarities == sorted(similarities, reverse=True)


@pytest.mark.integration
class TestEndToEndFlow:
    """端到端流程测试"""
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_complete_customer_service_flow(self, mock_openai):
        """测试完整的客服流程"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "我可以帮您解答问题"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 创建完整系统
        kb = KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            similarity_threshold=0.6,
            max_results=3
        )
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        bot = ChatBot(
            deepseek_client=client,
            knowledge_base=kb,
            system_prompt="你是一个专业的客服机器人",
            max_history=10,
            enable_knowledge_base=True
        )
        
        # 模拟客服对话流程
        # 1. 用户打招呼
        response1 = bot.chat("你好")
        assert response1 is not None
        
        # 2. 用户询问产品
        response2 = bot.chat("如何使用产品？")
        assert response2 is not None
        
        # 3. 用户询问售后
        response3 = bot.chat("退款政策是什么？")
        assert response3 is not None
        
        # 4. 验证整个流程
        history = bot.get_history()
        assert len(history) == 6
        
        # 验证知识库被正确使用
        kb_results = bot.search_knowledge_base("退款")
        assert len(kb_results) > 0
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_stream_conversation_flow(self, mock_openai):
        """测试流式对话流程"""
        # Mock 流式响应
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="这"))]),
            Mock(choices=[Mock(delta=Mock(content="是"))]),
            Mock(choices=[Mock(delta=Mock(content="回复"))]),
        ]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai.return_value = mock_client
        
        # 创建系统
        kb = KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json"
        )
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        bot = ChatBot(
            deepseek_client=client,
            knowledge_base=kb,
            enable_knowledge_base=True
        )
        
        # 测试流式对话
        chunks = list(bot.chat_stream("测试问题"))
        
        assert len(chunks) == 3
        assert "".join(chunks) == "这是回复"
        
        # 验证历史记录
        history = bot.get_history()
        assert len(history) == 2
        assert history[1]["content"] == "这是回复"
