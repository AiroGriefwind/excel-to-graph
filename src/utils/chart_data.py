from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_platform_pie(platform_df: pd.DataFrame):
    if platform_df.empty:
        return px.pie(names=["暫無數據"], values=[1], title="平台瀏覽量占比")

    return px.pie(
        platform_df,
        names="platform",
        values="views_sum",
        hover_data=["post_count", "interactions_sum"],
        title="平台瀏覽量占比",
        hole=0.35,
    )


def _hover_text(title: str, date_text: str, metric_label: str, value: float) -> str:
    title_text = title or "（無標題）"
    return f"{title_text}<br>{date_text}<br>{metric_label}：{value:,.0f}"


def _add_extremum_markers(
    fig: go.Figure,
    *,
    dates: pd.Series,
    values: pd.Series,
    date_texts: pd.Series,
    titles: pd.Series,
    metric_label: str,
    color: str,
    symbol: str,
    legend_name: str,
    mode: str,
) -> None:
    if values.empty:
        return
    target = values.max() if mode == "max" else values.min()
    mask = values == target
    if not mask.any():
        return

    custom = [
        _hover_text(title, date_text, metric_label, float(value))
        for title, date_text, value in zip(titles[mask], date_texts[mask], values[mask])
    ]
    fig.add_trace(
        go.Scatter(
            x=dates[mask],
            y=values[mask],
            mode="markers",
            name=legend_name,
            marker=dict(size=14, color=color, symbol=symbol, line=dict(width=2, color="white")),
            customdata=custom,
            hovertemplate="%{customdata}<extra></extra>",
            showlegend=True,
        )
    )


def build_daily_line(daily_df: pd.DataFrame):
    if daily_df.empty:
        return go.Figure().update_layout(title="按日期趨勢（暫無數據）")

    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    if df.empty:
        return go.Figure().update_layout(title="按日期趨勢（暫無數據）")

    if "top_title_views" not in df.columns:
        df["top_title_views"] = ""
    if "top_title_interactions" not in df.columns:
        df["top_title_interactions"] = ""

    date_texts = df["date"].dt.strftime("%Y/%m/%d")
    fig = go.Figure()

    series_specs = [
        {
            "column": "views_sum",
            "label": "瀏覽量",
            "title_col": "top_title_views",
            "line_color": "#63B3ED",
            "max_color": "#E53E3E",
            "min_color": "#DD6B20",
        },
        {
            "column": "interactions_sum",
            "label": "互動量",
            "title_col": "top_title_interactions",
            "line_color": "#2B6CB0",
            "max_color": "#C53030",
            "min_color": "#C05621",
        },
    ]

    for spec in series_specs:
        values = pd.to_numeric(df[spec["column"]], errors="coerce").fillna(0.0)
        titles = df[spec["title_col"]].fillna("").astype(str)
        custom = [
            _hover_text(title, date_text, spec["label"], float(value))
            for title, date_text, value in zip(titles, date_texts, values)
        ]

        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=values,
                mode="lines+markers",
                name=spec["label"],
                line=dict(color=spec["line_color"], width=2),
                marker=dict(size=7, color=spec["line_color"]),
                customdata=custom,
                hovertemplate="%{customdata}<extra></extra>",
            )
        )

        _add_extremum_markers(
            fig,
            dates=df["date"],
            values=values,
            date_texts=date_texts,
            titles=titles,
            metric_label=spec["label"],
            color=spec["max_color"],
            symbol="circle",
            legend_name=f"{spec['label']}最高",
            mode="max",
        )
        if float(values.max()) != float(values.min()):
            _add_extremum_markers(
                fig,
                dates=df["date"],
                values=values,
                date_texts=date_texts,
                titles=titles,
                metric_label=spec["label"],
                color=spec["min_color"],
                symbol="diamond",
                legend_name=f"{spec['label']}最低",
                mode="min",
            )

    fig.update_layout(
        title="按日期趨勢",
        legend_title_text="",
        xaxis_title="日期",
        yaxis_title="",
        hovermode="closest",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(tickformat="%Y/%m/%d")
    return fig
