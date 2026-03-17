from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.utils.presets import delete_preset, load_presets, save_preset  # noqa: E402


def main() -> None:
    test_path = ROOT_DIR / "tests" / "smokes" / ".tmp_filter_presets.json"
    if test_path.exists():
        test_path.unlink()

    payload = {
        "platforms": ["Facebook"],
        "formats": ["文章"],
        "date_start": "2026-03-01",
        "date_end": "2026-03-31",
        "keyword": "關鍵字",
    }

    save_preset("demoPreset", payload, path=test_path)
    loaded = load_presets(path=test_path)
    assert "demoPreset" in loaded, "保存预设失败"
    assert loaded["demoPreset"]["platforms"] == ["Facebook"], "预设字段不一致"

    delete_preset("demoPreset", path=test_path)
    loaded_after = load_presets(path=test_path)
    assert "demoPreset" not in loaded_after, "删除预设失败"

    if test_path.exists():
        test_path.unlink()

    print("[OK] 预设读写冒烟通过")


if __name__ == "__main__":
    main()

