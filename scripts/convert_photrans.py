import re
import sys
import os

def replace_photrans(text):
    # 匹配 {{photrans|文本|注音}}，其中文本和注音不包含 | 或 }
    pattern = r'\{\{photrans\|([^|}]+)\|([^|}]+)\}\}'
    return re.sub(pattern, r'\1（\2）', text)

def main():
    if len(sys.argv) != 2:
        print("用法: python script.py <输入文件路径>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        print(f"错误: 文件 '{input_path}' 不存在。")
        sys.exit(1)

    # 读取输入文件
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        sys.exit(1)

    # 处理内容
    converted_content = replace_photrans(content)

    # 生成输出文件名（在同一目录）
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(dir_name, f"{name}_converted{ext}")

    # 写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        print(f"处理完成，已保存到: {output_path}")
    except Exception as e:
        print(f"写入文件时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()