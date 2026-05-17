# -*- coding: utf-8 -*-
"""
辅助工具模块 - 各种实用小功能
"""

import time
import random
import json
import hashlib
from datetime import datetime
from config import DELAY_MIN, DELAY_MAX
from utils.logger import logger

def random_sleep(min_sec=DELAY_MIN, max_sec=DELAY_MAX):
    """
    随机延迟（模拟人类操作）
    
    参数：
        min_sec: 最小延迟秒数
        max_sec: 最大延迟秒数
    """
    sleep_time = random.uniform(min_sec, max_sec)
    logger.debug(f"⏱️ 延迟 {sleep_time:.2f} 秒")
    time.sleep(sleep_time)


def get_current_time_str(format="%Y-%m-%d %H:%M:%S"):
    """获取当前时间字符串"""
    return datetime.now().strftime(format)


def get_timestamp():
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def save_json(data, filepath):
    """
    保存数据为JSON文件
    
    参数：
        data: 要保存的数据
        filepath: 文件路径
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"💾 JSON已保存：{filepath}")
        return True
    except Exception as e:
        logger.error(f"❌ 保存JSON失败：{str(e)}")
        return False


def load_json(filepath):
    """
    从JSON文件加载数据
    
    参数：
        filepath: 文件路径
    
    返回：
        加载的数据，失败返回None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"📂 JSON已加载：{filepath}")
        return data
    except FileNotFoundError:
        logger.warning(f"⚠️ 文件不存在：{filepath}")
        return None
    except Exception as e:
        logger.error(f"❌ 加载JSON失败：{str(e)}")
        return None


def calculate_md5(text):
    """
    计算字符串的MD5值
    
    参数：
        text: 输入字符串
    
    返回：
        MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def clean_text(text):
    """
    清理文本（去除多余空白、换行等）
    
    参数：
        text: 原始文本
    
    返回：
        清理后的文本
    """
    if not text:
        return ""
    
    # 替换多个空白字符为单个空格
    text = ' '.join(text.split())
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def extract_number(text, default=0):
    """
    从文本中提取数字
    
    参数：
        text: 包含数字的文本
        default: 提取失败时的默认值
    
    返回：
        提取的数字（浮点数）
    """
    import re
    
    if not text:
        return default
    
    # 查找所有数字（包括小数）
    numbers = re.findall(r'\d+\.?\d*', str(text))
    
    if numbers:
        try:
            return float(numbers[0])
        except:
            return default
    
    return default


def chunk_list(lst, chunk_size):
    """
    将列表分块
    
    参数：
        lst: 原列表
        chunk_size: 每块大小
    
    返回：
        分块后的列表（生成器）
    
    使用示例：
        for chunk in chunk_list([1,2,3,4,5], 2):
            print(chunk)  # [1,2], [3,4], [5]
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def retry_on_failure(func, max_retry=3, delay=2, *args, **kwargs):
    """
    失败重试装饰器函数
    
    参数：
        func: 要执行的函数
        max_retry: 最大重试次数
        delay: 重试延迟（秒）
        *args, **kwargs: 函数参数
    
    返回：
        函数执行结果
    """
    for i in range(max_retry):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"⚠️ 执行失败（第{i+1}次）：{str(e)}")
            if i < max_retry - 1:
                time.sleep(delay)
                continue
            else:
                logger.error(f"❌ 已重试{max_retry}次，仍然失败")
                raise

