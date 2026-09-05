from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any, Iterable

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# (內部歸一化 format 候選值, 報表展示行名)：候選值涵蓋簡/繁等寫法變體，全部併入該錨定行；
# 錨定行永遠顯示、順序固定。錨定之外的形式由 build_report_table 動態成行。
# 註：「專題」族（專題報道/專題/專題報告/專題文章…）刻意不做錨定行——按用戶要求保持細分，
# 各原始寫法自動成行、行名即原始形式名。
REPORT_CATEGORY_ROWS: list[tuple[tuple[str, ...], str]] = [
    (("新聞報道",), "新聞報道"),
    (("評論/博客文章（中）",), "評論/博文（中）"),
    (("評論/博客文章（連視頻）（中）",), "評論/博文（中）連視頻"),
    (("評論/博客文章（英）",), "評論/博文（英）"),
    (("評論/博客文章（連視頻）（英）",), "評論/博文（英）連視頻"),
    (("影片",), "影片"),
    (("帖文", "貼文"), "貼文"),
]

# 形式為空（或 NaN）的行歸入此動態行
UNLABELED_FORMAT_LABEL = "未標註形式"

# 內部列名（唯一）；匯出 Word 表頭用 DISPLAY_COLUMNS
REPORT_COLUMNS = ["分類", "數目", "瀏覽量", "平均瀏覽量", "互動量", "平均互動量"]
DISPLAY_COLUMNS = ["分類", "數目", "瀏覽量", "平均", "互動量", "平均"]
TOTAL_LABEL = "總數"


def _safe_avg(total: float, count: int) -> float:
    if count <= 0:
        return 0.0
    return round(float(total) / count, 1)


def format_report_number(value: Any) -> str:
    """數值顯示：千分位逗號；空值保持空白。"""
    if value is None:
        return ""
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return ""
        try:
            if "." in text:
                return f"{float(text):,.1f}"
            return f"{int(text):,}"
        except ValueError:
            return text
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return f"{value:,.1f}"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


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
    """構建報表：錨定分類行（固定順序、永遠顯示）+ 動態行（數據中出現的新形式自動成行）+ 總數。"""
    working = df.copy() if df is not None else pd.DataFrame()
    if "format" not in working.columns:
        working["format"] = ""

    rows: list[dict] = []
    matched_formats: list[str] = []
    for internal_formats, label in REPORT_CATEGORY_ROWS:
        subset = working[working["format"].isin(internal_formats)]
        metrics = _row_metrics(subset)
        rows.append({"分類": label, **metrics})
        matched_formats.extend(internal_formats)

    # 動態行：錨定分類之外的形式各自成行（按瀏覽量降序）；形式為空歸入「未標註形式」
    remaining = working[~working["format"].isin(matched_formats)]
    dynamic_rows: list[tuple[str, dict]] = []
    for fmt, subset in remaining.groupby("format", dropna=False):
        text = str(fmt).strip()
        label = text if text else UNLABELED_FORMAT_LABEL
        dynamic_rows.append((label, _row_metrics(subset)))
    dynamic_rows.sort(key=lambda item: item[1]["瀏覽量"], reverse=True)
    for label, metrics in dynamic_rows:
        rows.append({"分類": label, **metrics})

    # 總數 = 全部數據：錨定行 + 動態行完整覆蓋，保證分項加總一致
    total_metrics = _row_metrics(working)
    # 總數行的「平均互動量」不統計（數據稀疏時意義不大）
    total_metrics["平均互動量"] = ""
    rows.append({"分類": TOTAL_LABEL, **total_metrics})

    return pd.DataFrame(rows, columns=REPORT_COLUMNS)


def _set_run_font(run, font_name: str = "Microsoft YaHei", font_size: int = 11) -> None:
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(font_size)


def _set_cell_no_wrap(cell) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    # 移除舊的 noWrap 節點，避免重複
    for child in list(tc_pr):
        if child.tag == qn("w:noWrap"):
            tc_pr.remove(child)
    tc_pr.append(OxmlElement("w:noWrap"))


def _apply_table_grid(table, widths_cm: list[float]) -> None:
    """
    將列寬寫入表格層級的 tblGrid/tblW（1cm = 567 twips）。
    僅設置單元格 tcW 時 Word 固定布局仍按建表時均分的 tblGrid 渲染（表現為等寬），
    必須同時重寫網格列寬才能生效。
    """
    tbl = table._tbl
    tbl_pr = tbl.tblPr

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(int(round(sum(widths_cm) * 567))))

    for old_grid in tbl.findall(qn("w:tblGrid")):
        tbl.remove(old_grid)
    grid = OxmlElement("w:tblGrid")
    for width_cm in widths_cm:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(round(width_cm * 567))))
        grid.append(col)
    # tblGrid 必須緊跟 tblPr 之後（schema 順序）
    tbl_pr.addnext(grid)


def _estimate_text_width_cm(text: str) -> float:
    """依內容估算列寬：中文較寬、數字/符號較窄，並加邊距。"""
    width = 0.0
    for ch in str(text):
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF or ch in "（）/":
            width += 0.42
        else:
            width += 0.28
    return width + 0.55


def _row_display_values(row: pd.Series) -> list[str]:
    return [
        str(row["分類"]),
        format_report_number(row["數目"]),
        format_report_number(row["瀏覽量"]),
        format_report_number(row["平均瀏覽量"]),
        format_report_number(row["互動量"]),
        format_report_number(row["平均互動量"]),
    ]


def _compute_column_widths_cm(report_df: pd.DataFrame) -> list[float]:
    """按每列最長內容自由調整列寬，保證單行完整顯示。"""
    max_widths = [_estimate_text_width_cm(col) for col in DISPLAY_COLUMNS]
    for _, row in report_df.iterrows():
        values = _row_display_values(row)
        for idx, value in enumerate(values):
            max_widths[idx] = max(max_widths[idx], _estimate_text_width_cm(value))

    # 分類列保底略寬；數字列也給最小寬度避免過窄
    mins = [4.2, 1.8, 2.4, 2.2, 2.4, 2.2]
    return [max(mins[i], max_widths[i]) for i in range(len(DISPLAY_COLUMNS))]


def _apply_row_widths(cells, widths_cm: list[float]) -> None:
    for idx, width_cm in enumerate(widths_cm):
        cells[idx].width = Cm(width_cm)


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
    table.autofit = False
    table.allow_autofit = False

    widths_cm = _compute_column_widths_cm(report_df)
    _apply_table_grid(table, widths_cm)
    _apply_row_widths(table.rows[0].cells, widths_cm)

    header_cells = table.rows[0].cells
    for idx, col_name in enumerate(DISPLAY_COLUMNS):
        header_cells[idx].text = col_name
        _set_cell_no_wrap(header_cells[idx])
        for paragraph in header_cells[idx].paragraphs:
            # 數字列表頭靠右；分類列靠左
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            for run in paragraph.runs:
                _set_run_font(run, font_size=11)
                run.bold = True

    for _, row in report_df.iterrows():
        cells = table.add_row().cells
        _apply_row_widths(cells, widths_cm)
        values: Iterable = _row_display_values(row)
        for idx, value in enumerate(values):
            cells[idx].text = str(value)
            _set_cell_no_wrap(cells[idx])
            for paragraph in cells[idx].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
                for run in paragraph.runs:
                    _set_run_font(run, font_size=11)
                    if str(row["分類"]) == TOTAL_LABEL:
                        run.bold = True

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def default_report_filename() -> str:
    return f"內容統計報告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
