#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合并两个CSV文件并清理数据
"""
import csv
import re
from datetime import datetime

def clean_content(text):
    """清理正文中的网页元素"""
    if not text:
        return ""
    
    # 删除常见的网页导航元素
    noise_patterns = [
        r'^\d{4}年\d{1,2}月\d{1,2}日\s*星期[一二三四五六日]',
        r'欢迎您.*?使用帮助',
        r'退出\s*意见建议\s*返回主站',
        r'目录',
        r'点击了解更多',
        r'案\s+由',
        r'案\s+号',
        r'文书类型',
        r'审理法院',
        r'审理程序',
        r'裁判日期',
        r'公开类型',
        r'当事人',
        r'案件基本情况',
        r'首页.*?刑事案件.*?民事案件.*?行政案件',
        r'登录.*?注册.*?意见建议',
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
        
        # 跳过包含噪音模式的行
        skip = False
        for pattern in noise_patterns:
            if re.search(pattern, line):
                skip = True
                break
        
        if not skip and len(line) > 2:  # 至少2个字符
            cleaned_lines.append(line)
    
    # 重新组合，去重连续重复的行
    result = []
    prev_line = None
    for line in cleaned_lines:
        if line != prev_line:
            result.append(line)
            prev_line = line
    
    return '\n'.join(result)

def merge_and_clean():
    """合并并清理两个CSV文件"""
    file1 = 'data/judgments_part1.csv'
    file2 = 'data/judgments_part2.csv'
    
    print("=" * 60)
    print("📊 合并并清理裁判文书数据")
    print("=" * 60)
    
    # 读取第一个文件
    print(f"\n📂 读取：{file1}")
    rows1 = []
    with open(file1, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows1 = list(reader)
    print(f"✅ 读取 {len(rows1)} 条数据")
    
    # 读取第二个文件
    print(f"\n📂 读取：{file2}")
    rows2 = []
    with open(file2, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows2 = list(reader)
    print(f"✅ 读取 {len(rows2)} 条数据")
    
    # 合并
    all_rows = rows1 + rows2
    print(f"\n📊 合计：{len(all_rows)} 条数据")
    
    # 清理数据
    print("\n🧹 正在清理数据...")
    cleaned_count = 0
    for i, row in enumerate(all_rows, 1):
        original_length = len(row.get('正文', ''))
        row['正文'] = clean_content(row.get('正文', ''))
        new_length = len(row['正文'])
        
        if new_length < original_length:
            cleaned_count += 1
        
        if i % 50 == 0:
            print(f"  已处理：{i}/{len(all_rows)}")
    
    print(f"✅ 清理完成！共清理了 {cleaned_count} 条数据")
    
    # 统计信息
    total_chars = sum(len(row.get('正文', '')) for row in all_rows)
    empty_count = sum(1 for row in all_rows if len(row.get('正文', '').strip()) == 0)
    
    print(f"\n📈 数据统计：")
    print(f"  总条数：{len(all_rows)}")
    print(f"  空白正文：{empty_count} 条")
    print(f"  有效正文：{len(all_rows) - empty_count} 条")
    print(f"  平均长度：{total_chars // len(all_rows)} 字/条")
    
    # 保存清理后的数据
    output_file = 'data/裁判文书_合并清洗版_500条.csv'
    print(f"\n💾 保存到：{output_file}")
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['序号', '标题', '法院', '案号', '日期', '链接', '正文']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # 重新编号
        for i, row in enumerate(all_rows, 1):
            row['序号'] = i
            writer.writerow(row)
    
    print("✅ 保存成功！")
    
    # 可选：生成纯文本版本（只有标题和正文）
    output_txt = 'data/裁判文书_纯文本版_500条.txt'
    print(f"\n💾 额外生成纯文本版：{output_txt}")
    
    with open(output_txt, 'w', encoding='utf-8') as f:
        for i, row in enumerate(all_rows, 1):
            f.write(f"【案件 {i}】{row.get('标题', '')}\n")
            f.write(f"法院：{row.get('法院', '')}\n")
            f.write(f"案号：{row.get('案号', '')}\n")
            f.write(f"日期：{row.get('日期', '')}\n")
            f.write(f"\n{row.get('正文', '')}\n")
            f.write("\n" + "=" * 60 + "\n\n")
    
    print("✅ 纯文本版生成成功！")
    
    print("\n" + "=" * 60)
    print("🎉 全部完成！")
    print("=" * 60)
    print(f"\n📁 生成的文件：")
    print(f"  1. {output_file} (CSV格式，可用Excel打开)")
    print(f"  2. {output_txt} (纯文本格式，可直接阅读)")
    print()

if __name__ == "__main__":
    merge_and_clean()




