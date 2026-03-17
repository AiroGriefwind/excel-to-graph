from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd


DEFAULT_FILTERS: dict[str, Any] = {
    "platforms": [],
    "date_start": None,
    "date_end": None,
    "keyword": "",
    "formats": [],
}


def normalize_filters(raw_filters: dict[str, Any] | None) -> dict[str, Any]:
    if raw_filters is None:
        return DEFAULT_FILTERS.copy()

    filters = DEFAULT_FILTERS.copy()
    filters.update(raw_filters)
    return filters


def apply_filters(df: pd.DataFrame, raw_filters: dict[str, Any] | None) -> pd.DataFrame:
    filters = normalize_filters(raw_filters)
    result = df.copy()

    platforms: list[str] = filters.get("platforms") or []
    if platforms:
        result = result[result["platform"].isin(platforms)]

    formats: list[str] = filters.get("formats") or []
    if formats:
        result = result[result["format"].isin(formats)]

    keyword = str(filters.get("keyword") or "").strip()
    if keyword:
        result = result[result["title"].str.contains(keyword, case=False, na=False)]

    start: date | None = filters.get("date_start")
    end: date | None = filters.get("date_end")
    if start:
        result = result[pd.to_datetime(result["date"], errors="coerce").dt.date >= start]
    if end:
        result = result[pd.to_datetime(result["date"], errors="coerce").dt.date <= end]

    return result.reset_index(drop=True)

