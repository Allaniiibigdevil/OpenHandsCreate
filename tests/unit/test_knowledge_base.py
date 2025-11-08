"""知识库模块单元测试"""
import pytest
import os
import json
import tempfile
from src.knowledge_base import KnowledgeBase


class TestKnowledgeBase:
    """知识库类测试"""
    
    @pytest.fixture
    def kb(self):
        """创建知识库实例"""
        return KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            similarity_threshold=0.6,
            max_results=3
        )
    
    def test_load_knowledge_base_success(self, kb):
        """测试成功加载知识库"""
        assert kb.knowledge_data is not None
        assert len(kb.knowledge_data) == 3
    
    def test_load_knowledge_base_file_not_found(self):
        """测试知识库文件不存在时返回空列表"""
        kb = KnowledgeBase(data_path="non_existent.json")
        assert kb.knowledge_data == []
    
    def test_calculate_similarity(self, kb):
        """测试相似度计算"""
        similarity = kb._calculate_similarity("测试问题", "测试问题")
        assert similarity == 1.0
        
        similarity = kb._calculate_similarity("测试", "问题")
        assert 0 <= similarity <= 1
    
    def test_search_exact_match(self, kb):
        """测试精确匹配搜索"""
        results = kb.search("测试问题1")
        assert len(results) > 0
        assert results[0]["question"] == "测试问题1"
        assert results[0]["answer"] == "测试答案1"
    
    def test_search_partial_match(self, kb):
        """测试部分匹配搜索"""
        results = kb.search("产品使用")
        assert len(results) > 0
        assert any("产品" in r["question"] for r in results)
    
    def test_search_keyword_match(self, kb):
        """测试关键词匹配"""
        results = kb.search("退款")
        assert len(results) > 0
        assert any("退款" in r["keywords"] for r in results)
    
    def test_search_no_match(self, kb):
        """测试无匹配结果"""
        results = kb.search("完全不相关的内容xyz123")
        assert len(results) == 0
    
    def test_search_max_results(self):
        """测试最大结果数限制"""
        kb = KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            max_results=1
        )
        results = kb.search("测试")
        assert len(results) <= 1
    
    def test_search_similarity_threshold(self):
        """测试相似度阈值过滤"""
        kb = KnowledgeBase(
            data_path="tests/fixtures/test_knowledge_base.json",
            similarity_threshold=0.9
        )
        results = kb.search("完全不同的内容")
        assert len(results) == 0
    
    def test_get_context_with_results(self, kb):
        """测试获取上下文信息"""
        context = kb.get_context("测试问题")
        assert context is not None
        assert "以下是相关的知识库信息" in context
        assert "测试问题1" in context
    
    def test_get_context_no_results(self, kb):
        """测试无匹配时返回 None"""
        context = kb.get_context("完全不相关的内容xyz123")
        assert context is None
    
    def test_add_entry(self):
        """测试添加知识库条目"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_file = f.name
        
        try:
            kb = KnowledgeBase(data_path=temp_file)
            kb.add_entry(
                question="新问题",
                answer="新答案",
                category="新分类",
                keywords=["新", "关键词"]
            )
            
            assert len(kb.knowledge_data) == 1
            assert kb.knowledge_data[0]["question"] == "新问题"
            assert kb.knowledge_data[0]["answer"] == "新答案"
            
            # 验证文件已保存
            with open(temp_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert len(saved_data) == 1
        
        finally:
            os.unlink(temp_file)
    
    def test_search_results_sorted_by_similarity(self, kb):
        """测试搜索结果按相似度排序"""
        results = kb.search("测试")
        
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["similarity"] >= results[i + 1]["similarity"]
