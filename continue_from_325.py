#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从第326个案件继续爬取
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
from datetime import datetime

def connect_browser():
    """连接到已打开的浏览器"""
    options = webdriver.EdgeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    return webdriver.Edge(options=options)

def wait_for_case_list(driver):
    """等待案件列表加载"""
    print("⏳ 等待案件标题加载...")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.caseName"))
        )
        print("✅ 案件标题已加载")
        return True
    except:
        print("❌ 等待超时")
        return False

def get_case_list_from_page(driver):
    """从当前页面提取案件列表"""
    cases = []
    case_divs = driver.find_elements(By.CSS_SELECTOR, "div.LM_list")
    
    print(f"✅ 找到 {len(case_divs)} 个案件")
    
    for i, elem in enumerate(case_divs, 1):
        try:
            title_elem = elem.find_element(By.CSS_SELECTOR, "a.caseName")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")
            
            try:
                court = elem.find_element(By.CSS_SELECTOR, "span.slfyName").text.strip()
            except:
                court = ""
            
            try:
                case_no = elem.find_element(By.CSS_SELECTOR, "span.ah").text.strip()
            except:
                case_no = ""
            
            try:
                date = elem.find_element(By.CSS_SELECTOR, "span.cprq").text.strip()
            except:
                date = ""
            
            cases.append({
                "标题": title,
                "法院": court,
                "案号": case_no,
                "日期": date,
                "链接": link
            })
            
        except Exception as e:
            print(f"  ⚠️ 案件 {i} 提取失败：{e}")
            continue
    
    return cases

def get_case_detail(driver, case_info):
    """访问详情页"""
    link = case_info["链接"]
    print(f"  🔗 访问详情页: {case_info['标题'][:40]}...")
    
    main_window = driver.current_window_handle
    new_window = None
    
    try:
        all_links = driver.find_elements(By.CSS_SELECTOR, "a.caseName")
        link_element = None
        for elem in all_links:
            if elem.text.strip() == case_info["标题"]:
                link_element = elem
                break
        
        if not link_element:
            print(f"  ⚠️ 未找到链接元素，回退到 window.open")
            driver.execute_script(f"window.open('{link}', '_blank');")
        else:
            driver.execute_script("arguments[0].setAttribute('target', '_blank');", link_element)
            link_element.click()
        
        time.sleep(3)
        
        all_windows = driver.window_handles
        new_windows = [w for w in all_windows if w != main_window]
        
        if not new_windows:
            print(f"  ⚠️ 新窗口未打开")
            return ""
        
        new_window = new_windows[0]
        driver.switch_to.window(new_window)
        time.sleep(5)
        
        content = ""
        selectors = [
            "div.content", "div.document", "div.detail-content", "div.wsContent",
            "div#content", "div.main-content", "body"
        ]
        
        for selector in selectors:
            try:
                content_elem = driver.find_element(By.CSS_SELECTOR, selector)
                content = content_elem.text.strip()
                if content and len(content) > 100:
                    break
            except:
                continue
        
        if not content:
            content = driver.find_element(By.TAG_NAME, "body").text.strip()
        
        if new_window and driver.current_window_handle == new_window:
            driver.close()
        
        driver.switch_to.window(main_window)
        time.sleep(1)
        
        return content
        
    except Exception as e:
        print(f"  ❌ 详情页获取失败: {e}")
        try:
            current = driver.current_window_handle
            if current != main_window and new_window and current == new_window:
                driver.close()
            driver.switch_to.window(main_window)
        except:
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
        return ""

