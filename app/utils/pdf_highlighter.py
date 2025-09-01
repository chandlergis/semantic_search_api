import fitz  # PyMuPDF
import logging
import tempfile
import os
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HighlightMatch:
    """高亮匹配信息"""
    text: str
    similarity: float
    match_type: str  # 'high', 'medium', 'low'
    
class PDFHighlighter:
    """PDF文本高亮工具"""
    
    def __init__(self):
        # 定义高亮颜色
        self.colors = {
            'high': (1.0, 0.0, 0.0),      # 红色 - 高相似度
            'medium': (1.0, 0.5, 0.0),   # 橙色 - 中相似度
        }
    
    def highlight_pdf_text(self, 
                          pdf_path: str, 
                          highlights: List[HighlightMatch],
                          output_path: Optional[str] = None) -> str:
        """
        在PDF中高亮指定的文本
        
        Args:
            pdf_path: 输入PDF文件路径
            highlights: 需要高亮的文本列表
            output_path: 输出PDF文件路径，如果为None则生成临时文件
            
        Returns:
            输出PDF文件路径
        """
        try:
            # 打开PDF文档
            doc = fitz.open(pdf_path)
            logger.info(f"打开PDF文档: {pdf_path}, 页数: {doc.page_count}")
            logger.info(f"待高亮文本数量: {len(highlights)}")
            
            # 输出样本高亮文本
            for i, highlight in enumerate(highlights[:3]):
                logger.info(f"高亮样本{i+1} ({highlight.match_type}): {highlight.text[:100]}...")
            
            # 统计高亮信息
            total_highlights = 0
            
            # 如果启用调试，先分析PDF文本内容
            if logger.isEnabledFor(logging.DEBUG):
                self._debug_pdf_content(doc, highlights[:3])  # 只分析前3个highlights
            
            # 遍历每一页
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_highlights = 0
                
                # 对每个高亮文本进行处理
                for highlight in highlights:
                    # 预处理文本以提高匹配成功率
                    processed_text = self._preprocess_text_for_search(highlight.text)
                    if not processed_text:
                        continue
                        
                    # 多种搜索策略
                    text_instances = self._search_text_flexible(page, processed_text)
                    
                    if text_instances:
                        # 获取对应的颜色
                        color = self.colors.get(highlight.match_type, self.colors['medium'])
                        
                        # 为每个找到的文本实例添加高亮
                        for inst in text_instances:
                            try:
                                # 添加高亮注解 - 使用更明显的颜色设置
                                highlight_annot = page.add_highlight_annot(inst)
                                
                                # 设置透明度控制的颜色
                                if highlight.match_type == 'high':
                                    # 红色高亮 - 高相似度（透明度0.6）
                                    highlight_annot.set_colors(stroke=(1, 0, 0), fill=(1, 0.6, 0.6))
                                    highlight_annot.set_opacity(0.6)
                                    highlight_annot.set_border(width=1.5)
                                elif highlight.match_type == 'medium':
                                    # 橙色高亮 - 中相似度（透明度0.4）
                                    highlight_annot.set_colors(stroke=(1, 0.4, 0), fill=(1, 0.8, 0.6))
                                    highlight_annot.set_opacity(0.4)
                                    highlight_annot.set_border(width=1)
                                
                                highlight_annot.update()
                                page_highlights += 1
                                logger.info(f"成功高亮文本: {processed_text[:50]}...")
                            except Exception as e:
                                logger.warning(f"高亮文本失败: {str(e)}")
                    else:
                        logger.info(f"未找到文本: {processed_text[:50]}...")
                            
                logger.info(f"第{page_num + 1}页添加了{page_highlights}个高亮")
                total_highlights += page_highlights
            
            # 生成输出路径
            if output_path is None:
                output_path = self._generate_temp_output_path(pdf_path)
            
            # 验证高亮是否正确应用
            verification_result = self._verify_highlights_applied(doc)
            
            # 保存修改后的PDF
            doc.save(output_path)
            doc.close()
            
            logger.info(f"PDF高亮完成，总共添加{total_highlights}个高亮，保存到: {output_path}")
            logger.info(f"验证结果: {verification_result}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF高亮失败: {str(e)}")
            raise ValueError(f"PDF高亮处理失败: {str(e)}")
    
    def highlight_similarity_matches(self,
                                   pdf_path: str,
                                   similarity_data: List[dict],
                                   similarity_threshold_high: float = 0.9,
                                   similarity_threshold_medium: float = 0.7) -> str:
        """
        基于相似度数据高亮PDF文本
        
        Args:
            pdf_path: PDF文件路径
            similarity_data: 相似度匹配数据
            similarity_threshold_high: 高相似度阈值
            similarity_threshold_medium: 中相似度阈值
            
        Returns:
            高亮后的PDF文件路径
        """
        highlights = []
        
        for match in similarity_data:
            # 确定匹配类型（跳过低相似度）
            similarity = match.get('similarity', 0.0)
            if similarity >= similarity_threshold_high:
                match_type = 'high'
            elif similarity >= similarity_threshold_medium:
                match_type = 'medium'
            else:
                continue  # 跳过低相似度
            
            # 创建高亮对象（假设我们高亮待查重文档的文本）
            highlight_text = match.get('chunk_b', '')  # 待查重文档的文本块
            if highlight_text.strip():
                highlights.append(HighlightMatch(
                    text=highlight_text.strip(),
                    similarity=similarity,
                    match_type=match_type
                ))
        
        logger.info(f"准备高亮{len(highlights)}个文本块")
        return self.highlight_pdf_text(pdf_path, highlights)
    
    def _search_text_flexible(self, page, target_text: str) -> list:
        """
        灵活的文本搜索策略
        
        Args:
            page: PDF页面对象
            target_text: 目标文本
            
        Returns:
            找到的文本实例列表
        """
        # 策略1: 直接搜索原文本
        instances = page.search_for(target_text)
        if instances:
            logger.info(f"直接搜索成功: {target_text[:30]}...")
            return instances
        
        # 策略2: 清理文本后搜索（移除多余空格、换行符）
        cleaned_text = ' '.join(target_text.split())
        instances = page.search_for(cleaned_text)
        if instances:
            logger.debug(f"清理后搜索成功: {cleaned_text[:30]}...")
            return instances
        
        # 策略3: 分段搜索（搜索较短的关键片段）
        if len(target_text) > 50:
            # 取前30个字符作为关键片段
            key_fragment = target_text[:30].strip()
            instances = page.search_for(key_fragment)
            if instances:
                logger.debug(f"关键片段搜索成功: {key_fragment}")
                return instances
        
        # 策略4: 逐词搜索找到最佳匹配
        words = target_text.split()
        if len(words) > 3:
            # 尝试搜索前几个词的组合
            for i in range(min(5, len(words)), 2, -1):
                partial_text = ' '.join(words[:i])
                instances = page.search_for(partial_text)
                if instances:
                    logger.debug(f"部分词搜索成功: {partial_text}")
                    return instances
        
        # 策略5: 搜索单个有意义的词（长度>2）
        meaningful_words = [word for word in words if len(word) > 2]
        if meaningful_words:
            for word in meaningful_words[:3]:  # 尝试前3个有意义的词
                instances = page.search_for(word)
                if instances:
                    logger.debug(f"单个词搜索成功: {word}")
                    return instances
        
        # 策略6: 尝试模糊搜索（如果PDF文本可能有OCR错误或格式差异）
        if len(target_text) > 10:
            # 尝试搜索文本的开头部分（可能格式更一致）
            start_text = target_text[:20].strip()
            instances = page.search_for(start_text)
            if instances:
                logger.debug(f"开头文本搜索成功: {start_text}")
                return instances
        
        logger.info(f"所有搜索策略均失败: {target_text[:30]}...")
        return []
    
    def _generate_temp_output_path(self, input_path: str) -> str:
        """生成临时输出文件路径"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        # 使用项目目录下的temp_files文件夹，方便调试
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_files")
        os.makedirs(temp_dir, exist_ok=True)
        output_path = os.path.join(temp_dir, f"{base_name}_highlighted.pdf")
        return output_path
    
    def create_highlighted_copy(self, 
                              original_pdf_path: str,
                              match_links: List[dict],
                              target_doc: str = 'b',  # 默认高亮文档B（待查重文档）
                              **thresholds) -> str:
        """
        创建带高亮的PDF副本
        
        Args:
            original_pdf_path: 原始PDF路径
            match_links: 匹配链接数据
            target_doc: 目标文档 ('a' 或 'b')
            **thresholds: 相似度阈值
            
        Returns:
            高亮PDF的路径
        """
        highlights = []
        
        logger.info(f"开始处理{len(match_links)}个匹配链接")
        
        # 提取需要高亮的文本
        for i, match in enumerate(match_links):
            similarity = match.get('similarity', 0.0)
            
            # 确定匹配类型（跳过低相似度）
            if similarity >= thresholds.get('similarity_threshold_high', 0.9):
                match_type = 'high'
            elif similarity >= thresholds.get('similarity_threshold_medium', 0.7):
                match_type = 'medium'
            else:
                continue  # 跳过低相似度
            
            # 获取对应文档的文本
            if target_doc == 'a':
                text = match.get('chunk_a', '')
            else:
                text = match.get('chunk_b', '')
            
            # 调试信息
            if i < 3:  # 只输出前3个样本
                logger.info(f"匹配{i+1}: 相似度={similarity:.3f}, 类型={match_type}, 文本长度={len(text) if text else 0}")
                if text:
                    logger.info(f"原始文本片段: {text[:100]}...")
            
            if text and text.strip():
                # 预处理文本，提高匹配成功率
                processed_text = self._preprocess_text_for_search(text.strip())
                highlights.append(HighlightMatch(
                    text=processed_text,
                    similarity=similarity,
                    match_type=match_type
                ))
                
                if i < 3:  # 只输出前3个样本的处理结果
                    logger.info(f"处理后文本: {processed_text[:100]}...")
            else:
                if i < 3:
                    logger.info(f"匹配{i+1}: 文本为空，跳过")
                
        logger.info(f"准备高亮{len(highlights)}个文本块，目标文档: {target_doc}")
        
        return self.highlight_pdf_text(original_pdf_path, highlights)
    
    def _preprocess_text_for_search(self, text: str) -> str:
        """
        预处理文本以提高搜索成功率
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 1. 移除首尾空格
        text = text.strip()
        
        # 检查文本是否看起来像编码的二进制数据
        if self._is_likely_binary_data(text):
            logger.warning(f"检测到可能为二进制数据的文本: {text[:100]}...")
            return ""
        
        # 2. 处理常见的PDF文本提取问题
        import re
        
        # 移除换行符和制表符
        text = text.replace('\n', ' ').replace('\t', ' ')
        
        # 将多个连续空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除常见的标记和特殊字符（可能来自Markdown转换）
        text = re.sub(r'[\*\#\-\>\<\[\]\(\)\{\}]', '', text)
        
        # 处理中文标点符号和空格问题
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)  # 移除中文字符间的空格
        
        # 移除首尾的标点符号
        text = text.strip('.,!?;:、，。！？；：')
        
        # 4. 限制最大长度，避免过长的文本块难以匹配
        if len(text) > 200:
            # 取前150个字符，并在词边界处截断
            text = text[:150]
            last_space = text.rfind(' ')
            if last_space > 100:  # 确保不会太短
                text = text[:last_space]
        elif len(text) < 3:
            # 太短的文本可能无法有效搜索
            return ""
        
        logger.debug(f"文本预处理: {text[:50]}...")
        return text
    
    def _is_likely_binary_data(self, text: str) -> bool:
        """
        检查文本是否可能为编码的二进制数据
        
        Args:
            text: 要检查的文本
            
        Returns:
            是否为二进制数据
        """
        if not text:
            return False
            
        # 检查常见二进制数据特征
        # 1. 包含大量十六进制字符 (0-9, a-f, A-F)
        hex_chars = sum(1 for c in text if c in '0123456789abcdefABCDEF')
        if hex_chars / len(text) > 0.7:  # 70%以上为十六进制字符
            return True
            
        # 2. 包含大量下划线和波浪线
        special_chars = sum(1 for c in text if c in '_~')
        if special_chars / len(text) > 0.3:  # 30%以上为特殊字符
            return True
            
        # 3. 长度很长但看起来不像自然语言
        if len(text) > 50 and not any(c.isalpha() for c in text):
            return True
            
        return False
    
    def _verify_highlights_applied(self, doc) -> Dict[str, int]:
        """
        验证高亮是否成功应用到PDF
        
        Args:
            doc: PDF文档对象
            
        Returns:
            统计信息字典
        """
        total_annotations = 0
        highlight_annotations = 0
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            annotations = page.annots()
            page_annotations = 0
            page_highlights = 0
            
            for annot in annotations:
                page_annotations += 1
                if annot.type[1] == 'Highlight':
                    page_highlights += 1
            
            total_annotations += page_annotations
            highlight_annotations += page_highlights
            
            if page_annotations > 0:
                logger.info(f"第{page_num + 1}页发现 {page_annotations} 个注解，其中 {page_highlights} 个高亮")
        
        result = {
            'total_annotations': total_annotations,
            'highlight_annotations': highlight_annotations,
            'pages_with_highlights': sum(1 for page_num in range(doc.page_count) 
                                       if any(annot.type[1] == 'Highlight' 
                                            for annot in doc[page_num].annots()))
        }
        
        logger.info(f"PDF验证结果: 总注解数={total_annotations}, 高亮注解数={highlight_annotations}")
        return result
    
    def highlight_with_html_colors(self, pdf_path: str, highlights: List[HighlightMatch], output_path: Optional[str] = None, similarity_threshold_high: float = 0.9, similarity_threshold_medium: float = 0.7) -> str:
        """
        使用HTML样式在PDF中修改文本颜色
        
        Args:
            pdf_path: 输入PDF文件路径
            highlights: 需要高亮的文本列表
            output_path: 输出PDF文件路径
            
        Returns:
            输出PDF文件路径
        """
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"使用HTML样式处理PDF: {pdf_path}, 页数: {doc.page_count}")
            
            # 创建新的PDF文档
            new_doc = fitz.Document()
            
            total_highlights_applied = 0
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # 获取页面尺寸
                rect = page.rect
                
                # 获取页面文本（使用更好的文本提取方法）
                page_text = page.get_text("text", sort=True)
                
                # 调试：检查原始文本内容
                if page_num < 2:
                    logger.info(f"第{page_num + 1}页原始文本: {repr(page_text[:100])}")
                
                # 创建带HTML样式的新文本
                html_text = page_text
                page_highlights = 0
                
                # 对每个高亮文本添加HTML样式
                for highlight in highlights:
                    # 预处理文本以提高匹配成功率
                    processed_text = self._preprocess_text_for_search(highlight.text)
                    if not processed_text:
                        continue
                        
                    # 使用更智能的文本匹配
                    if processed_text in html_text:
                        # 根据相似度确定颜色（跳过低相似度）
                        if highlight.similarity >= similarity_threshold_high:
                            color = "rgba(255, 0, 0, 0.6)"  # 红色，透明度0.6
                            weight = "bold"
                        elif highlight.similarity >= similarity_threshold_medium:
                            color = "rgba(255, 136, 0, 0.4)"  # 橙色，透明度0.4
                            weight = "bold"
                        else:
                            continue  # 跳过低相似度
                        
                        # 替换文本为带样式的HTML
                        styled_text = f'<span style="color: {color}; font-weight: {weight}; background-color: #ffffcc;">{processed_text}</span>'
                        html_text = html_text.replace(processed_text, styled_text)
                        page_highlights += 1
                        total_highlights_applied += 1
                        logger.info(f"应用HTML样式: {processed_text[:30]} -> {color}")
                
                # 调试：检查HTML内容
                if page_num < 2:  # 只输出前2页的调试信息
                    logger.debug(f"第{page_num + 1}页HTML内容预览: {html_text[:200]}...")
                
                # 创建新页面并插入HTML内容
                new_page = new_doc.new_page(width=rect.width, height=rect.height)
                
                # 使用更完整的CSS样式
                css = """
                body { font-family: inherit; font-size: inherit; line-height: 1.6; }
                span { padding: 1px 2px; border-radius: 2px; }
                """
                
                new_page.insert_htmlbox(rect, html_text, css=css)
                
                logger.info(f"第{page_num + 1}页应用了{page_highlights}个HTML高亮")
            
            # 生成输出路径
            if output_path is None:
                output_path = self._generate_temp_output_path(pdf_path)
            
            # 保存新PDF
            new_doc.save(output_path)
            doc.close()
            new_doc.close()
            
            logger.info(f"HTML样式PDF生成完成，总共应用{total_highlights_applied}个高亮，保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"HTML样式处理失败: {str(e)}")
            raise ValueError(f"HTML样式处理失败: {str(e)}")
    
    def _debug_pdf_content(self, doc, sample_highlights: List[HighlightMatch]):
        """
        调试PDF内容，分析文本提取情况
        
        Args:
            doc: PDF文档对象
            sample_highlights: 样本高亮文本
        """
        logger.debug("=== PDF内容调试分析 ===")
        
        for page_num in range(min(3, doc.page_count)):  # 分析前3页
            page = doc[page_num]
            page_text = page.get_text()
            
            logger.debug(f"第{page_num + 1}页文本长度: {len(page_text)}")
            logger.debug(f"第{page_num + 1}页前300字符: {repr(page_text[:300])}")
            
            # 分析样本高亮文本是否在页面中
            for i, highlight in enumerate(sample_highlights):
                if i >= 3:  # 只分析前3个
                    break
                    
                logger.debug(f"\n--- 高亮文本{i+1}分析 ---")
                logger.debug(f"目标文本: {repr(highlight.text[:100])}")
                
                # 检查直接匹配
                if highlight.text in page_text:
                    logger.debug("✓ 直接匹配成功")
                    continue
                
                logger.debug("✗ 直接匹配失败")
                
                # 检查预处理后的匹配
                processed_text = self._preprocess_text_for_search(highlight.text)
                if processed_text and processed_text in page_text:
                    logger.debug(f"✓ 预处理后匹配成功: {repr(processed_text)}")
                    continue
                    
                # 检查部分匹配
                words = highlight.text.split()
                meaningful_words = [word for word in words if len(word) > 2][:5]  # 取前5个有意义的词
                
                for word_count in range(len(meaningful_words), 0, -1):
                    partial = ' '.join(meaningful_words[:word_count])
                    if partial in page_text:
                        logger.debug(f"✓ 部分匹配成功({word_count}词): {repr(partial)}")
                        break
                else:
                    logger.debug("✗ 部分匹配也失败")
                    
                    # 检查单个词匹配
                    for word in meaningful_words:
                        if word in page_text:
                            logger.debug(f"✓ 单个词匹配成功: {repr(word)}")
                            break
                    else:
                        logger.debug("✗ 所有匹配尝试失败")
        
        logger.debug("=== PDF内容调试结束 ===")

# 全局高亮器实例
pdf_highlighter = PDFHighlighter()