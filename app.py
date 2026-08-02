from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.tabs import (
    render_chart_section,
    render_content_section,
    render_export_section,
    render_filter_panel,
    render_header_and_presets,
    render_sidebar_upload,
    sync_filter_widgets,
)
from src.utils.excel_loader import parse_multiple_excels
from src.utils.filtering import DEFAULT_FILTERS, apply_filters
from src.utils.presets import load_presets
from src.utils.state import init_state


def _coerce_preset_dates(filters: dict) -> dict:
    payload = dict(filters)
    for key in ("date_start", "date_end"):
        value = payload.get(key)
        if isinstance(value, date) or value is None:
            continue
        parsed = pd.to_datetime(value, errors="coerce")
        payload[key] = None if pd.isna(parsed) else parsed.date()
    return payload


def main() -> None:
    st.set_page_config(page_title="Excel 分析看板", layout="wide")
    init_state()

    files = render_sidebar_upload()
    presets = load_presets()

    selected_preset_name = render_header_and_presets(presets)
    if selected_preset_name:
        st.session_state.active_filters = _coerce_preset_dates(presets[selected_preset_name])
        if st.session_state.raw_df is not None:
            sync_filter_widgets(st.session_state.active_filters, st.session_state.raw_df)
        st.success(f"已应用筛选条件：{selected_preset_name}")

    if not files:
        st.info("请先在左侧上传至少一个 Excel 文件。")
        return

    try:
        raw_df = parse_multiple_excels(files)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Excel 解析失败：{exc}")
        return

    draft_filters, apply_clicked, reset_clicked = render_filter_panel(raw_df, st.session_state.active_filters)
    if apply_clicked:
        st.session_state.active_filters = draft_filters
    if reset_clicked:
        st.session_state.active_filters = DEFAULT_FILTERS.copy()
        st.rerun()

    filtered_df = apply_filters(raw_df, st.session_state.active_filters)
    st.session_state.raw_df = raw_df
    st.session_state.filtered_df = filtered_df

    render_chart_section(filtered_df)
    render_export_section(raw_df, filtered_df)
    render_content_section(filtered_df)


if __name__ == "__main__":
    main()

