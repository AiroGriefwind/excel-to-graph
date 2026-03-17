from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .constants import PRESET_FILE_PATH


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    return value


def _write_presets(payload: dict[str, Any], path: Path) -> None:
    _ensure_parent_dir(path)
    path.write_text(json.dumps(_to_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def load_presets(path: Path = PRESET_FILE_PATH) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}
    return data


def save_preset(name: str, filter_payload: dict[str, Any], path: Path = PRESET_FILE_PATH) -> None:
    payload = load_presets(path)
    payload[name] = _to_jsonable(filter_payload)
    _write_presets(payload, path)


def delete_preset(name: str, path: Path = PRESET_FILE_PATH) -> None:
    payload = load_presets(path)
    if name not in payload:
        return
    payload.pop(name)
    _write_presets(payload, path)

