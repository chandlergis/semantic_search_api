import fitz  # PyMuPDF
import logging
import tempfile
import os
import re
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HighlightMatch:
    """高亮匹配信息"""
    text: str
    similarity: float
    match_type: str  # 'high', 'medium'

class PDFHighlighter:
    """PDF文本高亮工具"""
    
    def __init__(self):
        self.colors = {
            'high': (1.0, 0.7, 0.7),  # 淡红色
            'medium': (1.0, 0.9, 0.4), # 淡橙色
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        text = re.sub(r'\s+', ' ', text).strip()
        regex_splitter = r'([^。！？.?!;]+[。！？.?!;]?)'
        raw_sentences = [s.strip() for s in re.findall(regex_splitter, text) if s.strip()]
        return raw_sentences

    def _strip_markdown(self, text: str) -> str:
        """移除文本中的Markdown标记"""
        text = re.sub(r'(\**|__)(.*?)\1', r'\2', text)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'!?\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'^\s*[\*\-+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'^\s*[-_*]{3,}\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        return text

    def highlight_pdf_text(self,
                          pdf_path: str,
                          highlights: List[HighlightMatch],
                          output_path: Optional[str] = None) -> str:
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"打开PDF文档: {pdf_path}, 页数: {doc.page_count}")
            
            total_highlights = 0

            # 1. 将所有待高亮的巨大文本块拆分为句子
            all_sentences_to_highlight = []
            for highlight in highlights:
                sentences = self._split_into_sentences(highlight.text)
                for sentence in sentences:
                    all_sentences_to_highlight.append(
                        (sentence, highlight.match_type)  # 附带颜色类型
                    )
            logger.info(f"拆分为 {len(all_sentences_to_highlight)} 个句子进行高亮")

            # 2. 逐页处理，优化性能
            unmatched_sentences = list(all_sentences_to_highlight)
            for page_num in range(doc.page_count):
                if not unmatched_sentences:  # 如果所有句子都已高亮，提前退出
                    break
                
                page = doc[page_num]
                page_highlights = 0

                # 3. 优化：一次性提取页面文本用于快速预检
                page_text_for_check = page.get_text("text")
                if not page_text_for_check.strip():
                    continue
                normalized_page_text_for_check = self._normalize_for_search(re.sub(r'\s+', '', page_text_for_check))

                found_on_this_page = []
                for sentence, match_type in unmatched_sentences:
                    clean_sentence = self._strip_markdown(sentence)
                    normalized_sentence = self._normalize_for_search(re.sub(r'\s+', '', clean_sentence))

                    if not normalized_sentence:
                        continue

                    # 4. 优化：快速预检，判断句子是否存在于本页
                    if normalized_sentence in normalized_page_text_for_check:
                        # 5. 精确查找并高亮
                        text_instances = self._search_text_flexible(page, clean_sentence)
                        if text_instances:
                            color = self.colors.get(match_type, self.colors['medium'])
                            for inst in text_instances:
                                try:
                                    annot = page.add_highlight_annot(inst)
                                    annot.set_colors(stroke=color)
                                    annot.set_opacity(0.5)
                                    annot.update()
                                    page_highlights += 1
                                except Exception as e:
                                    logger.warning(f"高亮文本失败 for rect {inst}: {str(e)}")
                            
                            found_on_this_page.append((sentence, match_type))
                
                if page_highlights > 0:
                    logger.info(f"第 {page_num + 1} 页添加了 {page_highlights} 个高亮")
                    total_highlights += page_highlights
                    # 从待处理列表中移除已找到的句子
                    unmatched_sentences = [s for s in unmatched_sentences if s not in found_on_this_page]

            if unmatched_sentences:
                logger.warning(f"{len(unmatched_sentences)} 个句子未在PDF中找到匹配项。 সন")
                for i, (text, _) in enumerate(unmatched_sentences[:5]):
                    logger.debug(f"未匹配样本 {i+1}: {text[:100]}...")

            if output_path is None:
                output_path = self._generate_temp_output_path(pdf_path)
            
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            logger.info(f"PDF高亮完成，总共添加 {total_highlights} 个高亮，保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF高亮失败: {str(e)}")
            raise ValueError(f"PDF高亮处理失败: {str(e)}")
    
    def highlight_similarity_matches(self,
                                   pdf_path: str,
                                   similarity_data: List[dict],
                                   similarity_threshold_high: float = 0.9,
                                   similarity_threshold_medium: float = 0.7) -> str:
        highlights = []
        for match in similarity_data:
            similarity = match.get('similarity', 0.0)
            if similarity >= similarity_threshold_high:
                match_type = 'high'
            elif similarity >= similarity_threshold_medium:
                match_type = 'medium'
            else:
                continue
            
            highlight_text = match.get('chunk_b', '')
            if highlight_text.strip():
                highlights.append(HighlightMatch(
                    text=highlight_text.strip(),
                    similarity=similarity,
                    match_type=match_type
                ))
        
        logger.info(f"准备高亮 {len(highlights)} 个文本块")
        return self.highlight_pdf_text(pdf_path, highlights)

    def _normalize_for_search(self, text: str) -> str:
        """标准化文本，移除所有非字母数字字符并转为小写。"""
        return re.sub(r'\W', '', text, flags=re.UNICODE).lower()

    def _search_text_flexible(self, page, target_text: str) -> list:
        """
        在页面中搜索文本，能应对PDF文本提取中的空格和换行问题。
        """
        if not target_text.strip():
            return []

        words = page.get_text("words")
        if not words:
            return []

        page_words = [w[4] for w in words]
        normalized_page_text = self._normalize_for_search("".join(page_words))
        
        text_without_spaces = re.sub(r'\s+', '', target_text)
        normalized_target = self._normalize_for_search(text_without_spaces)

        if not normalized_target:
            return []

        match_start_index = normalized_page_text.find(normalized_target)
        if match_start_index == -1:
            return []

        start_word_index = -1
        end_word_index = -1
        current_len = 0
        for i, word in enumerate(page_words):
            if start_word_index == -1 and current_len >= match_start_index:
                start_word_index = i
            
            current_len += len(self._normalize_for_search(word))
            
            if end_word_index == -1 and current_len >= match_start_index + len(normalized_target):
                end_word_index = i
                break
        
        if start_word_index != -1 and end_word_index != -1:
            return [fitz.Rect(w[:4]) for w in words[start_word_index : end_word_index + 1]]

        return []

    def _generate_temp_output_path(self, input_path: str) -> str:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_files")
        os.makedirs(temp_dir, exist_ok=True)
        timestamp = tempfile.mktemp().split('/')[-1]
        output_path = os.path.join(temp_dir, f"{base_name}_{timestamp}_highlighted.pdf")
        return output_path

    def create_highlighted_copy(self, 
                              original_pdf_path: str,
                              match_links: List[dict],
                              target_doc: str = 'b',  # 默认高亮文档B（待查重文档）
                              **thresholds) -> str:
        highlights = []
        logger.info(f"开始为文档 '{target_doc}' 处理 {len(match_links)} 个匹配链接")
        
        for match in match_links:
            similarity = match.get('similarity', 0.0)
            
            if similarity >= thresholds.get('similarity_threshold_high', 0.9):
                match_type = 'high'
            elif similarity >= thresholds.get('similarity_threshold_medium', 0.7):
                match_type = 'medium'
            else:
                continue
            
            text = match.get('chunk_a', '') if target_doc == 'a' else match.get('chunk_b', '')
            
            if text and text.strip():
                highlights.append(HighlightMatch(
                    text=text.strip(),
                    similarity=similarity,
                    match_type=match_type
                ))
            else:
                logger.debug(f"匹配文本为空，跳过")
                
        logger.info(f"准备为文档 '{target_doc}' 高亮 {len(highlights)} 个文本块")
        return self.highlight_pdf_text(original_pdf_path, highlights)

# 全局高亮器实例
pdf_highlighter = PDFHighlighter()