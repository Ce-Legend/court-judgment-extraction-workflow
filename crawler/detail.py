# -*- coding: utf-8 -*-
"""
详情页模块 - 负责爬取判决书详情页内容
新手提示：这个模块负责打开每个判决书的详细页面，获取完整内容
"""

from selenium.webdriver.common.by import By
import time
from utils.logger import logger
from utils.helper import random_sleep, save_json
from config import RAW_DATA_DIR, SAVE_RAW_HTML
import os

class DetailCrawler:
    """详情页爬虫"""
    
    def __init__(self, browser):
        """
        初始化详情页爬虫
        
        参数：
            browser: BrowserDriver实例
        """
        self.browser = browser
        self.driver = browser.driver
    
    def get_detail(self, case_info):
        """
        获取案件详情
        【支持两种方式】
        1. 如果有link：直接访问URL
        2. 如果link为空但有element：点击元素跳转
        
        参数：
            case_info: 案件基本信息（包含link或element）
        
        返回：
            包含详细内容的案件信息
        """
        try:
            link = case_info.get("link", "")
            element = case_info.get("element")
            
            # 方式1：通过URL访问
            if link:
                logger.info(f"🔗 正在访问详情页：{link}")
                
                # 访问详情页
                success = self.browser.get(link)
                if not success:
                    logger.error(f"❌ 详情页访问失败")
                    return None
                    
            # 方式2：通过点击元素访问
            elif element:
                logger.info(f"🖱️ 点击案件元素 #{case_info.get('index', '?')}...")
                
                try:
                    # 滚动到元素可见位置
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(2)
                    
                    # 查找可点击的元素（<a>标签或整个元素）
                    clickable = None
                    try:
                        # 尝试找到内部的<a>标签
                        clickable = element.find_element(By.TAG_NAME, "a")
                        logger.debug("找到<a>标签")
                    except:
                        # 如果没有<a>标签，尝试找其他可点击元素
                        try:
                            clickable = element.find_element(By.CSS_SELECTOR, "[onclick]")
                            logger.debug("找到带onclick的元素")
                        except:
                            clickable = element
                            logger.debug("使用整个元素")
                    
                    # 记录当前URL
                    old_url = self.driver.current_url
                    
                    # 方法1：尝试JavaScript点击（绕过interactable检查）
                    try:
                        logger.info("尝试JavaScript点击...")
                        self.driver.execute_script("arguments[0].click();", clickable)
                        logger.success("✅ JavaScript点击成功")
                    except Exception as js_error:
                        logger.warning(f"JavaScript点击失败：{str(js_error)}")
                        
                        # 方法2：尝试模拟鼠标点击
                        try:
                            logger.info("尝试ActionChains点击...")
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(self.driver)
                            actions.move_to_element(clickable).click().perform()
                            logger.success("✅ ActionChains点击成功")
                        except Exception as action_error:
                            logger.warning(f"ActionChains点击失败：{str(action_error)}")
                            
                            # 方法3：直接Selenium click
                            logger.info("尝试Selenium click...")
                            clickable.click()
                            logger.success("✅ Selenium click成功")
                    
                    # 等待URL变化（说明跳转成功）
                    logger.info("⏳ 等待页面跳转...")
                    for i in range(15):
                        time.sleep(1)
                        new_url = self.driver.current_url
                        if new_url != old_url:
                            logger.success(f"✅ 页面已跳转: {new_url[:80]}...")
                            break
                        if i == 5:
                            logger.debug(f"等待中... ({i+1}/15)")
                    else:
                        logger.warning("⚠️ 点击后URL未变化，可能未跳转")
                        # 保存页面源代码用于调试
                        debug_file = f"data/debug_no_jump_{case_info.get('index', 'unknown')}.html"
                        try:
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(self.driver.page_source)
                            logger.info(f"📄 已保存页面源代码：{debug_file}")
                        except:
                            pass
                        
                except Exception as e:
                    logger.error(f"❌ 点击元素失败：{str(e)}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    return None
            else:
                logger.warning(f"⚠️ 案件 {case_info.get('title', 'Unknown')} 既没有链接也没有元素引用")
                return None
            
            # 等待页面加载（大幅延长等待时间，让JavaScript执行完成）
            logger.info("⏳ 等待JavaScript动态内容加载...")
            random_sleep(15, 20)  # 增加到15-20秒
            
            # 多次滚动页面，触发内容加载
            try:
                for i in range(3):
                    self.browser.scroll_down(300)
                    time.sleep(2)
                logger.info("📜 已滚动页面，触发动态内容加载")
            except:
                pass
            
            # 再等待一段时间确保内容渲染完成
            time.sleep(5)
            
            # 解析详情页
            detail_data = self._parse_detail_page(case_info)
            
            # 保存原始HTML（如果配置启用）
            if SAVE_RAW_HTML and detail_data:
                self._save_raw_html(detail_data)
            
            # 如果是通过点击访问的，需要返回列表页以便点击下一个
            if element and not link:
                try:
                    logger.info("🔙 返回列表页...")
                    self.driver.back()
                    time.sleep(3)  # 等待列表页重新加载
                except Exception as e:
                    logger.warning(f"⚠️ 返回列表页失败：{str(e)}")
            
            return detail_data
            
        except Exception as e:
            logger.error(f"❌ 获取详情失败：{str(e)}")
            # 如果出错且是点击模式，也尝试返回
            if case_info.get("element") and not case_info.get("link"):
                try:
                    self.driver.back()
                except:
                    pass
            return None
    
    def _parse_detail_page(self, case_info):
        """解析详情页"""
        try:
            # 复制基本信息
            detail = case_info.copy()
            
            # 等待内容区域加载（添加更多可能的选择器）
            content_selectors = [
                (By.ID, "content"),
                (By.CLASS_NAME, "content"),
                (By.CLASS_NAME, "detail-content"),
                (By.CSS_SELECTOR, ".doc-content"),
                (By.CSS_SELECTOR, "#contentHtml"),
                (By.CSS_SELECTOR, ".PDF-container"),
                (By.CSS_SELECTOR, "div[class*='content']"),
                (By.CSS_SELECTOR, "div[id*='content']"),
                (By.CSS_SELECTOR, ".text-content"),
                (By.CSS_SELECTOR, ".document"),
                (By.CSS_SELECTOR, "pre"),  # 有些判决书用pre标签
                (By.XPATH, "//div[contains(text(), '法院')]"),  # 包含"法院"文字的div
            ]
            
            content_elem = None
            for by, selector in content_selectors:
                try:
                    content_elem = self.browser.find_element(by, selector, timeout=5)
                    if content_elem:
                        logger.info(f"找到内容区域：{by}={selector}")
                        break
                except:
                    continue
            
            if content_elem:
                # 获取完整文本
                detail["full_text"] = content_elem.text
                detail["html_content"] = content_elem.get_attribute("innerHTML")
                
                # 检查内容是否真的有效
                if detail["full_text"] and len(detail["full_text"]) > 100:
                    logger.success(f"✅ 获取到判决书内容，长度：{len(detail['full_text'])} 字符")
                else:
                    logger.warning(f"⚠️ 内容可能未加载完全，长度：{len(detail.get('full_text', ''))} 字符")
                    # 保存页面源代码用于调试
                    debug_file = f"data/debug_empty_content_{case_info.get('index', 'unknown')}.html"
                    try:
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(self.driver.page_source)
                        logger.info(f"📄 已保存页面源代码：{debug_file}")
                    except:
                        pass
            else:
                # 如果找不到特定的内容区域，获取整个页面的文本
                logger.warning("⚠️ 未找到特定内容区域，获取整个页面文本")
                detail["full_text"] = self.driver.find_element(By.TAG_NAME, "body").text
                detail["html_content"] = self.driver.page_source
                
                # 保存页面源代码用于调试
                debug_file = f"data/debug_no_element_{case_info.get('index', 'unknown')}.html"
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    logger.info(f"📄 已保存页面源代码：{debug_file}")
                except:
                    pass
            
            # 提取标题（如果列表页没有提取到）
            if not detail.get("title"):
                try:
                    title_elem = self.driver.find_element(By.TAG_NAME, "h1")
                    detail["title"] = title_elem.text
                except:
                    pass
            
            # 记录当前URL
            detail["detail_url"] = self.driver.current_url
            
            return detail
            
        except Exception as e:
            logger.error(f"❌ 解析详情页失败：{str(e)}")
            return None
    
    def _save_raw_html(self, detail_data):
        """保存原始HTML"""
        try:
            case_no = detail_data.get("case_no", "")
            if not case_no:
                # 使用索引作为文件名
                case_no = f"case_{detail_data.get('index', 'unknown')}"
            
            # 清理文件名中的非法字符
            case_no = case_no.replace("/", "_").replace("\\", "_").replace(":", "_")
            
            filename = f"{case_no}.html"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            
            # 保存HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(detail_data.get("html_content", ""))
            
            logger.debug(f"💾 原始HTML已保存：{filepath}")
            
        except Exception as e:
            logger.warning(f"⚠️ 保存原始HTML失败：{str(e)}")
    
    def batch_get_details(self, case_list, start_index=0):
        """
        批量获取案件详情
        
        参数：
            case_list: 案件列表
            start_index: 从第几个开始（用于断点续传）
        
        返回：
            详情列表
        """
        details = []
        total = len(case_list)
        
        logger.info(f"📚 开始批量获取详情，共 {total} 个案件")
        
        for i in range(start_index, total):
            case = case_list[i]
            logger.info(f"📄 [{i+1}/{total}] 正在获取案件详情...")
            
            detail = self.get_detail(case)
            
            if detail:
                details.append(detail)
                logger.success(f"✅ [{i+1}/{total}] 详情获取成功")
            else:
                logger.warning(f"⚠️ [{i+1}/{total}] 详情获取失败")
            
            # 定期保存进度
            from config import CHECKPOINT_INTERVAL
            if (i + 1) % CHECKPOINT_INTERVAL == 0:
                self._save_checkpoint(details, i + 1)
            
            random_sleep(2, 4)
        
        logger.success(f"✅ 批量获取完成，成功 {len(details)}/{total} 个")
        return details
    
    def _save_checkpoint(self, details, index):
        """保存断点"""
        from config import CHECKPOINT_DIR
        from utils.helper import get_timestamp
        
        checkpoint_file = os.path.join(
            CHECKPOINT_DIR, 
            f"checkpoint_{index}_{get_timestamp()}.json"
        )
        
        save_json(details, checkpoint_file)
        logger.info(f"💾 断点已保存：{checkpoint_file}")

