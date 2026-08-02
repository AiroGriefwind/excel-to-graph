from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.utils.report_export import (
    DISPLAY_COLUMNS,
    REPORT_CATEGORY_ROWS,
    TOTAL_LABEL,
    build_report_docx,
    build_report_table,
    default_report_filename,
)


def _render_preview_html(report_df: pd.DataFrame) -> None:
    """用 HTML 表预览，避免 Streamlit dataframe 不支持重复列名「平均」。"""
    headers = "".join(f"<th>{html.escape(col)}</th>" for col in DISPLAY_COLUMNS)
    body_rows: list[str] = []
    for _, row in report_df.iterrows():
        values = [
            row["分類"],
            row["數目"],
            row["瀏覽量"],
            row["平均瀏覽量"],
            row["互動量"],
            row["平均互動量"],
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
      }}
      .report-preview-table th, .report-preview-table td {{
        border: 1px solid rgba(120,120,120,0.35);
        padding: 0.45rem 0.6rem;
        text-align: center;
      }}
      .report-preview-table th {{
        background: rgba(120,120,120,0.12);
        font-weight: 600;
      }}
      .report-preview-table td:first-child {{
        text-align: left;
      }}
    </style>
    <table class="report-preview-table">
      <thead><tr>{headers}</tr></thead>
      <tbody>{''.join(body_rows)}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_export_section(raw_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    st.subheader("統計報告匯出")

    respect_filters = st.checkbox(
        "受篩選器影響",
        value=False,
        key="report_respect_filters",
        help="勾選後，預覽與匯出都按當前篩選結果統計；取消勾選則始終統計全部上傳數據。",
    )

    source_df = filtered_df if respect_filters else raw_df
    if respect_filters:
        st.caption("當前模式：跟隨篩選器。僅統計下列固定分類。")
        subtitle = "基於當前篩選條件匯出"
    else:
        st.caption("當前模式：統計全部上傳數據（不受篩選器影響）。僅統計下列固定分類。")
        subtitle = "基於全部上傳數據匯出（不受篩選器影響）"

    report_df = build_report_table(source_df)
    _render_preview_html(report_df)

    covered = "、".join(label for _, label in REPORT_CATEGORY_ROWS)
    st.caption(f"分項分類：{covered}")

    docx_bytes = build_report_docx(
        report_df,
        title="內容統計報告",
        subtitle=subtitle,
    )
    st.download_button(
        label="匯出 Word (.docx)",
        data=docx_bytes,
        file_name=default_report_filename(),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )
