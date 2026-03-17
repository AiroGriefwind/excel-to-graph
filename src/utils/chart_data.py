from __future__ import annotations

import plotly.express as px
import pandas as pd


def build_platform_pie(platform_df: pd.DataFrame):
    if platform_df.empty:
        return px.pie(names=["暂无数据"], values=[1], title="平台浏览量占比")

    return px.pie(
        platform_df,
        names="platform",
        values="views_sum",
        hover_data=["post_count", "interactions_sum"],
        title="平台浏览量占比",
        hole=0.35,
    )


def build_daily_line(daily_df: pd.DataFrame):
    if daily_df.empty:
        return px.line(title="按日期趋势（暂无数据）")

    fig = px.line(
        daily_df,
        x="date",
        y=["views_sum", "interactions_sum"],
        markers=True,
        title="按日期趋势",
    )
    fig.update_layout(legend_title_text="")
    return fig

