from __future__ import annotations

from typing import Any

import streamlit as st


def render_header_and_presets(presets: dict[str, dict[str, Any]]) -> str | None:
    st.title("Excel 内容分析仪表盘")
    st.caption("多文件上传 / 条件筛选 / 图表分析 / 卡片浏览")

    st.subheader("已保存筛选条件")
    if not presets:
        st.info("还没有已保存的筛选条件。请在下方筛选器区域保存。")
        return None

    selected_preset_name: str | None = None
    cols = st.columns(min(4, max(1, len(presets))))
    for idx, name in enumerate(presets.keys()):
        col = cols[idx % len(cols)]
        if col.button(name, use_container_width=True, key=f"preset_btn_{idx}_{name}"):
            selected_preset_name = name

    return selected_preset_name

