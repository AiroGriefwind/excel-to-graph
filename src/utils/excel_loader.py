from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd

from .constants import COLUMN_ALIASES, STANDARD_COLUMNS


def _normalize_column_name(column_name: str) -> str:
    text = str(column_name).strip()
    return COLUMN_ALIASES.get(text, text.lower())


def _clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).replace({"N/A": "", "nan": ""}),
        errors="coerce",
    ).fillna(0)


def _parse_single_date(value) -> date | None:
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    # 兼容 Excel 序列日期（常见于纯数字单元格）
    if isinstance(value, (int, float)) and value > 0:
        base = datetime(1899, 12, 30)
        try:
            return (base + timedelta(days=float(value))).date()
        except Exception:  # noqa: BLE001
            return None

    text = str(value).strip()
    if not text:
        return None

    normalized = (
        text.replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
        .replace("/", "-")
        .replace(".", "-")
        .strip()
    )

    # 优先严格格式，避免推断 warning 与歧义
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue

    # 宽松兜底：提取 YYYY MM DD
    parts = pd.Series([normalized]).str.extract(r"(?P<year>\d{4})\D*(?P<month>\d{1,2})\D*(?P<day>\d{1,2})")
    if not parts.isna().all(axis=None):
        try:
            y = int(parts.loc[0, "year"])
            m = int(parts.loc[0, "month"])
            d = int(parts.loc[0, "day"])
            return date(y, m, d)
        except Exception:  # noqa: BLE001
            return None
    return None


def _parse_date_series(series: pd.Series) -> pd.Series:
    return series.apply(_parse_single_date)


def parse_single_excel(file_obj, source_name: str | None = None) -> pd.DataFrame:
    """
    解析单个 Excel:
    - 第 1 行标题
    - 第 2 行报表时间
    - 第 3 行空行
    - 第 4 行列名
    - 第 5 行开始数据
    """
    df = pd.read_excel(file_obj, header=3, engine="openpyxl")
    df.columns = [_normalize_column_name(col) for col in df.columns]

    existing_columns = [col for col in STANDARD_COLUMNS if col in df.columns]
    df = df[existing_columns].copy()

    for required_col in STANDARD_COLUMNS:
        if required_col not in df.columns:
            df[required_col] = None

    df = df[STANDARD_COLUMNS]
    df = df.dropna(how="all")

    df["date"] = _parse_date_series(df["date"])
    df["platform"] = df["platform"].astype(str).str.strip()
    df["title"] = df["title"].astype(str).str.strip()
    df["format"] = df["format"].astype(str).str.strip()
    df["link"] = df["link"].astype(str).str.strip()
    df["views"] = _clean_numeric(df["views"])
    df["interactions"] = _clean_numeric(df["interactions"])

    file_name = source_name or getattr(file_obj, "name", "uploaded.xlsx")
    df["source_file"] = Path(file_name).name

    # 去掉由缺失值造成的 "None"/"nan" 文本噪音
    text_cols = ["platform", "title", "format", "link"]
    for col in text_cols:
        df[col] = df[col].replace({"None": "", "nan": ""})

    return df.reset_index(drop=True)


def parse_multiple_excels(files: Iterable) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for file_obj in files:
        frames.append(parse_single_excel(file_obj, source_name=getattr(file_obj, "name", None)))

    if not frames:
        return pd.DataFrame(columns=STANDARD_COLUMNS + ["source_file"])

    return pd.concat(frames, ignore_index=True)

