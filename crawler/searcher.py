# -*- coding: utf-8 -*-
"""
搜索模块 - 负责在裁判文书网搜索判决书
新手提示：这个模块负责在网站上输入关键词并获取搜索结果
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from utils.logger import logger
from utils.helper import random_sleep, get_timestamp
from config import WENSHU_LIST_URL, KEYWORD, START_YEAR, END_YEAR

class WenshuSearcher:
    """裁判文书网搜索器"""
    
    def __init__(self, browser):
        """
        初始化搜索器
        
        参数：
            browser: BrowserDriver实例
        """
        self.browser = browser
        self.driver = browser.driver
        self.results = []
    
    def open_wenshu_site(self):
        """确认已打开裁判文书网搜索结果"""
        try:
            # 检查是否是远程模式
            if self.browser.is_remote:
                logger.info("=" * 60)
                logger.info("🌐 远程浏览器模式")
                logger.info("=" * 60)
                
                # 获取当前页面信息
                try:
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    
                    # 检查是否已经在搜索结果页面
                    if "wenshu.court.gov.cn" in current_url:
                        logger.success("✅ 检测到裁判文书网页面")
                        logger.info(f"📄 当前页面：{page_title}")
                        
                        # 等待页面完全加载
                        logger.info("⏳ 等待页面完全加载...")
                        random_sleep(3, 5)
                        
                        # 滚动页面
                        try:
                            self.browser.scroll_down(500)
                            time.sleep(2)
                            logger.info("📜 已滚动页面，触发内容加载")
                        except:
                            pass
                        
                    else:
                        logger.warning(f"⚠️  当前不在裁判文书网页面")
                        logger.warning(f"📍 当前网址：{current_url}")
                        logger.info("💡 程序将跳转到搜索页面...")
                        
                        # 跳转到搜索页面
                        success = self.browser.get(WENSHU_LIST_URL)
                        if not success:
                            logger.error("❌ 跳转失败")
                            return False
                        
                        random_sleep(5, 8)
                        
                except Exception as e:
                    logger.warning(f"⚠️ 获取页面信息失败：{str(e)}")
                
            else:
                # 自动模式：需要导航到搜索页面
                logger.info("🌐 正在打开裁判文书网...")
                logger.info(f"📍 网址：{WENSHU_LIST_URL}")
                
                success = self.browser.get(WENSHU_LIST_URL)
                if not success:
                    logger.error("❌ 裁判文书网打开失败")
                    return False
                
                logger.info("⏳ 等待页面加载...")
                random_sleep(5, 8)
                
                # 滚动页面
                try:
                    self.browser.scroll_down(500)
                    time.sleep(2)
                except:
                    pass
            
            # 保存截图
            screenshot_path = f"data/debug_current_page_{get_timestamp()}.png"
            try:
                self.browser.save_screenshot(screenshot_path)
                logger.info(f"📸 页面截图：{screenshot_path}")
            except:
                pass
            
            # 提示用户确认
            logger.info("=" * 60)
            logger.info("⏸️  请确认当前页面：")
            logger.info("   ✓ 能看到搜索结果列表吗？")
            logger.info("   ✓ 页面加载正常吗？")
            logger.info("")
            logger.info("   如果页面正常 → 按回车开始爬取")
            logger.info("   如果页面异常 → 按 Ctrl+C 退出")
            logger.info("=" * 60)
            
            # 等待用户确认
            try:
                input("\n按回车键开始爬取...")
                logger.success("✅ 用户确认完成，开始爬取数据")
            except KeyboardInterrupt:
                logger.warning("⚠️ 用户取消")
                return False
            except:
                pass
            
            random_sleep(2, 3)
            return True
                
        except Exception as e:
            logger.error(f"❌ 打开裁判文书网出错：{str(e)}")
            return False
    
    def search_cases(self):
        """
        搜索案件（用户已手动完成搜索）
        
        返回：
            是否搜索成功
        """
        try:
            logger.info("=" * 60)
            logger.info("🔍 搜索阶段")
            logger.info("=" * 60)
            logger.info("📌 您应该已经手动完成了搜索操作")
            logger.info("📌 程序将直接读取当前页面的搜索结果")
            logger.info("")
            
            # 检查当前页面是否有搜索结果
            time.sleep(2)
            
            # 保存当前页面截图
            screenshot_path = f"data/debug_search_result_{get_timestamp()}.png"
            try:
                self.browser.save_screenshot(screenshot_path)
                logger.info(f"📸 搜索结果页截图：{screenshot_path}")
            except:
                pass
            

            # 检查是否有搜索结果（检测案件列表容器）
            try:
                test_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.LM_list")
                if test_elements and len(test_elements) > 0:
                    logger.success(f"✅ 检测到 {len(test_elements)} 个案件")
                    return True
                else:
                    logger.warning("⚠️ 未检测到案件列表，但继续尝试...")
                    return True
            except:
                logger.warning("⚠️ 无法确认搜索结果，但继续尝试...")
                return True
                
        except Exception as e:
            logger.error(f"❌ 搜索检查出错：{str(e)}")
            return True  # 即使出错也继续，让后续步骤去处理
    
    def _try_search_by_input(self):
        """通过输入框搜索"""
        try:
            # 查找搜索框（可能的选择器）
            search_selectors = [
                (By.ID, "keyword"),
                (By.NAME, "keyword"),
                (By.CSS_SELECTOR, "input[placeholder*='关键词']"),
                (By.CSS_SELECTOR, "input[placeholder*='案由']"),
                (By.CSS_SELECTOR, ".search-input"),
                (By.XPATH, "//input[@type='text']"),
            ]
            
            search_box = None
            for by, selector in search_selectors:
                try:
                    search_box = self.browser.find_element(by, selector, timeout=5)
                    if search_box:
                        logger.info(f"找到搜索框：{by}={selector}")
                        break
                except:
                    continue
            
            if not search_box:
                logger.warning("⚠️ 未找到搜索框")
                return False
            
            # 清空并输入关键词（模拟人类输入）
            search_box.clear()
            time.sleep(0.5)
            
            for char in KEYWORD:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            logger.info(f"已输入关键词：{KEYWORD}")
            time.sleep(1)
            
            # 查找搜索按钮
            search_button = None
            button_selectors = [
                (By.ID, "search"),
                (By.ID, "searchBtn"),
                (By.CSS_SELECTOR, ".search-btn"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), '搜索')]"),
                (By.XPATH, "//button[contains(text(), '查询')]"),
            ]
            
            for by, selector in button_selectors:
                try:
                    search_button = self.browser.find_element(by, selector, timeout=3)
                    if search_button:
                        logger.info(f"找到搜索按钮：{by}={selector}")
                        break
                except:
                    continue
            
            if search_button:
                # 点击搜索按钮
                search_button.click()
                logger.info("已点击搜索按钮")
                return True
            else:
                # 尝试按回车键搜索
                logger.info("未找到搜索按钮，尝试按回车键")
                search_box.send_keys(Keys.RETURN)
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ 输入框搜索失败：{str(e)}")
            return False
    
    def _try_search_by_url(self):
        """通过URL参数直接搜索"""
        try:
            # 构造搜索URL
            search_url = f"{WENSHU_LIST_URL}?keyword={KEYWORD}"
            
            logger.info(f"使用URL搜索：{search_url}")
            return self.browser.get(search_url)
            
        except Exception as e:
            logger.warning(f"⚠️ URL搜索失败：{str(e)}")
            return False
    
    def get_case_list(self, max_page=50):
        """
        获取案件列表
        
        参数：
            max_page: 最多爬取多少页
        
        返回：
            案件列表
        """
        try:
            logger.info(f"📋 开始获取案件列表（最多{max_page}页）...")
            
            all_cases = []
            current_page = 1
            
            while current_page <= max_page:
                logger.info(f"📄 正在获取第 {current_page} 页...")
                
                # 等待列表加载
                random_sleep(3, 5)
                
                # 获取当前页的案件
                cases = self._parse_current_page()
                
                if not cases:
                    logger.warning(f"⚠️ 第 {current_page} 页没有找到案件，可能已到最后一页")
                    break
                
                logger.success(f"✅ 第 {current_page} 页获取到 {len(cases)} 条案件")
                all_cases.extend(cases)
                
                logger.info(f"📊 当前总计：{len(all_cases)} 条案件")
                
                # 检查是否达到目标数量
                from config import TARGET_COUNT
                if len(all_cases) >= TARGET_COUNT:
                    logger.success(f"🎉 已达到目标数量 {TARGET_COUNT} 条！")
                    break
                
                # 尝试翻页
                if not self._go_to_next_page():
                    logger.warning("⚠️ 无法翻页，停止获取")
                    break
                
                current_page += 1
                random_sleep(2, 4)
            
            logger.success(f"✅ 案件列表获取完成，共 {len(all_cases)} 条")
            self.results = all_cases
            return all_cases
            
        except Exception as e:
            logger.error(f"❌ 获取案件列表出错：{str(e)}")
            return []
    
    def _parse_current_page(self):
        """解析当前页的案件列表"""
        try:
            cases = []
            
            # 等待JavaScript渲染案件标题链接
            logger.info("⏳ 等待案件标题加载...")
            
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # 等待至少一个 a.caseName 出现（最多15秒）
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.caseName"))
                )
                logger.success("✅ 案件标题已加载")
                time.sleep(2)  # 额外等待2秒确保稳定
            except Exception as e:
                logger.error(f"❌ 案件标题加载失败：{str(e)}")
                logger.info("💡 请确认页面已完全加载，能看到案件列表")
                return []
            
            # 获取案件列表：每个案件在一个 <div class="LM_list"> 中
            # 每页通常有5个案件
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, "div.LM_list")
                logger.info(f"✅ 找到 {len(elements)} 个案件")
            except Exception as e:
                logger.error(f"❌ 未找到案件列表：{str(e)}")
                elements = []
            
            if not elements or len(elements) == 0:
                logger.warning("⚠️ 当前页没有案件")
                
                # 保存截图用于调试
                screenshot_path = f"data/debug_page_{get_timestamp()}.png"
                self.browser.save_screenshot(screenshot_path)
                
                # 保存页面源代码用于调试
                html_path = f"data/debug_page_{get_timestamp()}.html"
                try:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    logger.info(f"📄 已保存页面HTML：{html_path}")
                except:
                    pass
                
                return cases
            
            # 解析每个案件
            for idx, elem in enumerate(elements):
                try:
                    case_info = self._parse_case_element(elem, idx)
                    if case_info:
                        cases.append(case_info)
                except Exception as e:
                    logger.warning(f"⚠️ 解析第 {idx+1} 个案件失败：{str(e)}")
                    continue
            
            return cases
            
        except Exception as e:
            logger.error(f"❌ 解析页面失败：{str(e)}")
            return []
    
    def _parse_case_element(self, element, index):
        """
        解析单个案件元素
        
        HTML结构：
        <div class="LM_list">
          <div class="list_title"><h4><a class="caseName" href="...">案件标题</a></h4></div>
          <div class="list_subtitle">
            <span class="slfyName">法院</span>
            <span class="ah">案号</span>
            <span class="cprq">日期</span>
          </div>
        </div>
        """
        try:
            # 提取案件信息
            case_info = {
                "index": index + 1,
                "title": "",
                "link": "",
                "case_no": "",  # 案号
                "court": "",    # 法院
                "date": "",     # 日期
                "case_type": "",  # 案件类型
                "element": element,  # 保存元素引用，用于后续点击
                "list_index": index,  # 在列表中的索引
            }
            
            # 获取标题和链接 - 使用正确的选择器 a.caseName
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "a.caseName")
                case_info["title"] = title_elem.text.strip()
                
                # 获取href属性
                link = title_elem.get_attribute("href") or ""
                
                # 如果是相对路径，转换为绝对路径
                if link and not link.startswith("http"):
                    from config import WENSHU_BASE_URL
                    # 处理 ../181107ANFZ0BXSK4/index.html 这种路径
                    if link.startswith("../"):
                        link = f"{WENSHU_BASE_URL}/website/wenshu/{link[3:]}"
                    elif link.startswith("/"):
                        link = f"{WENSHU_BASE_URL}{link}"
                
                case_info["link"] = link
                
                logger.debug(f"案件 #{index+1}: {case_info['title'][:30] if case_info['title'] else ''}... | 链接: {link[:50] if link else 'None'}...")
                
            except Exception as e:
                logger.debug(f"提取标题和链接失败：{str(e)}")
            
            # 提取法院名称 - span.slfyName
            try:
                court_elem = element.find_element(By.CSS_SELECTOR, "span.slfyName")
                case_info["court"] = court_elem.text.strip()
            except:
                pass
            
            # 提取案号 - span.ah
            try:
                case_no_elem = element.find_element(By.CSS_SELECTOR, "span.ah")
                case_info["case_no"] = case_no_elem.text.strip()
            except:
                pass
            
            # 提取日期 - span.cprq
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, "span.cprq")
                case_info["date"] = date_elem.text.strip()
            except:
                pass
            
            # 如果所有信息都为空，至少标记为有效元素
            if not case_info["title"]:
                case_info["title"] = f"案件{index + 1}"
            
            logger.debug(f"解析案件 #{case_info['index']}: {case_info['title'][:30]}...")
            
            return case_info
            
        except Exception as e:
            logger.warning(f"⚠️ 解析案件元素失败：{str(e)}")
            return None
    
    def _go_to_next_page(self):
        """翻到下一页"""
        try:
            # 可能的下一页按钮选择器
            next_selectors = [
                (By.LINK_TEXT, "下一页"),
                (By.PARTIAL_LINK_TEXT, "下一页"),
                (By.CSS_SELECTOR, ".next-page"),
                (By.CSS_SELECTOR, "a[title='下一页']"),
                (By.XPATH, "//a[contains(text(), '下一页')]"),
                (By.XPATH, "//button[contains(text(), '下一页')]"),
            ]
            
            for by, selector in next_selectors:
                try:
                    next_button = self.browser.wait_for_element_clickable(by, selector, timeout=5)
                    if next_button:
                        logger.info("找到下一页按钮，正在点击...")
                        
                        # 滚动到按钮位置
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        
                        # 点击
                        next_button.click()
                        logger.success("✅ 已翻页")
                        return True
                except:
                    continue
            
            logger.warning("⚠️ 未找到下一页按钮")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ 翻页失败：{str(e)}")
            return False

