from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from src.utils.filtering import DEFAULT_FILTERS
from src.utils.presets import save_preset

FILTER_WIDGET_KEYS = {
    "platforms": "filter_platforms",
    "formats": "filter_formats",
    "date_start": "filter_date_start",
    "date_end": "filter_date_end",
    "keyword": "filter_keyword",
}

PRIMARY_BUTTON_CSS = """
<style>
div.stButton > button[kind="primary"] {
  background: #c62828 !important;
  border-color: #c62828 !important;
}
div.stButton > button[kind="primary"]:hover {
  background: #b71c1c !important;
  border-color: #b71c1c !important;
}
</style>
"""


def _safe_unique(df: pd.DataFrame, column: str) -> list[str]:
    if df.empty or column not in df.columns:
        return []
    values = [str(v) for v in df[column].dropna().unique() if str(v).strip()]
    return sorted(values)


def _date_bounds(df: pd.DataFrame) -> tuple[date | None, date | None]:
    if df.empty or "date" not in df.columns:
        return None, None
    s = pd.to_datetime(df["date"], errors="coerce").dropna()
    if s.empty:
        return None, None
    return s.min().date(), s.max().date()


def _sync_widget_state(filters: dict[str, Any], min_date: date | None, max_date: date | None) -> None:
    st.session_state[FILTER_WIDGET_KEYS["platforms"]] = list(filters.get("platforms") or [])
    st.session_state[FILTER_WIDGET_KEYS["formats"]] = list(filters.get("formats") or [])
    st.session_state[FILTER_WIDGET_KEYS["keyword"]] = str(filters.get("keyword") or "")
    st.session_state[FILTER_WIDGET_KEYS["date_start"]] = filters.get("date_start") or min_date or date.today()
    st.session_state[FILTER_WIDGET_KEYS["date_end"]] = filters.get("date_end") or max_date or date.today()


def _clamp_widget_dates(min_date: date | None, max_date: date | None) -> None:
    if min_date is None or max_date is None:
        return

    start_key = FILTER_WIDGET_KEYS["date_start"]
    end_key = FILTER_WIDGET_KEYS["date_end"]
    start_val = st.session_state.get(start_key, min_date)
    end_val = st.session_state.get(end_key, max_date)

    if start_val < min_date:
        st.session_state[start_key] = min_date
    elif start_val > max_date:
        st.session_state[start_key] = max_date

    if end_val < min_date:
        st.session_state[end_key] = min_date
    elif end_val > max_date:
        st.session_state[end_key] = max_date


def _summarize_filters(filters: dict[str, Any]) -> str:
    platforms = "、".join(filters.get("platforms") or []) or "全部"
    formats = "、".join(filters.get("formats") or []) or "全部"
    start = str(filters.get("date_start") or "不限")
    end = str(filters.get("date_end") or "不限")
    keyword = str(filters.get("keyword") or "").strip() or "无"
    return f"平台：{platforms} ｜ 形式：{formats} ｜ 日期：{start} ~ {end} ｜ 关键词：{keyword}"


def sync_filter_widgets(filters: dict[str, Any], df: pd.DataFrame) -> None:
    min_date, max_date = _date_bounds(df)
    payload = DEFAULT_FILTERS.copy()
    payload.update(filters or {})
    _sync_widget_state(payload, min_date, max_date)


def _build_filters_from_widgets(min_date: date | None, max_date: date | None) -> dict[str, Any]:
    start = st.session_state[FILTER_WIDGET_KEYS["date_start"]]
    end = st.session_state[FILTER_WIDGET_KEYS["date_end"]]

    # 当用户选择了全范围，等价于“不限制”
    if min_date and start == min_date:
        start = None
    if max_date and end == max_date:
        end = None

    return {
        "platforms": list(st.session_state[FILTER_WIDGET_KEYS["platforms"]] or []),
        "formats": list(st.session_state[FILTER_WIDGET_KEYS["formats"]] or []),
        "date_start": start,
        "date_end": end,
        "keyword": str(st.session_state[FILTER_WIDGET_KEYS["keyword"]] or "").strip(),
    }


def render_filter_panel(df: pd.DataFrame, active_filters: dict[str, Any]) -> tuple[dict[str, Any], bool, bool]:
    filters = DEFAULT_FILTERS.copy()
    filters.update(active_filters or {})

    min_date, max_date = _date_bounds(df)
    platform_options = _safe_unique(df, "platform")
    format_options = _safe_unique(df, "format")

    init_flag = "filter_widgets_initialized"
    if not st.session_state.get(init_flag):
        _sync_widget_state(filters, min_date, max_date)
        st.session_state[init_flag] = True
    _clamp_widget_dates(min_date, max_date)

    st.caption(f"当前筛选条件：{_summarize_filters(filters)}")
    st.markdown(PRIMARY_BUTTON_CSS, unsafe_allow_html=True)

    apply_clicked = False
    reset_clicked = False

    with st.expander("筛选器（点击展开修改）", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.multiselect(
                "平台",
                options=platform_options,
                key=FILTER_WIDGET_KEYS["platforms"],
            )
            st.multiselect(
                "形式",
                options=format_options,
                key=FILTER_WIDGET_KEYS["formats"],
            )
        with c2:
            st.date_input(
                "开始日期",
                min_value=min_date,
                max_value=max_date,
                disabled=min_date is None,
                key=FILTER_WIDGET_KEYS["date_start"],
            )
            st.date_input(
                "结束日期",
                min_value=min_date,
                max_value=max_date,
                disabled=max_date is None,
                key=FILTER_WIDGET_KEYS["date_end"],
            )

            st.text_input(
                "标题关键字",
                placeholder="输入标题关键字（模糊匹配）",
                key=FILTER_WIDGET_KEYS["keyword"],
            )

        current_filters = _build_filters_from_widgets(min_date, max_date)

        left_col, right_col, right_col2 = st.columns([1.2, 1, 1])
        with left_col:
            with st.popover("保存筛选条件", use_container_width=True):
                st.write("请确认以下筛选条件：")
                st.json(
                    {
                        "platforms": current_filters.get("platforms", []),
                        "formats": current_filters.get("formats", []),
                        "date_start": str(current_filters.get("date_start") or ""),
                        "date_end": str(current_filters.get("date_end") or ""),
                        "keyword": current_filters.get("keyword", ""),
                    }
                )
                preset_name = st.text_input("筛选条件名称", key="new_preset_name", placeholder="例如：Facebook_本周高浏览")
                if st.button("确认保存", use_container_width=True):
                    clean_name = preset_name.strip()
                    if not clean_name:
                        st.warning("请输入筛选条件名称。")
                    else:
                        save_preset(clean_name, current_filters)
                        st.success(f"已保存筛选条件：{clean_name}")
        with right_col:
            reset_clicked = st.button("重置", use_container_width=True)
        with right_col2:
            apply_clicked = st.button("筛选", type="primary", use_container_width=True)

        if reset_clicked:
            _sync_widget_state(DEFAULT_FILTERS.copy(), min_date, max_date)

    if reset_clicked:
        return DEFAULT_FILTERS.copy(), False, True

    return _build_filters_from_widgets(min_date, max_date), apply_clicked, False

