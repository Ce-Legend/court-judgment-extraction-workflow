# -*- coding: utf-8 -*-
"""
日志模块 - 记录程序运行情况
新手提示：这个模块负责输出彩色日志，方便查看程序运行状态
"""

import sys
import logging
from config import LOG_DIR, LOG_LEVEL
import os

try:
    from loguru import logger

    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True,
    )

    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "scraper_{time:YYYY-MM-DD}.log")
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="00:00",
        retention="7 days",
        encoding="utf-8",
    )
except ImportError:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
    )
    logger = logging.getLogger("judgment_workflow")
    logger.success = logger.info

def log_info(message):
    """记录信息日志"""
    logger.info(message)

def log_success(message):
    """记录成功日志"""
    logger.success(message)

def log_warning(message):
    """记录警告日志"""
    logger.warning(message)

def log_error(message):
    """记录错误日志"""
    logger.error(message)

def log_debug(message):
    """记录调试日志"""
    logger.debug(message)

# 导出logger供其他模块使用
__all__ = ["logger", "log_info", "log_success", "log_warning", "log_error", "log_debug"]

