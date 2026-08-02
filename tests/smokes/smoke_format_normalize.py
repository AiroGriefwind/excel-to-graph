from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.format_normalize import detect_language, normalize_format  # noqa: E402


def main() -> None:
    assert normalize_format("新聞報道") == "新聞報道"
    assert normalize_format("新聞報道（連視頻）") == "新聞報道"
    assert normalize_format("新闻报道（连视频）") == "新聞報道"

    assert (
        normalize_format("評論文章", title="胡曉明：黎智英案為社會帶來深切反思", platform="巴士的報")
        == "評論/博客文章（中）"
    )
    assert (
        normalize_format("博客文章", title="Investment opportunities for the Northern Metropolis project", platform="巴士的報")
        == "評論/博客文章（英）"
    )
    assert (
        normalize_format("博客文章", title="任何中文標題", platform="BastilleGlobal")
        == "評論/博客文章（英）"
    )
    assert (
        normalize_format("評論文章（連視頻）", title="中文評論標題", platform="巴士的報")
        == "評論/博客文章（連視頻）（中）"
    )
    assert (
        normalize_format("博客文章（連視頻）", title="An English blog with video", platform="BastilleGlobal")
        == "評論/博客文章（連視頻）（英）"
    )

    # 未命中规则的形式保持原样
    assert normalize_format("專題報道") == "專題報道"
    assert normalize_format("影片") == "影片"

    assert detect_language("", "") == "其他"
    assert detect_language("Hello world", "YouTube") == "英"
    assert detect_language("中文標題", "YouTube") == "中"

    print("[OK] 形式归一化冒烟通过")


if __name__ == "__main__":
    main()
