from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.excel_loader import parse_multiple_excels  # noqa: E402
from src.utils.filtering import apply_filters  # noqa: E402
from src.utils.metrics import aggregate_by_platform, aggregate_daily_views, summarize_metrics  # noqa: E402


def main() -> None:
    mock_dir = ROOT_DIR / "tests" / "mocks"
    files = sorted(mock_dir.glob("*.xlsx"))
    assert files, "tests/mocks 下未找到 .xlsx 样本文件"

    handlers = [open(path, "rb") for path in files]
    try:
        raw_df = parse_multiple_excels(handlers)
    finally:
        for h in handlers:
            h.close()

    required_cols = {"date", "platform", "title", "format", "link", "views", "interactions", "source_file"}
    assert required_cols.issubset(set(raw_df.columns)), f"缺少必须列: {required_cols - set(raw_df.columns)}"
    assert len(raw_df) > 0, "解析后数据为空"

    first_platform = str(raw_df["platform"].dropna().iloc[0])
    filtered = apply_filters(raw_df, {"platforms": [first_platform]})
    summary = summarize_metrics(filtered)
    by_platform = aggregate_by_platform(filtered)
    daily = aggregate_daily_views(filtered)

    assert summary["post_count"] >= 0, "post_count 计算失败"
    assert summary["views_sum"] >= 0, "views_sum 计算失败"
    assert not by_platform.empty, "平台聚合为空"
    assert "date" in daily.columns, "日期聚合缺少 date 列"

    print("[OK] 数据管道冒烟通过")
    print(f"- 输入文件数: {len(files)}")
    print(f"- 总记录数: {len(raw_df)}")
    print(f"- 平台筛选: {first_platform}")
    print(f"- 筛选后记录数: {summary['post_count']}")


if __name__ == "__main__":
    main()

