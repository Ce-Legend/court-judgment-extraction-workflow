# -*- coding: utf-8 -*-
"""
Public demo configuration for the judgment extraction workflow.

Copy this file or override values in local scripts when running against a
browser you control. The repository does not include local browser state,
runtime logs, or collected judgment data.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
LOG_DIR = str(PROJECT_ROOT / "logs")
CHECKPOINT_DIR = str(DATA_DIR / "checkpoints")

WENSHU_BASE_URL = "https://wenshu.court.gov.cn"
WENSHU_LIST_URL = f"{WENSHU_BASE_URL}/website/wenshu/181107ANFZ0BXSK4/index.html"

KEYWORD = "故意伤害"
START_YEAR = 2020
END_YEAR = 2025
TARGET_COUNT = 500

DELAY_MIN = 2
DELAY_MAX = 5
PAGE_LOAD_TIMEOUT = 45
CHECKPOINT_INTERVAL = 20
SAVE_RAW_HTML = False
HEADLESS = False
LOG_LEVEL = "INFO"

CHROME_OPTIONS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-sandbox",
]

for path in [DATA_DIR, RAW_DATA_DIR, Path(LOG_DIR), Path(CHECKPOINT_DIR)]:
    path.mkdir(parents=True, exist_ok=True)