def go_to_next_page(driver):
    """翻到下一页（照搬自start.py）"""
    try:
        # 记录当前页第一个案件的标题，用于判断是否真的翻页了
        try:
            old_first_title = driver.find_element(By.CSS_SELECTOR, "div.LM_list a.caseName").text.strip()
        except:
            old_first_title = ""
        
        # 先滚动到页面底部，确保翻页按钮可见
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # 尝试多种下一页按钮选择器
        next_selectors = [
            (By.LINK_TEXT, "下一页"),
            (By.PARTIAL_LINK_TEXT, "下一页"),
            (By.CSS_SELECTOR, ".next-page"),
            (By.CSS_SELECTOR, "a[title='下一页']"),
            (By.XPATH, "//a[contains(text(), '下一页') and not(contains(@class, 'disabled'))]"),
            (By.XPATH, "//button[contains(text(), '下一页')]"),
        ]
        
        for by, selector in next_selectors:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                
                # 滚动到按钮位置
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                
                # 点击
                next_button.click()
                print("✅ 已点击翻页按钮")
                
                # 等待新页面加载（最多15秒）
                for i in range(15):
                    time.sleep(1)
                    try:
                        new_first_title = driver.find_element(By.CSS_SELECTOR, "div.LM_list a.caseName").text.strip()
                        if new_first_title and new_first_title != old_first_title:
                            print(f"✅ 确认翻页成功（第一个案件已变化）")
                            time.sleep(2)  # 额外等待确保稳定
                            return True
                    except:
                        pass
                
                print("⚠️ 翻页后页面没有变化，尝试下一个选择器")
                continue
                
            except:
                continue
        
        print("❌ 未找到下一页按钮")
        return False
        
    except Exception as e:
        print(f"❌ 翻页失败: {e}")
        return False

def save_case_to_csv(case, csv_file, is_first=False):
    """边爬边保存到CSV"""
    os.makedirs("data", exist_ok=True)
    fieldnames = ['序号', '标题', '法院', '案号', '日期', '链接', '正文']
    mode = 'w' if is_first else 'a'
    with open(csv_file, mode, encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_first:
            writer.writeheader()
        writer.writerow(case)

def main():
    print("=" * 60)
    print("🚀 继续爬取（从第326个开始）")
    print("=" * 60)
    
    driver = connect_browser()
    
    # 生成新文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"data/裁判文书_续_{timestamp}.csv"
    
    start_num = 325  # 已经爬了325个
    total_count = start_num
    target_count = 500
    page_num = 66  # 第66页
    
    print(f"\n💾 保存文件：{csv_file}")
    print(f"📝 从第 {start_num + 1} 个案件继续\n")
    
    while total_count < target_count:
        print(f"\n📄 正在爬取第 {page_num} 页...")
        
        if not wait_for_case_list(driver):
            break
        
        cases = get_case_list_from_page(driver)
        
        if not cases:
            print("❌ 当前页没有案件")
            break
        
        for case in cases:
            if total_count >= target_count:
                break
            
            content = get_case_detail(driver, case)
            case["正文"] = content
            total_count += 1
            case["序号"] = total_count
            
            save_case_to_csv(case, csv_file, is_first=(total_count == start_num + 1))
            
            print(f"  ✅ [{total_count}/{target_count}] {case['标题'][:40]}... (正文: {len(content)}字) - 已保存")
        
        print(f"📊 已收集并保存：{total_count} / {target_count}")
        
        if total_count >= target_count:
            break
        
        # 翻页（先尝试自动，失败则手动）
        print("\n⏭️ 点击下一页...")
        if not go_to_next_page(driver):
            print("⚠️ 自动翻页失败，切换到手动模式")
            print("=" * 60)
            print("👉 请在浏览器中【手动点击下一页】")
            print("   等页面加载完成后，按【回车键】继续爬取")
            print("   如果没有更多页面，直接按 Ctrl+C 退出")
            print("=" * 60)
            try:
                input("按回车继续...")
                # 等待一下确保页面加载
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n用户中断")
                break
        
        page_num += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！本次新增 {total_count - start_num} 个案件")
    print(f"📊 总计：{total_count} / {target_count}")
    print("=" * 60)
    print(f"\n💾 新数据已保存到：{csv_file}")
    print(f"💾 之前数据在：data/judgments_part1.csv")
    print(f"\n💡 提示：可以用 Excel 或 Python 合并两个文件\n")

if __name__ == "__main__":
    main()
