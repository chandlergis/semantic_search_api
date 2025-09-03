from typing import List, Dict, Tuple
import math
import jieba
import re

class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        初始化BM25算法
        
        Args:
            k1: 调节词频饱和度的参数
            b: 调节文档长度归一化的参数
        """
        self.k1 = k1
        self.b = b
        self.documents: List[List[str]] = []
        self.avgdl = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []
        self.num_docs = 0

    def add_document(self, document: List[str]) -> None:
        """
        添加文档到索引
        
        Args:
            document: 分词后的文档词列表
        """
        self.documents.append(document)
        self.doc_len.append(len(document))
        self.num_docs += 1
        
        # 更新词频统计
        unique_words = set(document)
        for word in unique_words:
            self.doc_freqs[word] = self.doc_freqs.get(word, 0) + 1
        
        # 更新平均文档长度
        if self.num_docs > 0:
            self.avgdl = sum(self.doc_len) / self.num_docs

    def calculate_idf(self) -> None:
        """计算所有词的逆文档频率(IDF)"""
        for word, freq in self.doc_freqs.items():
            self.idf[word] = math.log((self.num_docs - freq + 0.5) / (freq + 0.5) + 1)

    def search(self, query: List[str], top_n: int = 5) -> List[Tuple[int, float]]:
        """
        搜索与查询最相似的文档
        
        Args:
            query: 分词后的查询词列表
            top_n: 返回前N个结果
            
        Returns:
            包含(文档索引, 相似度分数)的列表
        """
        if not self.documents or not query:
            return []
            
        self.calculate_idf()
        scores = []
        
        for doc_idx, document in enumerate(self.documents):
            score = 0.0
            doc_length = self.doc_len[doc_idx]
            
            for word in query:
                if word not in self.idf:
                    continue
                    
                # 计算词在文档中的频率
                tf = document.count(word)
                
                # BM25公式
                numerator = self.idf[word] * tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avgdl)
                score += numerator / denominator
            
            scores.append((doc_idx, score))
        
        # 按分数降序排序并返回前N个
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

    def similarity(self, doc1: List[str], doc2: List[str]) -> float:
        """
        计算两个文档之间的BM25相似度
        
        Args:
            doc1: 第一个文档的分词结果
            doc2: 第二个文档的分词结果
            
        Returns:
            相似度分数 (0-1范围)
        """
        # 临时添加文档到索引
        temp_bm25 = BM25(self.k1, self.b)
        temp_bm25.add_document(doc1)
        temp_bm25.add_document(doc2)
        
        # 使用doc2作为查询来搜索doc1的相似度
        results = temp_bm25.search(doc2)
        
        if results:
            # 获取doc1的分数并归一化到0-1范围
            max_score = max(score for _, score in results)
            if max_score > 0:
                for doc_idx, score in results:
                    if doc_idx == 0:  # doc1的索引
                        return min(1.0, score / max_score)
        
        return 0.0

def tokenize_chinese_text(text: str) -> List[str]:
    """
    中文文本分词
    
    Args:
        text: 中文文本
        
    Returns:
        分词后的词列表
    """
    if not text:
        return []
    
    # 使用jieba分词
    words = jieba.cut(text)
    # 过滤空字符和标点符号
    tokens = [word.strip() for word in words if word.strip() and not re.match(r'^[\W_]+$', word)]
    return tokens

def bm25_similarity(text1: str, text2: str) -> float:
    """
    计算两个中文文本的BM25相似度
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        相似度分数 (0-1范围)
    """
    # 分词
    tokens1 = tokenize_chinese_text(text1)
    tokens2 = tokenize_chinese_text(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # 使用BM25计算相似度
    bm25 = BM25()
    return bm25.similarity(tokens1, tokens2)
