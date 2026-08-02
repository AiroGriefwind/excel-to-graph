from __future__ import annotations

import re

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_VIDEO_MARKERS = ("（連視頻）", "(連視頻)", "（连视频）", "(连视频)", "（連视频）", "(連视频)")


def detect_language(title: str | None, platform: str | None) -> str:
    """
    粗分语言：中 / 英 / 其他。
    - BastilleGlobal 平台强制视为英文
    - 其余按标题中的汉字/拉丁字母占比判断
    """
    platform_text = str(platform or "").strip().lower()
    if "bastilleglobal" in platform_text:
        return "英"

    text = str(title or "").strip()
    cjk_count = len(_CJK_RE.findall(text))
    latin_count = len(_LATIN_RE.findall(text))

    if cjk_count == 0 and latin_count == 0:
        return "其他"
    if cjk_count == 0:
        return "英"
    if latin_count == 0:
        return "中"
    return "中" if cjk_count >= latin_count else "英"


def _strip_video_marker(text: str) -> tuple[str, bool]:
    has_video = False
    result = text
    for marker in _VIDEO_MARKERS:
        if marker in result:
            has_video = True
            result = result.replace(marker, "")
    # 兼容「連視頻」散落在括号外的写法
    if "連視頻" in result or "连视频" in result:
        has_video = True
        result = result.replace("連視頻", "").replace("连视频", "")
        result = result.replace("（）", "").replace("()", "")
    return result.strip(), has_video


def normalize_format(raw_format: str | None, title: str | None = None, platform: str | None = None) -> str:
    """
    将原始「形式」归一为筛选器用分类：
    1) 新聞報道 / 新聞報道（連視頻） -> 新聞報道
    2) 評論文章 / 博客文章 -> 評論/博客文章（中|英|其他）
    3) 上述评论/博客若带连视频 -> 評論/博客文章（連視頻）（中|英|其他）
    其余形式原样返回。
    """
    raw = str(raw_format or "").strip()
    if not raw:
        return ""

    compact = raw.replace(" ", "")
    base, has_video = _strip_video_marker(compact)

    if base in {"新聞報道", "新闻报道"}:
        return "新聞報道"

    if base in {"評論文章", "评论文章", "博客文章"}:
        lang = detect_language(title, platform)
        if has_video:
            return f"評論/博客文章（連視頻）（{lang}）"
        return f"評論/博客文章（{lang}）"

    return raw


def apply_format_normalization(df):
    """写入 format_raw，并将 format 替换为归一化分类。"""
    result = df.copy()
    if "format" not in result.columns:
        result["format"] = ""
    result["format_raw"] = result["format"]
    result["format"] = [
        normalize_format(fmt, title, platform)
        for fmt, title, platform in zip(
            result["format_raw"],
            result["title"] if "title" in result.columns else [""] * len(result),
            result["platform"] if "platform" in result.columns else [""] * len(result),
        )
    ]
    return result
