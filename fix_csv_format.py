# -*- coding: utf-8 -*-
"""
修复CSV格式问题：
1. 确保正文字段里的换行符不会破坏CSV结构
2. 将正文中的多余换行符替换为空格或特殊标记
"""
import csv

print("=" * 70)
print("🔧 修复CSV格式问题")
print("=" * 70)

# 读取原始数据
print("\n📂 读取原始CSV...")
try:
    with open('data/裁判文书_完整版_500条.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    print(f"✅ 成功读取 {len(rows)} 条记录")
except Exception as e:
    print(f"❌ 读取失败: {e}")
    exit(1)

# 处理每条记录
print("\n🔄 正在处理数据...")
for i, row in enumerate(rows, 1):
    # 清理正文中的换行符
    if '正文' in row:
        original_text = row['正文']
        # 将正文中的换行符替换为空格（保持可读性）
        # 但多个连续换行符只保留一个空格
        cleaned_text = ' '.join(line.strip() for line in original_text.split('\n') if line.strip())
        row['正文'] = cleaned_text
    
    if i % 100 == 0:
        print(f"  已处理 {i}/{len(rows)}")

print(f"✅ 处理完成！")

# 保存为标准CSV格式
output_file = 'data/裁判文书_标准格式_500条.csv'
print(f"\n💾 保存到: {output_file}")

try:
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['序号', '标题', '法院', '案号', '日期', '性别', '判决结果', '链接', '正文']
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    print("✅ 保存成功！")
except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)

# 验证结果
print("\n📊 验证结果...")
with open(output_file, 'r', encoding='utf-8-sig') as f:
    verify_rows = list(csv.DictReader(f))

print(f"  原始记录数: {len(rows)}")
print(f"  保存后记录数: {len(verify_rows)}")

if len(rows) == len(verify_rows):
    print("  ✅ 记录数一致")
else:
    print(f"  ⚠️ 记录数不一致！差异: {abs(len(rows) - len(verify_rows))}")

# 显示前3条数据
print("\n📝 前3条数据预览:")
print("-" * 70)
for i, row in enumerate(verify_rows[:3], 1):
    print(f"\n[案件 {i}]")
    print(f"  标题: {row.get('标题', '')[:50]}...")
    print(f"  法院: {row.get('法院', '')}")
    print(f"  案号: {row.get('案号', '')}")
    print(f"  性别: {row.get('性别', '') or '(空)'}")
    print(f"  判决: {row.get('判决结果', '')[:60] or '(空)'}...")
    print(f"  正文长度: {len(row.get('正文', ''))} 字符")

print("\n" + "=" * 70)
print("🎉 完成！")
print("=" * 70)
print(f"\n生成文件: {output_file}")
print("说明：正文中的换行符已替换为空格，确保CSV格式正确")
print()


