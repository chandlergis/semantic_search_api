"""
极速 Markdown 文本过滤器
基于实测结果优化，专注于真正提升性能的策略
"""

class OptimizedMarkdownFilter:
    """
    优化的 Markdown 文本过滤器
    基于实际性能测试结果优化
    """
    
    # 使用类变量减少初始化开销
    SPECIAL_CHARS = frozenset('#*_~`[]()!|>')
    WHITESPACE = frozenset(' \t\r\n')
    LIST_MARKERS = frozenset('-*+')
    
    # 预编译的转换表（类级别，只创建一次）
    TRANS_TABLE = str.maketrans({
        '*': '',
        '_': '',
        '~': '',
        '`': '',
        '|': ' ',
        '#': ' ',
        '>': ' ',
        '[': '',
        ']': '',
        '!': '',
    })
    
    @staticmethod
    def extract_lightning_fast(markdown_text: str) -> str:
        """
        闪电版：极简实现，最高性能
        使用最少的条件判断和字符串操作
        """
        if not markdown_text:
            return ""
        
        # 步骤1: 快速移除明显的 Markdown 符号
        text = markdown_text.translate(OptimizedMarkdownFilter.TRANS_TABLE)
        
        # 步骤2: 处理括号内容（链接URL）- 使用 while 循环避免递归
        while '(' in text and ')' in text:
            start = text.find('(')
            end = text.find(')', start)
            if start != -1 and end != -1:
                # 检查是否是 URL（简单判断）
                content = text[start+1:end]
                if 'http' in content or 'www' in content or '/' in content:
                    text = text[:start] + ' ' + text[end+1:]
                else:
                    break
            else:
                break
        
        # 步骤3: 快速处理行首标记（使用列表推导式）
        lines = text.split('\n')
        result = []
        
        for line in lines:
            if not line:
                continue
                
            # 快速跳过列表标记
            stripped = line.lstrip()
            if stripped:
                # 处理无序列表
                if stripped[0] in '-+' and len(stripped) > 1 and stripped[1] == ' ':
                    line = stripped[2:]
                # 处理有序列表（简化判断）
                elif stripped[0].isdigit():
                    dot_idx = stripped.find('. ')
                    if 0 < dot_idx < 4:  # 1. 2. ... 99.
                        line = stripped[dot_idx+2:]
                
                # 清理空白
                line = ' '.join(line.split())
                if line:
                    result.append(line)
        
        return '\n'.join(result)
    
    @staticmethod
    def extract_balanced(markdown_text: str) -> str:
        """
        平衡版：在速度和准确性之间取得平衡
        处理大部分常见的 Markdown 语法
        """
        if not markdown_text:
            return ""
        
        result = []
        lines = markdown_text.split('\n')
        
        in_code_block = False
        
        for line in lines:
            # 处理代码块
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                result.append(line)
                continue
            
            # 跳过空行
            if not line.strip():
                continue
            
            # 处理标题（移除 # 符号）
            if line.lstrip().startswith('#'):
                line = line.lstrip('#').strip()
            
            # 处理列表项
            stripped = line.lstrip()
            if stripped:
                # 无序列表
                if len(stripped) > 2 and stripped[0] in '-*+' and stripped[1] == ' ':
                    line = stripped[2:]
                    # 处理任务列表 [ ] 或 [x]
                    if line.startswith('[') and len(line) > 3 and line[2] == ']':
                        line = line[4:]
                # 有序列表
                elif stripped[0].isdigit():
                    dot_idx = stripped.find('. ')
                    if 0 < dot_idx < 4:
                        line = stripped[dot_idx+2:]
                # 引用
                elif stripped.startswith('>'):
                    line = stripped[1:].lstrip()
            
            # 处理行内格式（使用 replace 链式调用，比正则快）
            # 加粗
            while '**' in line:
                start = line.find('**')
                if start == -1:
                    break
                end = line.find('**', start + 2)
                if end == -1:
                    break
                line = line[:start] + line[start+2:end] + line[end+2:]
            
            # 斜体
            for marker in ['*', '_']:
                while marker in line:
                    start = line.find(marker)
                    if start == -1:
                        break
                    # 确保不是列表标记
                    if start > 0 and line[start-1] not in ' \n':
                        end = line.find(marker, start + 1)
                        if end != -1 and end > start + 1:
                            line = line[:start] + line[start+1:end] + line[end+1:]
                        else:
                            break
                    else:
                        break
            
            # 删除线
            line = line.replace('~~', '')
            
            # 行内代码（简单处理）
            while '`' in line:
                start = line.find('`')
                if start == -1:
                    break
                end = line.find('`', start + 1)
                if end == -1:
                    break
                line = line[:start] + line[start+1:end] + line[end+1:]
            
            # 链接 [text](url)
            while '[' in line and '](' in line and ')' in line:
                start = line.find('[')
                mid = line.find('](', start)
                end = line.find(')', mid) if mid != -1 else -1
                if start != -1 and mid != -1 and end != -1:
                    text = line[start+1:mid]
                    line = line[:start] + text + line[end+1:]
                else:
                    break
            
            # 图片 ![alt](url)
            while '![' in line and '](' in line and ')' in line:
                start = line.find('![')
                mid = line.find('](', start)
                end = line.find(')', mid) if mid != -1 else -1
                if start != -1 and mid != -1 and end != -1:
                    alt = line[start+2:mid]
                    line = line[:start] + alt + line[end+1:]
                else:
                    break
            
            # 清理表格分隔符
            if '|' in line:
                # 检查是否是表格分隔行
                if all(c in '-|: ' for c in line):
                    continue
                line = line.replace('|', ' ')
            
            # 最终清理
            line = ' '.join(line.split())
            if line:
                result.append(line)
        
        return '\n'.join(result)
    
    @staticmethod 
    def extract_for_pdf_matching(markdown_text: str) -> str:
        """
        专门为 PDF 匹配优化的版本
        确保输出格式与 PyMuPDF 提取的文本一致
        """
        if not markdown_text:
            return ""
        
        # 使用闪电版提取
        text = OptimizedMarkdownFilter.extract_lightning_fast(markdown_text)
        
        # PDF 匹配特殊处理
        # 1. 统一换行符为空格（PDF 中的换行通常是空格）
        text = text.replace('\n\n', '\n')  # 段落分隔保留单个换行
        text = text.replace('\n', ' ')     # 行内换行变空格
        
        # 2. 合并多个空格
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        # 3. 移除首尾空白
        text = text.strip()
        
        return text


