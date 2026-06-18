from pathlib import Path
from typing import Any, Dict


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return value.strip('"').strip("'")


def _fallback_yaml(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current_key = None
    current_map_key = None
    current_list_item = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            current_key = line[:-1]
            result[current_key] = []
            current_map_key = None
            current_list_item = None
            continue

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            if value.strip():
                result[current_key] = _parse_scalar(value)
            else:
                result[current_key] = {}
            current_map_key = current_key
            current_list_item = None
            continue

        if indent == 2 and line.startswith("- "):
            value = line[2:]
            if ":" in value:
                key, item_value = value.split(":", 1)
                current_list_item = {key.strip(): _parse_scalar(item_value)}
                result.setdefault(current_key, []).append(current_list_item)
            else:
                result.setdefault(current_key, []).append(_parse_scalar(value))
            continue

        if indent == 2 and ":" in line:
            key, value = line.split(":", 1)
            if not isinstance(result.get(current_key), dict):
                result[current_key] = {}
            result[current_key][key.strip()] = _parse_scalar(value)
            current_map_key = current_key
            continue

        if indent == 4 and current_list_item is not None and ":" in line:
            key, value = line.split(":", 1)
            current_list_item[key.strip()] = _parse_scalar(value)
            continue

        if indent == 4 and current_map_key and ":" in line:
            key, value = line.split(":", 1)
            result[current_map_key][key.strip()] = _parse_scalar(value)
            continue

    return result


def load_yaml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded or {}
    except Exception:
        return _fallback_yaml(text)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_taste_prompt(root: Path = None) -> Dict[str, Any]:
    base = root or project_root()
    return load_yaml(base / "config" / "taste_prompt.yaml")


def load_scoring_rubrics(root: Path = None) -> Dict[str, Any]:
    base = root or project_root()
    return load_yaml(base / "config" / "scoring_rubrics.yaml")


def load_sources(root: Path = None) -> Dict[str, Any]:
    base = root or project_root()
    return load_yaml(base / "config" / "sources.yaml")

