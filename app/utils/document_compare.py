import hashlib
import re
import logging
import difflib
from typing import List, Dict, Tuple, Optional, Any
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class DocumentComparator:
    """文档比对器 - 实现双文件相似度检测和差异高亮"""
    
    def __init__(self, 
                 similarity_threshold_high: float = 0.9,
                 similarity_threshold_medium: float = 0.7,
                 chunk_size: int = 300):
        """
        初始化文档比对器
        
        Args:
            similarity_threshold_high: 高相似度阈值 (红色高亮)
            similarity_threshold_medium: 中等相似度阈值 (黄色高亮) 
            chunk_size: 文本分块大小
        """
        self.similarity_threshold_high = similarity_threshold_high
        self.similarity_threshold_medium = similarity_threshold_medium
        self.chunk_size = chunk_size
        
    def split_into_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        将文本分割成语义块
        
        Args:
            text: 输入文本
            
        Returns:
            包含块信息的列表，每个块包含: {id, content, start_pos, end_pos}
        """
        if not text:
            return []
        
        chunks = []
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        chunk_id = 0
        current_pos = 0
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # 如果段落太长，按句子分割
            if len(paragraph) > self.chunk_size:
                sentences = re.split(r'[。！？.!?]', paragraph)
                current_chunk = ""
                chunk_start = current_pos
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    # 如果添加这个句子会超过chunk_size，先保存当前chunk
                    if current_chunk and len(current_chunk + sentence) > self.chunk_size:
                        chunks.append({
                            'id': f'chunk_{chunk_id}',
                            'content': current_chunk.strip(),
                            'start_pos': chunk_start,
                            'end_pos': chunk_start + len(current_chunk)
                        })
                        chunk_id += 1
                        current_chunk = sentence
                        chunk_start = current_pos + len(current_chunk) - len(sentence)
                    else:
                        current_chunk += sentence + "。" if sentence else ""
                
                # 保存最后的chunk
                if current_chunk.strip():
                    chunks.append({
                        'id': f'chunk_{chunk_id}',
                        'content': current_chunk.strip(),
                        'start_pos': chunk_start,
                        'end_pos': chunk_start + len(current_chunk)
                    })
                    chunk_id += 1
            else:
                # 段落不长，直接作为一个chunk
                chunks.append({
                    'id': f'chunk_{chunk_id}',
                    'content': paragraph.strip(),
                    'start_pos': current_pos,
                    'end_pos': current_pos + len(paragraph)
                })
                chunk_id += 1
            
            current_pos += len(paragraph) + 2  # +2 for \n\n
        
        return chunks
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用SequenceMatcher计算字符级相似度
        char_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # 使用TF-IDF计算语义相似度
        try:
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            semantic_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            semantic_similarity = 0.0
        
        # 综合相似度 (字符相似度权重0.4，语义相似度权重0.6)
        final_similarity = 0.4 * char_similarity + 0.6 * semantic_similarity
        
        # 确保相似度不超过1.0 (处理浮点精度问题)
        final_similarity = min(1.0, max(0.0, final_similarity))
        
        return float(final_similarity)
    
    def find_best_matches(self, chunks_a: List[Dict], chunks_b: List[Dict]) -> List[Dict]:
        """
        找到两个文档之间的最佳匹配块
        
        Args:
            chunks_a: 文档A的块列表
            chunks_b: 文档B的块列表
            
        Returns:
            匹配结果列表，每个结果包含: {chunk_a_id, chunk_b_id, similarity, match_type}
        """
        matches = []
        used_b_chunks = set()
        
        for chunk_a in chunks_a:
            best_match = None
            best_similarity = 0.0
            
            for chunk_b in chunks_b:
                if chunk_b['id'] in used_b_chunks:
                    continue
                    
                similarity = self.calculate_similarity(
                    chunk_a['content'], 
                    chunk_b['content']
                )
                
                if similarity > best_similarity and similarity >= self.similarity_threshold_medium:
                    best_similarity = similarity
                    best_match = chunk_b
            
            if best_match:
                used_b_chunks.add(best_match['id'])
                
                # 确定匹配类型
                if best_similarity >= self.similarity_threshold_high:
                    match_type = 'high'  # 红色高亮
                elif best_similarity >= self.similarity_threshold_medium:
                    match_type = 'medium'  # 黄色高亮
                else:
                    match_type = 'low'
                
                matches.append({
                    'chunk_a_id': chunk_a['id'],
                    'chunk_b_id': best_match['id'],
                    'similarity': best_similarity,
                    'match_type': match_type
                })
        
        return matches
    
    def convert_to_html_with_highlights(self, text: str, chunks: List[Dict], matches: List[Dict], is_doc_a: bool = True) -> str:
        """
        将文档转换为带高亮的HTML
        
        Args:
            text: 原始文本
            chunks: 文档块列表
            matches: 匹配结果列表
            is_doc_a: 是否为文档A
            
        Returns:
            带高亮标记的HTML字符串
        """
        # 创建chunk_id到匹配信息的映射
        chunk_matches = {}
        for match in matches:
            if is_doc_a:
                chunk_matches[match['chunk_a_id']] = match
            else:
                chunk_matches[match['chunk_b_id']] = match
        
        # 构建HTML
        html_parts = []
        last_pos = 0
        
        for chunk in chunks:
            # 添加chunk之前的文本
            if chunk['start_pos'] > last_pos:
                between_text = text[last_pos:chunk['start_pos']]
                html_parts.append(self._escape_html(between_text))
            
            # 检查是否有匹配
            match_info = chunk_matches.get(chunk['id'])
            if match_info:
                css_class = f"highlight-{match_info['match_type']}"
                link_id = f"link_{match_info['chunk_a_id']}_{match_info['chunk_b_id']}"
                html_parts.append(
                    f'<span class="{css_class}" id="{link_id}" data-match-type="{match_info["match_type"]}" '
                    f'data-similarity="{match_info["similarity"]:.3f}">{self._escape_html(chunk["content"])}</span>'
                )
            else:
                html_parts.append(self._escape_html(chunk['content']))
            
            last_pos = chunk['end_pos']
        
        # 添加剩余文本
        if last_pos < len(text):
            html_parts.append(self._escape_html(text[last_pos:]))
        
        return ''.join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """HTML转义"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;')
                   .replace('\n', '<br>'))
    
    def _get_chunk_content_by_id(self, chunks: List[Dict], chunk_id: str) -> str:
        """
        根据chunk_id获取chunk内容
        
        Args:
            chunks: 文档块列表
            chunk_id: 块ID
            
        Returns:
            块内容，如果未找到返回空字符串
        """
        for chunk in chunks:
            if chunk['id'] == chunk_id:
                return chunk['content']
        return ""
    
    def compare_documents(self, text_a: str, text_b: str, filename_a: str = "Document A", filename_b: str = "Document B") -> Dict:
        """
        比较两个文档并返回完整的比对结果
        
        Args:
            text_a: 文档A内容
            text_b: 文档B内容  
            filename_a: 文档A文件名
            filename_b: 文档B文件名
            
        Returns:
            包含比对结果的字典
        """
        logger.info(f"开始比较文档: {filename_a} vs {filename_b}")
        
        # 分块处理
        chunks_a = self.split_into_chunks(text_a)
        chunks_b = self.split_into_chunks(text_b)
        
        logger.info(f"文档A分块数: {len(chunks_a)}, 文档B分块数: {len(chunks_b)}")
        
        # 找到匹配块
        matches = self.find_best_matches(chunks_a, chunks_b)
        
        logger.info(f"找到 {len(matches)} 个匹配块")
        
        # 生成带高亮的HTML
        html_a = self.convert_to_html_with_highlights(text_a, chunks_a, matches, is_doc_a=True)
        html_b = self.convert_to_html_with_highlights(text_b, chunks_b, matches, is_doc_a=False)
        
        # 计算整体相似度
        overall_similarity = self.calculate_similarity(text_a, text_b)
        
        # 统计匹配信息
        high_matches = len([m for m in matches if m['match_type'] == 'high'])
        medium_matches = len([m for m in matches if m['match_type'] == 'medium'])
        
        result = {
            'document_a': {
                'filename': filename_a,
                'content': text_a,
                'html_content': html_a,
                'chunks_count': len(chunks_a)
            },
            'document_b': {
                'filename': filename_b, 
                'content': text_b,
                'html_content': html_b,
                'chunks_count': len(chunks_b)
            },
            'comparison': {
                'overall_similarity': overall_similarity,
                'total_matches': len(matches),
                'high_similarity_matches': high_matches,
                'medium_similarity_matches': medium_matches,
                'match_links': [
                    {
                        'chunk_a_id': match['chunk_a_id'],
                        'chunk_b_id': match['chunk_b_id'],
                        'chunk_a': self._get_chunk_content_by_id(chunks_a, match['chunk_a_id']),
                        'chunk_b': self._get_chunk_content_by_id(chunks_b, match['chunk_b_id']),
                        'similarity': match['similarity'],
                        'match_type': match['match_type'],
                        'link_id': f"link_{match['chunk_a_id']}_{match['chunk_b_id']}"
                    }
                    for match in matches
                ]
            },
            'metadata': {
                'comparison_time': None,  # 可以添加时间戳
                'algorithm_params': {
                    'similarity_threshold_high': self.similarity_threshold_high,
                    'similarity_threshold_medium': self.similarity_threshold_medium,
                    'chunk_size': self.chunk_size
                }
            }
        }
        
        logger.info(f"文档比对完成，整体相似度: {overall_similarity:.3f}")
        
        return result

# 全局比对器实例
document_comparator = DocumentComparator()