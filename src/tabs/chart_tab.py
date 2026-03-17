from __future__ import annotations

import pandas as pd
import streamlit as st

from src.utils.chart_data import build_daily_line, build_platform_pie
from src.utils.metrics import aggregate_by_platform, aggregate_daily_views, summarize_metrics


def render_chart_section(filtered_df: pd.DataFrame) -> None:
    st.subheader("图表区域")
    summary = summarize_metrics(filtered_df)

    k1, k2, k3 = st.columns(3)
    k1.metric("内容条数", f"{summary['post_count']:,}")
    k2.metric("浏览量总和", f"{summary['views_sum']:,.0f}")
    k3.metric("互动量总和", f"{summary['interactions_sum']:,.0f}")

    platform_df = aggregate_by_platform(filtered_df)
    daily_df = aggregate_daily_views(filtered_df)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(build_platform_pie(platform_df), use_container_width=True)
    with c2:
        st.plotly_chart(build_daily_line(daily_df), use_container_width=True)

