import os
import re
import shutil
import yaml
from typing import List

def convert_ruby_syntax(content: str) -> str:
    """转换注音语法为 <ruby> 标签"""
    pattern = r'([^\s（]+)（(.*?)）'
    return re.sub(
        pattern,
        lambda m: f'<ruby>{m.group(1)}<rt>{m.group(2)}</rt></ruby>',
        content
    )

def parse_front_matter(content: str):
    """解析 Markdown 文件头部的 YAML front matter，返回 (meta, body)"""
    if content.startswith('---\n'):
        parts = content[4:].split('---\n', 1)
        if len(parts) == 2:
            meta_str, body = parts
            try:
                meta = yaml.safe_load(meta_str) or {}
                return meta, body
            except yaml.YAMLError:
                pass
    return {}, content

def split_into_paragraphs(lines: List[str]) -> List[List[str]]:
    """将行列表按空行或 '---' 分割为段落块，保留原始行（包括空行和分隔符）"""
    paragraphs = []
    current_para = []

    for line in lines:
        stripped = line.strip()
        if stripped == '---' or stripped == '':
            if current_para:
                paragraphs.append(current_para)
                current_para = []
            # 将分隔符或空行作为独立段落保留
            paragraphs.append([line])
        else:
            current_para.append(line)
    
    if current_para:
        paragraphs.append(current_para)
    
    return paragraphs

def indent_block(text: str, indent="    ") -> str:
    """为多行文本每行添加缩进（空行保持为空）"""
    if not text:
        return ""
    return '\n'.join(
        indent + line if line else ""
        for line in text.split('\n')
    )

def generate_tabbed_translation(lines: List[str]) -> str:
    """根据段落结构生成标签页内容"""
    original_lines = []
    interleaved_lines = []

    paragraphs = split_into_paragraphs(lines)

    for para in paragraphs:
        first_line_stripped = para[0].strip()
        if len(para) == 1 and (first_line_stripped == '' or first_line_stripped == '---'):
            # 空行或分隔符段落：直接透传
            original_lines.append(para[0])
            interleaved_lines.append(para[0])
        else:
            # 内容段落：判断是否为原文/译文对
            if len(para) % 2 == 0 and len(para) > 0:
                # 偶数行：视为交替的原文/译文
                for i in range(0, len(para), 2):
                    orig = para[i]
                    trans = para[i + 1]
                    original_lines.append(orig)
                    interleaved_lines.append(orig)
                    interleaved_lines.append('')
                    interleaved_lines.append(trans)
            else:
                # 奇数行：视为无翻译的原文（如标题）
                for line in para:
                    original_lines.append(line)
                    interleaved_lines.append(line)

    original_content = '\n'.join(original_lines)
    interleaved_content = '\n'.join(interleaved_lines)

    return f"""=== "翻訳なし"
{indent_block(original_content)}

=== "翻訳あり"
{indent_block(interleaved_content)}
"""

def process_translated_content(body: str) -> str:
    """处理带翻译的正文：提取标题，其余内容生成标签页"""
    lines = body.split('\n')
    
    title_line = None
    content_lines = lines

    # 检查第一行是否为一级标题
    if lines and lines[0].startswith('# '):
        title_line = lines[0]
        # 跳过标题行及其后的空行（最多一个）
        i = 1
        while i < len(lines) and lines[i].strip() == '':
            i += 1
        content_lines = lines[i:]

    tabbed_content = generate_tabbed_translation(content_lines)

    if title_line is not None:
        return f"{title_line}\n\n{tabbed_content}"
    else:
        return tabbed_content

def convert_file(input_path: str, output_path: str):
    """读取文件，根据元数据决定是否生成翻译标签页，并转换注音"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    meta, body = parse_front_matter(raw_content)

    if meta.get('translated') is True:
        try:
            processed_body = process_translated_content(body)
        except Exception as e:
            print(f"⚠️ 警告：翻译处理失败 ({input_path})：{e}")
            processed_body = body
    else:
        processed_body = body

    final_content = convert_ruby_syntax(processed_body)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"✅ 已生成: {output_path}")

def main():
    src_dir = 'src'
    docs_dir = 'docs'

    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    os.makedirs(docs_dir, exist_ok=True)

    for root, _, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith('.md'):
                input_path = os.path.join(root, filename)
                rel_path = os.path.relpath(input_path, src_dir)
                output_path = os.path.join(docs_dir, rel_path)
                convert_file(input_path, output_path)

    print("🎉 所有文件转换完成！")

if __name__ == '__main__':
    main()