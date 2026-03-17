from __future__ import annotations

from pathlib import Path

# 报表固定列（第 4 行）
RAW_COLUMNS = ["日期", "平台", "標題", "形式", "連結", "瀏覽量", "互動量"]

# 内部标准字段
STANDARD_COLUMNS = [
    "date",
    "platform",
    "title",
    "format",
    "link",
    "views",
    "interactions",
]

COLUMN_ALIASES = {
    "日期": "date",
    "平台": "platform",
    "標題": "title",
    "标题": "title",
    "形式": "format",
    "連結": "link",
    "链接": "link",
    "瀏覽量": "views",
    "浏览量": "views",
    "互動量": "interactions",
    "互动量": "interactions",
}

PRESET_FILE_PATH = Path(".streamlit") / "filter_presets.json"