class ChunkProcessor:
    """
    分块处理器：用于处理超大文件
    将文本分成小块并行处理
    """
    
    @staticmethod
    def process_in_chunks(markdown_text: str, chunk_size: int = 10000) -> str:
        """
        分块处理大文本
        chunk_size: 每块的字符数
        """
        if len(markdown_text) <= chunk_size:
            return OptimizedMarkdownFilter.extract_balanced(markdown_text)
        
        # 按行分割，避免在单词中间切断
        lines = markdown_text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                # 处理当前块
                chunk_text = '\n'.join(current_chunk)
                processed = OptimizedMarkdownFilter.extract_balanced(chunk_text)
                if processed:
                    chunks.append(processed)
                # 开始新块
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size + 1  # +1 for newline
        
        # 处理最后一块
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            processed = OptimizedMarkdownFilter.extract_balanced(chunk_text)
            if processed:
                chunks.append(processed)
        
        return '\n'.join(chunks)


# 智能选择器
class SmartMarkdownFilter:
    """
    智能过滤器：根据文本特征自动选择最佳算法
    """
    
    @staticmethod
    def extract(markdown_text: str) -> str:
        """
        自动选择最佳提取策略
        """
        if not markdown_text:
            return ""
        
        text_len = len(markdown_text)
        
        # 小文本：使用平衡版（准确性优先）
        if text_len < 5000:
            return OptimizedMarkdownFilter.extract_balanced(markdown_text)
        
        # 中等文本：使用闪电版
        elif text_len < 50000:
            return OptimizedMarkdownFilter.extract_lightning_fast(markdown_text)
        
        # 大文本：分块处理
        else:
            return ChunkProcessor.process_in_chunks(markdown_text)
    
    @staticmethod
    def extract_for_pdf(markdown_text: str) -> str:
        """
        PDF 匹配专用
        """
        return OptimizedMarkdownFilter.extract_for_pdf_matching(markdown_text)


