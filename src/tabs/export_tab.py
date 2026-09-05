from __future__ import annotations

import html
from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from src.utils.bastille_report import (
    BASTILLE_COLUMNS,
    build_bastille_docx,
    build_bastille_table,
    default_bastille_filename,
)
from src.utils.report_export import (
    DISPLAY_COLUMNS,
    REPORT_CATEGORY_ROWS,
    TOTAL_LABEL,
    build_report_docx,
    build_report_table,
    default_report_filename,
    format_report_number,
)


def _format_date_ymd(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, pd.Timestamp):
        return value.strftime("%Y/%m/%d")
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y/%m/%d")


def _date_range_subtitle(filters: dict[str, Any] | None, fallback_df: pd.DataFrame) -> str:
    """副標題統一為篩選條件中的開始日期 - 結束日期（YYYY/MM/DD）。"""
    filters = filters or {}
    start = _format_date_ymd(filters.get("date_start"))
    end = _format_date_ymd(filters.get("date_end"))

    if (start is None or end is None) and fallback_df is not None and not fallback_df.empty:
        if "date" in fallback_df.columns:
            series = pd.to_datetime(fallback_df["date"], errors="coerce").dropna()
            if not series.empty:
                if start is None:
                    start = series.min().strftime("%Y/%m/%d")
                if end is None:
                    end = series.max().strftime("%Y/%m/%d")

    if start and end:
        return f"{start} - {end}"
    if start:
        return start
    if end:
        return end
    return ""


