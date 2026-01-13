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

def process_comment(comment_text: str) -> str:
    """处理评论文本，转换为 Admonition 语法"""
    if not comment_text or not comment_text.strip():
        return ""
    
    # 清理并保留原始格式
    lines = comment_text.strip().split('\n')
    indented_content = '\n'.join(f"    {line}" if line else "    " for line in lines)
    
    return f"""??? quote "Comment"

{indented_content}"""

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
                for i in range(0, len(para), 2):
                    orig = para[i]
                    trans = para[i + 1]
                    original_lines.append(orig)
                    interleaved_lines.append(orig)
                    interleaved_lines.append('')
                    interleaved_lines.append(trans)
            else:
                # 奇数行：视为无翻译原文
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

def process_translated_content(meta: dict, body: str) -> str:
    """处理带翻译的正文，支持 title 和 video"""
    lines = body.split('\n')
    tabbed_content = generate_tabbed_translation(lines)

    parts = []

    # 1. 标题
    title = meta.get('title')
    if title:
        parts.append(f"# {title}")

    # 2. 视频（如果存在）
    video_url = meta.get('video')
    if video_url and isinstance(video_url, str) and video_url.strip():
        video_url = video_url.strip()
        # 使用标准 HTML5 video 标签，带 controls 和响应式
        video_html = f'<video src="{video_url}" controls style="width:100%; max-width:800px; height:auto;"></video>'
        parts.append(video_html)

    # 3. 标签页内容
    parts.append(tabbed_content)

    # 4. 评论（如果有）
    comment = meta.get('comment')
    if comment:
        comment_section = process_comment(comment)
        parts.append(comment_section)

    return '\n\n'.join(parts)

def convert_file(input_path: str, output_path: str):
    """读取文件，根据元数据生成带标题、视频、翻译的内容，并转换注音"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    meta, body = parse_front_matter(raw_content)

    title = meta.get('title')
    video_url = meta.get('video')
    has_video = video_url and isinstance(video_url, str) and video_url.strip()

    if meta.get('translated') is True:
        try:
            processed_body = process_translated_content(meta, body)
        except Exception as e:
            print(f"⚠️ 警告：翻译处理失败 ({input_path})：{e}")
            processed_body = body
    else:
        # 无翻译：普通正文
        parts = []
        if title:
            parts.append(f"# {title}")
        if has_video:
            vid = video_url.strip()
            parts.append(f'<video src="{vid}" controls style="width:100%; max-width:800px; height:auto;"></video>')
        parts.append(body)
        processed_body = '\n\n'.join(parts)

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
            input_path = os.path.join(root, filename)
            rel_path = os.path.relpath(input_path, src_dir)
            output_path = os.path.join(docs_dir, rel_path)

            if filename.endswith('.md'):
                # Markdown 文件：转换
                convert_file(input_path, output_path)
            else:
                # 非 Markdown 文件：直接复制
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy2(input_path, output_path)
                print(f"📎 已复制: {output_path}")

    print("🎉 所有文件转换完成！")

if __name__ == '__main__':
    main()