import os
import re
import shutil

def convert_content(content):
    """转换注音语法为 <ruby> 标签"""
    # 匹配：连续非空白字符 + 全角左括号 + 注音内容 + 全角右括号
    pattern = r'([^\s（]+)（(.*?)）'
    result = re.sub(
        pattern,
        lambda m: f'<ruby>{m.group(1)}<rt>{m.group(2)}</rt></ruby>',
        content
    )
    return result

def convert_file(input_path, output_path):
    """读取文件，转换内容，并写入输出路径"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    converted = convert_content(content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(converted)
    print(f"✅ 已生成: {output_path}")

def main():
    src_dir = 'src'
    docs_dir = 'docs'

    # 清空 docs 目录（确保干净构建）
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    os.makedirs(docs_dir, exist_ok=True)

    # 递归遍历 src/ 所有 .md 文件
    for root, dirs, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith('.md'):
                # 构建输入路径
                input_path = os.path.join(root, filename)

                # 计算相对路径，用于在 docs/ 中重建结构
                rel_path = os.path.relpath(input_path, src_dir)
                output_path = os.path.join(docs_dir, rel_path)

                # 转换并保存
                convert_file(input_path, output_path)

    print("🎉 所有文件转换完成！")

if __name__ == '__main__':
    main()