def _render_preview_html(report_df: pd.DataFrame) -> None:
    """用 HTML 表预览，避免 Streamlit dataframe 不支持重复列名「平均」。"""
    headers = "".join(f"<th>{html.escape(col)}</th>" for col in DISPLAY_COLUMNS)
    body_rows: list[str] = []
    for _, row in report_df.iterrows():
        values = [
            row["分類"],
            format_report_number(row["數目"]),
            format_report_number(row["瀏覽量"]),
            format_report_number(row["平均瀏覽量"]),
            format_report_number(row["互動量"]),
            format_report_number(row["平均互動量"]),
        ]
        is_total = str(row["分類"]) == TOTAL_LABEL
        cells = "".join(
            f"<td{' style=\"font-weight:700\"' if is_total else ''}>{html.escape(str(v))}</td>"
            for v in values
        )
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = f"""
    <style>
      .report-preview-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 0.4rem 0 0.8rem 0;
        table-layout: auto;
      }}
      .report-preview-table th, .report-preview-table td {{
        border: 1px solid rgba(120,120,120,0.35);
        padding: 0.45rem 0.6rem;
        text-align: right;
        white-space: nowrap;
      }}
      .report-preview-table th {{
        background: rgba(120,120,120,0.12);
        font-weight: 600;
      }}
      .report-preview-table td:first-child,
      .report-preview-table th:first-child {{
        text-align: left;
        white-space: nowrap;
      }}
    </style>
    <table class="report-preview-table">
      <thead><tr>{headers}</tr></thead>
      <tbody>{''.join(body_rows)}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def _render_bastille_preview_html(table_df: pd.DataFrame) -> None:
    """博文表預覽：標題/欄目列允許換行，其餘列單行顯示。"""
    headers = "".join(f"<th>{html.escape(col)}</th>" for col in BASTILLE_COLUMNS)
    body_rows: list[str] = []
    for _, row in table_df.iterrows():
        values = [
            str(row["數目"]),
            str(row["日期"]),
            str(row["欄目"]),
            str(row["標題"]),
            format_report_number(row["瀏覽量"]),
        ]
        cells = "".join(f"<td>{html.escape(v)}</td>" for v in values)
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = f"""
    <style>
      .bastille-preview-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 0.4rem 0 0.8rem 0;
        table-layout: auto;
      }}
      .bastille-preview-table th, .bastille-preview-table td {{
        border: 1px solid rgba(120,120,120,0.35);
        padding: 0.45rem 0.6rem;
        text-align: left;
        vertical-align: top;
      }}
      .bastille-preview-table th {{
        background: rgba(120,120,120,0.12);
        font-weight: 600;
        white-space: nowrap;
      }}
      /* 數目/日期/瀏覽量單行顯示；瀏覽量右對齊 */
      .bastille-preview-table th:nth-child(1),
      .bastille-preview-table td:nth-child(1),
      .bastille-preview-table th:nth-child(2),
      .bastille-preview-table td:nth-child(2),
      .bastille-preview-table th:nth-child(5),
      .bastille-preview-table td:nth-child(5) {{
        white-space: nowrap;
      }}
      .bastille-preview-table th:nth-child(5),
      .bastille-preview-table td:nth-child(5) {{
        text-align: right;
      }}
    </style>
    <table class="bastille-preview-table">
      <thead><tr>{headers}</tr></thead>
      <tbody>{''.join(body_rows)}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_export_section(raw_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    st.subheader("統計報告匯出")

    tab_summary, tab_bastille = st.tabs(["分類統計表", "英文版博文表（BastilleGlobal）"])
    with tab_summary:
        _render_summary_report(raw_df, filtered_df)
    with tab_bastille:
        _render_bastille_report(raw_df, filtered_df)


def _render_summary_report(raw_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    respect_filters = st.checkbox(
        "受篩選器影響",
        value=True,
        key="report_respect_filters",
        help="勾選後，預覽與匯出都按當前篩選結果統計；取消勾選則始終統計全部上傳數據。",
    )

    source_df = filtered_df if respect_filters else raw_df
    if respect_filters:
        st.caption("當前模式：跟隨篩選器。錨定分類之外的形式將自動單獨成行。")
    else:
        st.caption("當前模式：統計全部上傳數據（不受篩選器影響）。錨定分類之外的形式將自動單獨成行。")

    active_filters = st.session_state.get("active_filters") or {}
    subtitle = _date_range_subtitle(active_filters, raw_df)
    if subtitle:
        st.caption(subtitle)

    report_df = build_report_table(source_df)
    _render_preview_html(report_df)

    covered = "、".join(label for _, label in REPORT_CATEGORY_ROWS)
    st.caption(f"錨定分類：{covered}（數據中出現的其他形式自動成行）")

    docx_bytes = build_report_docx(
        report_df,
        title="內容統計報告",
        subtitle=subtitle or None,
    )
    st.download_button(
        label="匯出 Word (.docx)",
        data=docx_bytes,
        file_name=default_report_filename(),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        key="summary_download",
    )


def _render_bastille_report(raw_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    respect_filters = st.checkbox(
        "受篩選器影響",
        value=True,
        key="bastille_respect_filters",
        help="勾選後，預覽與匯出都按當前篩選結果統計；取消勾選則始終統計全部上傳數據。",
    )

    source_df = filtered_df if respect_filters else raw_df
    if respect_filters:
        st.caption("當前模式：跟隨篩選器。僅列出平台為 BastilleGlobal 的文章。")
    else:
        st.caption("當前模式：統計全部上傳數據（不受篩選器影響）。僅列出平台為 BastilleGlobal 的文章。")

    active_filters = st.session_state.get("active_filters") or {}
    subtitle = _date_range_subtitle(active_filters, raw_df)
    if subtitle:
        st.caption(subtitle)

    table_df = build_bastille_table(source_df)
    if table_df.empty:
        st.info("無平台為 BastilleGlobal 的文章。")
        return

    _render_bastille_preview_html(table_df)
    st.caption(f"共 {len(table_df)} 篇。「欄目」暫無數據，預留空白列。")

    docx_bytes = build_bastille_docx(
        table_df,
        title="巴士的報英文版博文列表",
        subtitle=subtitle or None,
    )
    st.download_button(
        label="匯出 Word (.docx)",
        data=docx_bytes,
        file_name=default_bastille_filename(),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        key="bastille_download",
    )
