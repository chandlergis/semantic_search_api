import re
import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher
import numpy as np

logger = logging.getLogger(__name__)

class DocumentComparator:
    """文档比对器 - 实现双文件相似度检测和差异高亮"""
    
    def __init__(self, 
                 similarity_threshold_high: float = 0.9,
                 similarity_threshold_medium: float = 0.7,
                 min_block_length: int = 3, # 至少连续匹配3句话才算一个块
                 **kwargs):
        self.similarity_threshold_high = similarity_threshold_high
        self.similarity_threshold_medium = similarity_threshold_medium
        self.min_block_length = min_block_length

    def split_into_sentences(self, text: str, offset: int = 0) -> List[Dict[str, Any]]:
        if not text:
            return []
        # 更鲁棒的句子分割，处理各种换行和空格
        text = re.sub(r'\s+', ' ', text).strip()
        regex_splitter = r'([^。！？.?!;]+[。！？.?!;]?)'
        raw_sentences = [s.strip() for s in re.findall(regex_splitter, text) if s.strip()]
        
        sentences_data = []
        current_pos = 0
        for i, sentence_content in enumerate(raw_sentences):
            start_pos = text.find(sentence_content, current_pos)
            if start_pos == -1:
                continue
            end_pos = start_pos + len(sentence_content)
            sentences_data.append({
                'id': f'sent_{i}',
                'content': sentence_content,
                'start_pos': start_pos + offset,
                'end_pos': end_pos + offset
            })
            current_pos = end_pos
        return sentences_data

    def _calculate_raw_similarity(self, text1: str, text2: str) -> float:
        """基础的文本相似度计算"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()

    def find_matching_blocks(self, sents_a: List[Dict], sents_b: List[Dict]) -> List[Dict]:
        """使用动态规划查找连续的高相似度句子块"""
        if not sents_a or not sents_b:
            return []

        # 1. 创建相似度矩阵
        num_a, num_b = len(sents_a), len(sents_b)
        sim_matrix = np.zeros((num_a, num_b))
        for i in range(num_a):
            for j in range(num_b):
                sim = self._calculate_raw_similarity(sents_a[i]['content'], sents_b[j]['content'])
                if sim >= self.similarity_threshold_medium:
                    sim_matrix[i, j] = sim

        # 2. 动态规划查找连续块
        dp = np.zeros_like(sim_matrix, dtype=int)
        matches = []
        for i in range(num_a):
            for j in range(num_b):
                if sim_matrix[i, j] > 0:
                    if i > 0 and j > 0:
                        dp[i, j] = dp[i-1, j-1] + 1
                    else:
                        dp[i, j] = 1
        
        # 3. 提取并合并块
        visited = np.zeros_like(dp, dtype=bool)
        for i in range(num_a - 1, -1, -1):
            for j in range(num_b - 1, -1, -1):
                if dp[i, j] > 0 and not visited[i, j]:
                    length = dp[i, j]
                    if length >= self.min_block_length:
                        start_a, start_b = i - length + 1, j - length + 1
                        
                        # 标记为已访问
                        for k in range(length):
                            visited[start_a + k, start_b + k] = True
                        
                        block_a = sents_a[start_a : i + 1]
                        block_b = sents_b[start_b : j + 1]
                        
                        content_a = "".join([s['content'] for s in block_a])
                        content_b = "".join([s['content'] for s in block_b])
                        
                        # 重新计算整个块的精确相似度
                        block_similarity = self._calculate_raw_similarity(content_a, content_b)
                        match_type = 'high' if block_similarity >= self.similarity_threshold_high else 'medium'

                        matches.append({
                            'chunk_a_id': block_a[0]['id'],
                            'chunk_b_id': block_b[0]['id'],
                            'chunk_a': content_a,
                            'chunk_b': content_b,
                            'similarity': block_similarity,
                            'match_type': match_type,
                            'original_sentences_a': block_a,
                            'original_sentences_b': block_b
                        })
        
        logger.info(f"找到 {len(matches)} 个连续匹配块")
        return sorted(matches, key=lambda m: m['similarity'], reverse=True)

    def convert_to_html_with_highlights(self, text: str, sentences: List[Dict], matches: List[Dict], is_doc_a: bool = True) -> str:
        highlight_map = {}
        for match in matches:
            original_sentences = match['original_sentences_a'] if is_doc_a else match['original_sentences_b']
            for sent in original_sentences:
                highlight_map[sent['id']] = match

        html_parts = []
        last_pos = 0
        sorted_sentences = sorted(sentences, key=lambda s: s['start_pos'])

        i = 0
        while i < len(sorted_sentences):
            sentence = sorted_sentences[i]
            match_info = highlight_map.get(sentence['id'])

            if match_info:
                original_block = match_info['original_sentences_a'] if is_doc_a else match_info['original_sentences_b']
                start_char = original_block[0]['start_pos']
                end_char = original_block[-1]['end_pos']
                
                # 安全检查，确保 start_char 和 end_char 不会超出文本范围
                if start_char >= len(text) or end_char > len(text) or start_char > end_char:
                    i += len(original_block)
                    continue

                block_content = text[start_char:end_char]

                if start_char > last_pos:
                    html_parts.append(self._escape_html(text[last_pos:start_char]))

                css_class = f"highlight-{match_info['match_type']}"
                link_id = f"link_{match_info['chunk_a_id']}_{match_info['chunk_b_id']}"
                html_parts.append(
                    f'<span class="{css_class}" id="{link_id}" data-match-type="{match_info["match_type"]}" '
                    f'data-similarity="{match_info["similarity"]:.3f}">{self._escape_html(block_content)}</span>'
                )
                last_pos = end_char
                i += len(original_block)
            else:
                # 安全检查
                if sentence['start_pos'] > last_pos and sentence['start_pos'] < len(text):
                     html_parts.append(self._escape_html(text[last_pos:sentence['start_pos']]))
                
                if sentence['start_pos'] < len(text) and sentence['end_pos'] <= len(text):
                    html_parts.append(self._escape_html(sentence['content']))
                    last_pos = sentence['end_pos']
                i += 1

        if last_pos < len(text):
            html_parts.append(self._escape_html(text[last_pos:]))
        
        return ''.join(html_parts)

    def _escape_html(self, text: str) -> str:
        return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                   .replace('"', '&quot;').replace("'", '&#x27;').replace('\n', '<br>'))

    def compare_documents(self, text_a: str, text_b: str, filename_a: str = "Document A", filename_b: str = "Document B") -> Dict:
        logger.info(f"开始比较文档: {filename_a} vs {filename_b}")
        
        # 识别并分离垃圾前缀
        garbage_pattern = re.compile(r'^[a-zA-Z0-9\-_~]{20,}\s*')
        
        prefix_a_match = garbage_pattern.match(text_a)
        offset_a = len(prefix_a_match.group(0)) if prefix_a_match else 0
        clean_text_a = text_a[offset_a:]
        
        prefix_b_match = garbage_pattern.match(text_b)
        offset_b = len(prefix_b_match.group(0)) if prefix_b_match else 0
        clean_text_b = text_b[offset_b:]

        if offset_a > 0: logger.info(f"在 {filename_a} 中检测到并移除 {offset_a} 字符的前缀")
        if offset_b > 0: logger.info(f"在 {filename_b} 中检测到并移除 {offset_b} 字符的前缀")

        # 使用清理后的文本进行句子分割，并传入偏移量
        sentences_a = self.split_into_sentences(clean_text_a, offset=offset_a)
        sentences_b = self.split_into_sentences(clean_text_b, offset=offset_b)
        
        matches = self.find_matching_blocks(sentences_a, sentences_b)
        
        # 使用原始文本生成HTML，因为偏移量已经修正了位置
        html_a = self.convert_to_html_with_highlights(text_a, sentences_a, matches, is_doc_a=True)
        html_b = self.convert_to_html_with_highlights(text_b, sentences_b, matches, is_doc_a=False)
        
        # 基于清理后的文本计算相似度
        total_chars_a = len(clean_text_a)
        matched_chars_a = sum(len(m['chunk_a']) for m in matches)
        overall_similarity = matched_chars_a / total_chars_a if total_chars_a > 0 else 0
        logger.info(f"文档比对完成，整体相似度: {overall_similarity:.3f}")
        
        high_matches = len([m for m in matches if m['match_type'] == 'high'])
        medium_matches = len([m for m in matches if m['match_type'] == 'medium'])
        
        return {
            'document_a': {
                'filename': filename_a,
                'content': text_a,
                'html_content': html_a,
                'chunks_count': len(sentences_a)
            },
            'document_b': {
                'filename': filename_b, 
                'content': text_b,
                'html_content': html_b,
                'chunks_count': len(sentences_b)
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
                        'chunk_a': match['chunk_a'],
                        'chunk_b': match['chunk_b'],
                        'similarity': match['similarity'],
                        'match_type': match['match_type'],
                        'link_id': f"link_{match['chunk_a_id']}_{match['chunk_b_id']}"
                    }
                    for match in matches
                ]
            },
            'metadata': {
                'algorithm_params': {
                    'similarity_threshold_high': self.similarity_threshold_high,
                    'similarity_threshold_medium': self.similarity_threshold_medium,
                    'min_block_length': self.min_block_length
                }
            }
        }

# 全局比对器实例
document_comparator = DocumentComparator()