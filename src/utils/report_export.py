from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Iterable

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

# (內部歸一化 format, 報表展示行名)
REPORT_CATEGORY_ROWS: list[tuple[str, str]] = [
    ("新聞報道", "新聞報道"),
    ("評論/博客文章（中）", "評論/博文（中）"),
    ("評論/博客文章（連視頻）（中）", "評論/博文（中）連視頻"),
    ("評論/博客文章（英）", "評論/博文（英）"),
    ("評論/博客文章（連視頻）（英）", "評論/博文（英）連視頻"),
    ("專題報道", "專題"),
    ("影片", "影片"),
    ("帖文", "貼文"),
]

# 內部列名（唯一）；匯出 Word 表頭用 DISPLAY_COLUMNS
REPORT_COLUMNS = ["分類", "數目", "瀏覽量", "平均瀏覽量", "互動量", "平均互動量"]
DISPLAY_COLUMNS = ["分類", "數目", "瀏覽量", "平均", "互動量", "平均"]
TOTAL_LABEL = "總數"


def _safe_avg(total: float, count: int) -> float:
    if count <= 0:
        return 0.0
    return round(float(total) / count, 1)


def _row_metrics(subset: pd.DataFrame) -> dict[str, float | int]:
    count = int(len(subset))
    views = float(subset["views"].sum()) if count and "views" in subset.columns else 0.0
    interactions = (
        float(subset["interactions"].sum()) if count and "interactions" in subset.columns else 0.0
    )
    return {
        "數目": count,
        "瀏覽量": int(round(views)),
        "平均瀏覽量": _safe_avg(views, count),
        "互動量": int(round(interactions)),
        "平均互動量": _safe_avg(interactions, count),
    }


def build_report_table(df: pd.DataFrame) -> pd.DataFrame:
    """按固定分類行構建報表預覽表（基於全部上傳數據）。"""
    working = df.copy() if df is not None else pd.DataFrame()
    if "format" not in working.columns:
        working["format"] = ""

    rows: list[dict] = []
    matched_formats: list[str] = []
    for internal_format, label in REPORT_CATEGORY_ROWS:
        subset = working[working["format"] == internal_format]
        metrics = _row_metrics(subset)
        rows.append({"分類": label, **metrics})
        matched_formats.append(internal_format)

    # 總數：僅統計報表列出的分類，保證分項加總一致
    total_subset = working[working["format"].isin(matched_formats)]
    total_metrics = _row_metrics(total_subset)
    # 總數行的「平均互動量」不統計（數據稀疏時意義不大）
    total_metrics["平均互動量"] = ""
    rows.append({"分類": TOTAL_LABEL, **total_metrics})

    return pd.DataFrame(rows, columns=REPORT_COLUMNS)


def _set_run_font(run, font_name: str = "Microsoft YaHei", font_size: int = 11) -> None:
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(font_size)


def build_report_docx(
    report_df: pd.DataFrame,
    *,
    title: str = "內容統計報告",
    subtitle: str | None = None,
) -> bytes:
    """將報表 DataFrame 寫成 .docx 二進位內容。"""
    doc = Document()

    heading = doc.add_heading(title, level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in heading.runs:
        _set_run_font(run, font_size=16)

    meta = subtitle or f"匯出時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    meta_p = doc.add_paragraph(meta)
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in meta_p.runs:
        _set_run_font(run, font_size=10)

    table = doc.add_table(rows=1, cols=len(DISPLAY_COLUMNS))
    table.style = "Table Grid"

    header_cells = table.rows[0].cells
    for idx, col_name in enumerate(DISPLAY_COLUMNS):
        header_cells[idx].text = col_name
        for paragraph in header_cells[idx].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                _set_run_font(run, font_size=11)
                run.bold = True

    for _, row in report_df.iterrows():
        cells = table.add_row().cells
        values: Iterable = [
            row["分類"],
            row["數目"],
            row["瀏覽量"],
            row["平均瀏覽量"],
            row["互動量"],
            row["平均互動量"],
        ]
        for idx, value in enumerate(values):
            cells[idx].text = str(value)
            for paragraph in cells[idx].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    _set_run_font(run, font_size=11)
                    if str(row["分類"]) == TOTAL_LABEL:
                        run.bold = True

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def default_report_filename() -> str:
    return f"內容統計報告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
