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


def check_anchor_only_regression() -> None:
    """錨定分類內的形式版式不變；專題族走動態行（行名=原始形式）。"""
    df = pd.DataFrame(
        [
            {"format": "評論/博客文章（中）", "views": 100, "interactions": 10},
            {"format": "評論/博客文章（中）", "views": 50, "interactions": 5},
            {"format": "評論/博客文章（連視頻）（中）", "views": 200, "interactions": 20},
            {"format": "評論/博客文章（英）", "views": 80, "interactions": 8},
            {"format": "專題報道", "views": 300, "interactions": 30},
            {"format": "影片", "views": 400, "interactions": 40},
            {"format": "帖文", "views": 20, "interactions": 2},
            {"format": "新聞報道", "views": 999, "interactions": 99},
        ]
    )

    report = build_report_table(df)
    assert list(report["分類"]) == [
        "新聞報道",
        "評論/博文（中）",
        "評論/博文（中）連視頻",
        "評論/博文（英）",
        "評論/博文（英）連視頻",
        "影片",
        "貼文",
        "專題報道",  # 動態行：專題族不再有錨定行，行名=原始寫法
        "總數",
    ]

    topic_report = report.loc[report["分類"] == "專題報道"].iloc[0]
    assert int(topic_report["數目"]) == 1
    assert int(topic_report["瀏覽量"]) == 300

    news = report.loc[report["分類"] == "新聞報道"].iloc[0]
    assert int(news["數目"]) == 1
    assert int(news["瀏覽量"]) == 999

    zh = report.loc[report["分類"] == "評論/博文（中）"].iloc[0]
    assert int(zh["數目"]) == 2
    assert int(zh["瀏覽量"]) == 150
    assert float(zh["平均瀏覽量"]) == 75.0

    total = report.loc[report["分類"] == "總數"].iloc[0]
    assert int(total["數目"]) == 8
    assert int(total["瀏覽量"]) == 2149
    assert total["平均互動量"] == ""  # 總數行不統計平均互動量


def check_dynamic_categories() -> None:
    """錨定之外的形式（含專題族）自動成行；繁簡寫法併入錨定行；總數=全量。"""
    df = pd.DataFrame(
        [
            {"format": "專題報道", "views": 100, "interactions": 10},
            {"format": "專題報告", "views": 300, "interactions": 30},
            {"format": "專題文章", "views": 50, "interactions": 5},
            {"format": "直播", "views": 200, "interactions": 20},
            {"format": "貼文", "views": 40, "interactions": 4},  # 繁體寫法，應併入錨定「貼文」行
            {"format": "帖文", "views": 60, "interactions": 6},
            {"format": "", "views": 7, "interactions": 1},  # 形式為空 -> 未標註形式
        ]
    )

    report = build_report_table(df)
    assert list(report["分類"]) == [
        "新聞報道",
        "評論/博文（中）",
        "評論/博文（中）連視頻",
        "評論/博文（英）",
        "評論/博文（英）連視頻",
        "影片",
        "貼文",
        "專題報告",  # 動態行按瀏覽量降序；專題族各自獨立成行
        "直播",
        "專題報道",
        "專題文章",
        "未標註形式",
        "總數",
    ]

    topic_coverage = report.loc[report["分類"] == "專題報道"].iloc[0]
    assert int(topic_coverage["數目"]) == 1
    assert int(topic_coverage["瀏覽量"]) == 100

    post = report.loc[report["分類"] == "貼文"].iloc[0]
    assert int(post["數目"]) == 2  # 帖文 + 貼文 併入同一行
    assert int(post["瀏覽量"]) == 100

    report_zh = report.loc[report["分類"] == "專題報告"].iloc[0]
    assert int(report_zh["數目"]) == 1
    assert int(report_zh["瀏覽量"]) == 300

    unlabeled = report.loc[report["分類"] == "未標註形式"].iloc[0]
    assert int(unlabeled["數目"]) == 1

    total = report.loc[report["分類"] == "總數"].iloc[0]
    assert int(total["數目"]) == 7  # 全量（不再只統計白名單）
    assert int(total["瀏覽量"]) == 757

    # 分項加總 = 總數
    parts = report[report["分類"] != "總數"]
    assert int(parts["數目"].sum()) == 7
    assert int(parts["瀏覽量"].sum()) == 757

    docx_bytes = build_report_docx(report)
    assert docx_bytes[:2] == b"PK"


def main() -> None:
    check_anchor_only_regression()
    check_dynamic_categories()

    assert format_report_number(8818979) == "8,818,979"
    assert format_report_number(12344.8) == "12,344.8"
    assert format_report_number("") == ""

    report = build_report_table(
        pd.DataFrame([{"format": "評論/博客文章（中）", "views": 100, "interactions": 10}])
    )
    docx_bytes = build_report_docx(report)
    assert docx_bytes[:2] == b"PK"  # docx 是 zip 容器
    assert len(docx_bytes) > 1000

    print("[OK] 報表匯出冒煙通過")


if __name__ == "__main__":
    main()
