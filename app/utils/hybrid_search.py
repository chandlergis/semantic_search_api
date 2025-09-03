import re
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class TextProcessor:
    """文本预处理器"""
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符，保留中英文、数字、基本标点
        text = re.sub(r'[^\w\u4e00-\u9fff\s.,!?;:()]', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """简化分词处理 - 平衡词组和单字"""
        if not text:
            return []
        
        # 清理文本
        clean_text = self.clean_text(text)
        
        tokens = []
        words = clean_text.split()
        
        for word in words:
            # 如果包含中文字符
            if any('\u4e00' <= c <= '\u9fff' for c in word):
                # 分离中英文
                current_token = ""
                chinese_chars = []
                
                for char in word:
                    if '\u4e00' <= char <= '\u9fff':  # 中文字符
                        if current_token:
                            tokens.append(current_token.lower())
                            current_token = ""
                        chinese_chars.append(char)
                    elif char.isalnum():  # 英文数字
                        if chinese_chars:
                            # 处理中文字符 - 只保留完整词组，不重复添加单字符
                            chinese_text = ''.join(chinese_chars)
                            if len(chinese_text) >= 2:
                                tokens.append(chinese_text)  # 只添加词组
                            else:
                                tokens.extend(chinese_chars)  # 单字符直接添加
                            chinese_chars = []
                        current_token += char
                    else:  # 标点等
                        if current_token:
                            tokens.append(current_token.lower())
                            current_token = ""
                        if chinese_chars:
                            chinese_text = ''.join(chinese_chars)
                            if len(chinese_text) >= 2:
                                tokens.append(chinese_text)
                            else:
                                tokens.extend(chinese_chars)
                            chinese_chars = []
                
                # 处理末尾的token
                if current_token:
                    tokens.append(current_token.lower())
                if chinese_chars:
                    chinese_text = ''.join(chinese_chars)
                    if len(chinese_text) >= 2:
                        tokens.append(chinese_text)
                    else:
                        tokens.extend(chinese_chars)
            else:
                # 纯英文单词
                tokens.append(word.lower())
        
        # 过滤空值和去重
        unique_tokens = []
        seen = set()
        for token in tokens:
            if token and len(token.strip()) > 0 and token not in seen:
                unique_tokens.append(token)
                seen.add(token)
        
        return unique_tokens

class ChunkProcessor:
    """文档分块处理器"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.text_processor = TextProcessor()
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """将文本分割成重叠的块"""
        if not text or len(text) < self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 如果不是最后一块，尝试在句号处断开
            if end < len(text):
                # 寻找最近的句号
                last_period = text.rfind('。', start, end)
                if last_period > start + self.chunk_size // 2:
                    end = last_period + 1
                else:
                    # 寻找最近的空格
                    last_space = text.rfind(' ', start, end)
                    if last_space > start + self.chunk_size // 2:
                        end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 计算下一个块的起始位置（带重叠）
            start = max(start + 1, end - self.overlap)
            
            # 避免无限循环
            if start >= len(text):
                break
        
        return chunks

class HybridSearchEngine:
    """混合搜索引擎（BM25 + TF-IDF）"""
    
    def __init__(self, bm25_weight: float = 0.6, tfidf_weight: float = 0.4):
        self.bm25_weight = bm25_weight
        self.tfidf_weight = tfidf_weight
        self.text_processor = TextProcessor()
        self.chunk_processor = ChunkProcessor()
        
        # 搜索索引
        self.bm25_index: Optional[BM25Okapi] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        
        # 文档数据
        self.chunks_data: List[Dict] = []  # 存储chunk信息
        self.tokenized_chunks: List[List[str]] = []  # 存储分词后的chunks
    
    def build_index(self, chunks_data: List[Dict]):
        """构建搜索索引
        
        Args:
            chunks_data: 包含chunk信息的列表，每个元素应包含：
                - id: chunk ID
                - content: chunk内容
                - document_id: 所属文档ID
                - document_title: 所属文档标题
        """
        logger.info(f"构建搜索索引，共 {len(chunks_data)} 个chunks")
        
        self.chunks_data = chunks_data
        
        if not chunks_data:
            logger.warning("没有chunks数据，无法构建索引")
            return
        
        # 提取并预处理文本
        chunk_texts = [chunk['content'] for chunk in chunks_data]
        self.tokenized_chunks = [
            self.text_processor.tokenize(text) 
            for text in chunk_texts
        ]
        
        # 调试日志
        for i, tokens in enumerate(self.tokenized_chunks[:3]):  # 只显示前3个
            logger.info(f"文档{i}分词结果: {tokens[:20]}...")  # 只显示前20个token
        
        # 构建BM25索引
        try:
            self.bm25_index = BM25Okapi(self.tokenized_chunks)
            logger.info("BM25索引构建完成")
        except Exception as e:
            logger.error(f"BM25索引构建失败: {e}")
            self.bm25_index = None
        
        # 构建TF-IDF索引
        try:
            # 重新组合tokens为文本
            processed_texts = [' '.join(tokens) for tokens in self.tokenized_chunks]
            
            # 根据文档数量动态调整参数
            doc_count = len(processed_texts)
            if doc_count <= 2:
                # 文档数量很少时，使用更宽松的参数
                max_df = 1.0
                min_df = 1
            elif doc_count <= 10:
                # 文档数量较少时，适度调整
                max_df = 0.9
                min_df = 1
            else:
                # 文档数量充足时，使用原始参数
                max_df = 0.95
                min_df = 1
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                min_df=min_df,
                max_df=max_df,
                ngram_range=(1, 2)  # 包含1-gram和2-gram
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            logger.info("TF-IDF索引构建完成")
        except Exception as e:
            logger.error(f"TF-IDF索引构建失败: {e}")
            self.tfidf_vectorizer = None
            self.tfidf_matrix = None
    
    def search(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """执行混合搜索
        
        Args:
            query_text: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，每个结果包含：
            - chunk_id: chunk ID
            - content: chunk内容
            - document_id: 所属文档ID
            - document_title: 所属文档标题
            - bm25_score: BM25分数
            - tfidf_score: TF-IDF分数
            - final_score: 最终混合分数
        """
        if not self.chunks_data:
            logger.warning("索引未构建，无法执行搜索")
            return []
        
        logger.info(f"执行混合搜索，查询: {query_text[:100]}...")
        
        # 预处理查询文本
        query_tokens = self.text_processor.tokenize(query_text)
        print(f"DEBUG: 查询分词结果: {query_tokens}")
        logger.info(f"查询分词结果: {query_tokens}")
        if not query_tokens:
            logger.warning("查询文本预处理后为空")
            return []
        
        # 计算BM25分数
        bm25_scores = self._calculate_bm25_scores(query_tokens)
        
        # 计算TF-IDF分数
        tfidf_scores = self._calculate_tfidf_scores(query_text)
        
        # 计算混合分数
        results = self._calculate_hybrid_scores(bm25_scores, tfidf_scores)
        
        # 排序并返回Top-K结果
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"搜索完成，返回 {min(top_k, len(results))} 个结果")
        return results[:top_k]
    
    def _calculate_bm25_scores(self, query_tokens: List[str]) -> np.ndarray:
        """计算BM25分数"""
        if not self.bm25_index:
            logger.warning("BM25索引未构建")
            return np.zeros(len(self.chunks_data))
        
        try:
            scores = self.bm25_index.get_scores(query_tokens)
            logger.info(f"原始BM25分数: {scores}")
            
            # 只有一个文档时直接使用原始分数的归一化版本
            if len(scores) == 1:
                # 单文档情况：使用sigmoid函数将分数映射到(0,1)
                scores = 1 / (1 + np.exp(-scores))
            else:
                # 多文档情况：使用min-max归一化
                min_score = scores.min()
                max_score = scores.max()
                
                if max_score > min_score:
                    scores = (scores - min_score) / (max_score - min_score)
                else:
                    # 所有分数相同的情况
                    scores = np.ones_like(scores) * 0.5
                
            logger.info(f"归一化后BM25分数: {scores}")
            return scores
        except Exception as e:
            logger.error(f"BM25分数计算失败: {e}")
            return np.zeros(len(self.chunks_data))
    
    def _calculate_tfidf_scores(self, query_text: str) -> np.ndarray:
        """计算TF-IDF余弦相似度分数"""
        if not self.tfidf_vectorizer or self.tfidf_matrix is None:
            return np.zeros(len(self.chunks_data))
        
        try:
            # 处理查询文本
            query_tokens = self.text_processor.tokenize(query_text)
            query_processed = ' '.join(query_tokens)
            
            # 向量化查询
            query_vector = self.tfidf_vectorizer.transform([query_processed])
            
            # 计算余弦相似度
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            return similarities
        except Exception as e:
            logger.error(f"TF-IDF分数计算失败: {e}")
            return np.zeros(len(self.chunks_data))
    
    def _calculate_hybrid_scores(self, bm25_scores: np.ndarray, tfidf_scores: np.ndarray) -> List[Dict]:
        """计算混合分数"""
        results = []
        
        for i, chunk_data in enumerate(self.chunks_data):
            # 确保分数非负
            bm25_score = max(0.0, float(bm25_scores[i]) if i < len(bm25_scores) else 0.0)
            tfidf_score = max(0.0, float(tfidf_scores[i]) if i < len(tfidf_scores) else 0.0)
            
            # 混合分数
            final_score = (
                self.bm25_weight * bm25_score + 
                self.tfidf_weight * tfidf_score
            )
            
            result = {
                'chunk_id': chunk_data['id'],
                'document_id': chunk_data['document_id'],
                'document_title': chunk_data.get('document_title', ''),
                'content': chunk_data['content'],
                'chunk_index': i,
                'bm25_score': bm25_score,
                'tfidf_score': tfidf_score,
                'final_score': final_score
            }
            
            results.append(result)
        
        return results

# 全局搜索引擎实例
search_engine = HybridSearchEngine()