# 性能测试
def benchmark_optimized():
    """优化版本的性能测试"""
    import time
    
    # 生成不同大小的测试数据
    small_text = """
# Title
## Subtitle
This is **bold** and *italic* text.
- List item 1
- List item 2
[Link](http://example.com)
`code block`
""" * 10  # 小文本
    
    medium_text = small_text * 100  # 中等文本
    large_text = small_text * 1000   # 大文本
    
    tests = [
        ("小文本 (1KB)", small_text),
        ("中等文本 (12KB)", medium_text),
        ("大文本 (125KB)", large_text),
    ]
    
    print("优化版本性能测试")
    print("=" * 60)
    
    for name, test_text in tests:
        print(f"\n{name} - {len(test_text)} 字符")
        print("-" * 40)
        
        # 测试闪电版
        start = time.perf_counter()
        for _ in range(100):
            result = OptimizedMarkdownFilter.extract_lightning_fast(test_text)
        elapsed = time.perf_counter() - start
        print(f"闪电版: {elapsed:.4f}秒/100次 = {elapsed/100*1000:.2f}ms/次")
        print(f"  速度: {len(test_text)*100/elapsed/1024:.0f} KB/s")
        
        # 测试平衡版
        start = time.perf_counter()
        for _ in range(100):
            result = OptimizedMarkdownFilter.extract_balanced(test_text)
        elapsed = time.perf_counter() - start
        print(f"平衡版: {elapsed:.4f}秒/100次 = {elapsed/100*1000:.2f}ms/次")
        print(f"  速度: {len(test_text)*100/elapsed/1024:.0f} KB/s")
        
        # 测试智能版
        start = time.perf_counter()
        for _ in range(100):
            result = SmartMarkdownFilter.extract(test_text)
        elapsed = time.perf_counter() - start
        print(f"智能版: {elapsed:.4f}秒/100次 = {elapsed/100*1000:.2f}ms/次")
        print(f"  速度: {len(test_text)*100/elapsed/1024:.0f} KB/s")


# 实际使用示例
def integrate_with_document_parser(markdown_content: str) -> str:
    """
    集成到 document_parser.py 的示例
    """
    # 使用智能过滤器（自动选择最佳策略）
    return SmartMarkdownFilter.extract_for_pdf(markdown_content)


# 准确性测试
def test_accuracy():
    """测试提取的准确性"""
    test_cases = [
        (
            "# Header\n**Bold** and *italic*",
            "Header\nBold and italic"
        ),
        (
            "- Item 1\n- Item 2\n1. First\n2. Second",
            "Item 1\nItem 2\nFirst\nSecond"
        ),
        (
            "[Link text](http://example.com) and `code`",
            "Link text and code"
        ),
        (
            "![Image](image.jpg)\n~~Strikethrough~~",
            "Image\nStrikethrough"
        ),
    ]
    
    print("\n准确性测试")
    print("=" * 60)
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = OptimizedMarkdownFilter.extract_balanced(input_text)
        # 标准化比较（忽略空白差异）
        result_normalized = ' '.join(result.split())
        expected_normalized = ' '.join(expected.split())
        
        status = "✓" if result_normalized == expected_normalized else "✗"
        print(f"测试 {i}: {status}")
        if result_normalized != expected_normalized:
            print(f"  输入: {input_text}")
            print(f"  期望: {expected_normalized}")
            print(f"  实际: {result_normalized}")


if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    benchmark_optimized()
    print()
    test_accuracy()
    
    # 示例使用
    print("\n示例使用:")
    print("=" * 60)
    sample = """
# 个人简历

**姓名**: 张三  
*邮箱*: zhangsan@example.com

## 工作经验

- **软件工程师** @ [某公司](http://company.com) (2020-2024)
  - 开发了 `Python` 应用
  - 性能提升 ~~50%~~ **100%**

1. 第一个成就
2. 第二个成就
    """
    
    print("原始 Markdown:")
    print(sample)
    print("\n提取结果:")
    print(SmartMarkdownFilter.extract_for_pdf(sample))