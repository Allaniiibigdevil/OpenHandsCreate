"""DeepSeek 客户端单元测试"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.chatbot.deepseek_client import DeepSeekClient


class TestDeepSeekClient:
    """DeepSeek 客户端测试"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        return DeepSeekClient(
            api_key="test-api-key",
            api_base="https://api.test.com/v1",
            model="test-model",
            max_tokens=1000,
            temperature=0.7
        )
    
    def test_client_initialization(self, client):
        """测试客户端初始化"""
        assert client.model == "test-model"
        assert client.max_tokens == 1000
        assert client.temperature == 0.7
        assert client.client is not None
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_success(self, mock_openai):
        """测试成功的对话请求"""
        # Mock OpenAI 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是测试回复"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # 创建客户端并测试
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com",
            model="test-model"
        )
        
        messages = [{"role": "user", "content": "你好"}]
        response = client.chat(messages)
        
        assert response == "这是测试回复"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_with_system_prompt(self, mock_openai):
        """测试带系统提示词的对话"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "回复内容"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        messages = [{"role": "user", "content": "问题"}]
        system_prompt = "你是一个助手"
        
        client.chat(messages, system_prompt=system_prompt)
        
        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        called_messages = call_args.kwargs['messages']
        
        assert called_messages[0]['role'] == 'system'
        assert called_messages[0]['content'] == system_prompt
        assert called_messages[1]['role'] == 'user'
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_api_error(self, mock_openai):
        """测试 API 调用失败"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        messages = [{"role": "user", "content": "测试"}]
        
        with pytest.raises(Exception) as exc_info:
            client.chat(messages)
        
        assert "DeepSeek API 调用失败" in str(exc_info.value)
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_stream_success(self, mock_openai):
        """测试流式对话成功"""
        # Mock 流式响应
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta.content = "这是"
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta.content = "流式"
        
        mock_chunk3 = Mock()
        mock_chunk3.choices = [Mock()]
        mock_chunk3.choices[0].delta.content = "回复"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = [
            mock_chunk1, mock_chunk2, mock_chunk3
        ]
        mock_openai.return_value = mock_client
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        messages = [{"role": "user", "content": "测试"}]
        chunks = list(client.chat_stream(messages))
        
        assert chunks == ["这是", "流式", "回复"]
        
        # 验证调用参数包含 stream=True
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['stream'] is True
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_stream_with_system_prompt(self, mock_openai):
        """测试带系统提示词的流式对话"""
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta.content = "回复"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = [mock_chunk]
        mock_openai.return_value = mock_client
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        messages = [{"role": "user", "content": "问题"}]
        system_prompt = "系统提示"
        
        list(client.chat_stream(messages, system_prompt=system_prompt))
        
        # 验证系统消息被添加
        call_args = mock_client.chat.completions.create.call_args
        called_messages = call_args.kwargs['messages']
        
        assert called_messages[0]['role'] == 'system'
        assert called_messages[0]['content'] == system_prompt
    
    @patch('src.chatbot.deepseek_client.OpenAI')
    def test_chat_stream_api_error(self, mock_openai):
        """测试流式 API 调用失败"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Stream Error")
        mock_openai.return_value = mock_client
        
        client = DeepSeekClient(
            api_key="test-key",
            api_base="https://test.com"
        )
        
        messages = [{"role": "user", "content": "测试"}]
        
        with pytest.raises(Exception) as exc_info:
            list(client.chat_stream(messages))
        
        assert "DeepSeek API 流式调用失败" in str(exc_info.value)
