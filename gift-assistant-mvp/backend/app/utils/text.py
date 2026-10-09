import re
from typing import Optional, List


def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def normalize_list(values: Optional[List[str]]) -> List[str]:
    return [normalize_text(v) for v in (values or []) if normalize_text(v)]


def parse_tags(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    parts = re.split(r"[|,;]", raw)
    return [p.strip().lower() for p in parts if p.strip()]