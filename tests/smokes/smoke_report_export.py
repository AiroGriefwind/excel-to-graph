from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.report_export import (  # noqa: E402
    build_report_docx,
    build_report_table,
    format_report_number,
)


def main() -> None:
    df = pd.DataFrame(
        [
            {"format": "評論/博客文章（中）", "views": 100, "interactions": 10},
            {"format": "評論/博客文章（中）", "views": 50, "interactions": 5},
            {"format": "評論/博客文章（連視頻）（中）", "views": 200, "interactions": 20},
            {"format": "評論/博客文章（英）", "views": 80, "interactions": 8},
            {"format": "專題報道", "views": 300, "interactions": 30},
            {"format": "影片", "views": 400, "interactions": 40},
            {"format": "帖文", "views": 20, "interactions": 2},
            {"format": "新聞報道", "views": 999, "interactions": 99},  # 不應計入報表總數
        ]
    )

    report = build_report_table(df)
    assert list(report["分類"]) == [
        "新聞報道",
        "評論/博文（中）",
        "評論/博文（中）連視頻",
        "評論/博文（英）",
        "評論/博文（英）連視頻",
        "專題",
        "影片",
        "貼文",
        "總數",
    ]

    news = report.loc[report["分類"] == "新聞報道"].iloc[0]
    assert int(news["數目"]) == 1
    assert int(news["瀏覽量"]) == 999

    zh = report.loc[report["分類"] == "評論/博文（中）"].iloc[0]
    assert int(zh["數目"]) == 2
    assert int(zh["瀏覽量"]) == 150
    assert float(zh["平均瀏覽量"]) == 75.0

    total = report.loc[report["分類"] == "總數"].iloc[0]
    assert int(total["數目"]) == 8  # 含新聞報道
    assert int(total["瀏覽量"]) == 2149
    assert total["平均互動量"] == ""  # 總數行不統計平均互動量

    assert format_report_number(8818979) == "8,818,979"
    assert format_report_number(12344.8) == "12,344.8"
    assert format_report_number("") == ""

    docx_bytes = build_report_docx(report)
    assert docx_bytes[:2] == b"PK"  # docx 是 zip 容器
    assert len(docx_bytes) > 1000

    print("[OK] 報表匯出冒煙通過")


if __name__ == "__main__":
    main()
