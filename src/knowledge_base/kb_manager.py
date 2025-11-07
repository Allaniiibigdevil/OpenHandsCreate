"""企业知识库管理模块"""
import json
import os
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self, data_path: str, similarity_threshold: float = 0.6,
                 max_results: int = 3):
        """
        初始化知识库
        
        Args:
            data_path: 知识库数据文件路径
            similarity_threshold: 相似度匹配阈值
            max_results: 最大返回结果数
        """
        self.data_path = data_path
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        self.knowledge_data = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> List[Dict[str, str]]:
        """加载知识库数据"""
        if not os.path.exists(self.data_path):
            print(f"警告: 知识库文件不存在: {self.data_path}")
            return []
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"加载知识库失败: {str(e)}")
            return []
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def search(self, query: str) -> List[Dict[str, any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            
        Returns:
            匹配的知识库条目列表，按相似度排序
        """
        if not self.knowledge_data:
            return []
        
        results = []
        
        for item in self.knowledge_data:
            question = item.get('question', '')
            keywords = item.get('keywords', [])
            
            # 计算与问题的相似度
            question_similarity = self._calculate_similarity(query, question)
            
            # 计算与关键词的相似度
            keyword_similarity = 0
            if keywords:
                keyword_similarities = [
                    self._calculate_similarity(query, kw) for kw in keywords
                ]
                keyword_similarity = max(keyword_similarities) if keyword_similarities else 0
            
            # 取最高相似度
            max_similarity = max(question_similarity, keyword_similarity)
            
            if max_similarity >= self.similarity_threshold:
                results.append({
                    'question': question,
                    'answer': item.get('answer', ''),
                    'category': item.get('category', ''),
                    'similarity': max_similarity
                })
        
        # 按相似度排序并返回前N个结果
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:self.max_results]
    
    def get_context(self, query: str) -> Optional[str]:
        """
        获取查询的上下文信息
        
        Args:
            query: 查询文本
            
        Returns:
            格式化的知识库上下文，如果没有匹配则返回 None
        """
        results = self.search(query)
        
        if not results:
            return None
        
        context_parts = ["以下是相关的知识库信息：\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"{i}. 问题: {result['question']}")
            context_parts.append(f"   答案: {result['answer']}")
            if result.get('category'):
                context_parts.append(f"   分类: {result['category']}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def add_entry(self, question: str, answer: str, 
                  category: str = "", keywords: List[str] = None):
        """
        添加知识库条目
        
        Args:
            question: 问题
            answer: 答案
            category: 分类
            keywords: 关键词列表
        """
        entry = {
            'question': question,
            'answer': answer,
            'category': category,
            'keywords': keywords or []
        }
        
        self.knowledge_data.append(entry)
        self._save_knowledge_base()
    
    def _save_knowledge_base(self):
        """保存知识库到文件"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
