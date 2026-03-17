from __future__ import annotations

import pandas as pd


def summarize_metrics(df: pd.DataFrame) -> dict[str, int | float]:
    if df.empty:
        return {"post_count": 0, "views_sum": 0, "interactions_sum": 0}

    return {
        "post_count": int(len(df)),
        "views_sum": float(df["views"].sum()),
        "interactions_sum": float(df["interactions"].sum()),
    }


def aggregate_by_platform(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["platform", "post_count", "views_sum", "interactions_sum"])

    grouped = (
        df.groupby("platform", dropna=False)
        .agg(post_count=("platform", "count"), views_sum=("views", "sum"), interactions_sum=("interactions", "sum"))
        .reset_index()
        .sort_values(by="views_sum", ascending=False)
    )
    return grouped


def aggregate_daily_views(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "views_sum", "interactions_sum", "post_count"])

    normalized = df.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    grouped = (
        normalized.groupby("date")
        .agg(
            views_sum=("views", "sum"),
            interactions_sum=("interactions", "sum"),
            post_count=("title", "count"),
        )
        .reset_index()
        .sort_values(by="date")
    )
    return grouped

