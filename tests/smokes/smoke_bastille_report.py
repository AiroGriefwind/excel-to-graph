from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.bastille_report import (  # noqa: E402
    BASTILLE_COLUMNS,
    build_bastille_docx,
    build_bastille_table,
    filter_bastille_rows,
)
from src.utils.excel_loader import parse_multiple_excels  # noqa: E402


def main() -> None:
    # 合成數據：驗證篩選、排序、編號、日期格式、欄目填充
    df = pd.DataFrame(
        [
            {"platform": "BastilleGlobal", "title": "Later Post", "date": "2026-08-03", "views": 100, "section": "Bastille Commentary"},
            {"platform": "巴士的報", "title": "中文新聞", "date": "2026-08-01", "views": 999, "section": "止戈堂"},
            {"platform": "BastilleGlobal", "title": "Early Post", "date": "2026-08-01", "views": 200, "section": "-"},
            {"platform": "bastilleglobal", "title": "No Date Post", "date": None, "views": 50},
        ]
    )

    table = build_bastille_table(df)
    assert list(table.columns) == BASTILLE_COLUMNS
    assert len(table) == 3, "應僅含 BastilleGlobal 平台（大小寫不敏感）"
    assert table["數目"].tolist() == [1, 2, 3], "數目應順排"
    assert table["標題"].tolist() == ["Early Post", "Later Post", "No Date Post"], "應按日期升序，無日期排最後"
    assert table["日期"].tolist()[:2] == ["20260801", "20260803"], "日期應為 YYYYMMDD"
    assert table["日期"].iloc[2] == "", "無日期應留空"
    assert table["欄目"].tolist() == ["-", "Bastille Commentary", ""], "欄目應取自 section（缺失留空，'-' 原樣保留）"
    assert table["瀏覽量"].tolist() == [200, 100, 50]

    # 空表 / 無匹配平台
    empty_table = build_bastille_table(pd.DataFrame())
    assert empty_table.empty and list(empty_table.columns) == BASTILLE_COLUMNS
    no_match = build_bastille_table(pd.DataFrame([{"platform": "YouTube", "title": "x"}]))
    assert no_match.empty

    # 真實 mock 樣本回歸
    mock_dir = ROOT_DIR / "tests" / "mocks"
    files = sorted(mock_dir.glob("*.xlsx"))
    handlers = [open(path, "rb") for path in files]
    try:
        raw_df = parse_multiple_excels(handlers)
    finally:
        for h in handlers:
            h.close()

    subset = filter_bastille_rows(raw_df)
    assert len(subset) > 0, "mock 樣本應含 BastilleGlobal 文章"
    real_table = build_bastille_table(raw_df)
    assert len(real_table) == len(subset)
    assert real_table["數目"].tolist() == list(range(1, len(subset) + 1))
    date_texts = [d for d in real_table["日期"] if d]
    assert all(re.fullmatch(r"\d{8}", d) for d in date_texts), "日期應為 YYYYMMDD"
    assert date_texts == sorted(date_texts), "日期應升序"

    docx_bytes = build_bastille_docx(real_table)
    assert docx_bytes[:2] == b"PK"  # docx 是 zip 容器
    assert len(docx_bytes) > 1000

    print("[OK] BastilleGlobal 博文表冒煙通過")
    print(f"- mock 樣本 BastilleGlobal 文章數: {len(real_table)}")


if __name__ == "__main__":
    main()
