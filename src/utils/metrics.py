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


def _top_title_for_metric(group: pd.DataFrame, metric: str) -> str:
    if group.empty or metric not in group.columns:
        return ""
    working = group.copy()
    working[metric] = pd.to_numeric(working[metric], errors="coerce").fillna(0)
    row = working.loc[working[metric].idxmax()]
    title = str(row.get("title", "")).replace("\n", " ").strip()
    if not title or title in {"None", "nan"}:
        return ""
    return title if len(title) <= 48 else title[:48] + "…"


def aggregate_daily_views(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "views_sum",
                "interactions_sum",
                "post_count",
                "top_title_views",
                "top_title_interactions",
            ]
        )

    normalized = df.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    normalized = normalized.dropna(subset=["date"])
    if normalized.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "views_sum",
                "interactions_sum",
                "post_count",
                "top_title_views",
                "top_title_interactions",
            ]
        )

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

    title_rows = []
    for day, group in normalized.groupby("date"):
        title_rows.append(
            {
                "date": day,
                "top_title_views": _top_title_for_metric(group, "views"),
                "top_title_interactions": _top_title_for_metric(group, "interactions"),
            }
        )
    title_df = pd.DataFrame(title_rows)
    return grouped.merge(title_df, on="date", how="left")
