import re
from typing import Dict, List, Tuple

from sourcing_agent.models import SourceItem

EMAIL_RE = re.compile(r"(?<![\w.])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?!\w)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s)>\"]+")

CHINA_PUBLIC_TERMS = [
    "china",
    "chinese",
    "mandarin",
    "beijing",
    "shanghai",
    "shenzhen",
    "tsinghua",
    "peking university",
    "pku",
    "china market",
    "cross-border",
]

CHINESE_NAME_HINTS = [
    "wang",
    "zhang",
    "li",
    "liu",
    "chen",
    "yang",
    "huang",
    "zhao",
    "zhou",
    "wu",
    "xu",
    "sun",
    "ma",
    "gao",
    "lin",
    "he",
    "luo",
    "wei",
    "xin",
    "hao",
]


def extract_emails(text: str) -> List[str]:
    seen = set()
    emails = []
    for match in EMAIL_RE.finditer(text):
        email = match.group(1).lower()
        if email not in seen:
            seen.add(email)
            emails.append(email)
    return emails


def extract_urls(text: str) -> List[str]:
    return URL_RE.findall(text)


def short_summary(text: str, limit: int = 240) -> str:
    normalized = " ".join(text.split())
    return normalized[:limit]


def detect_china_affinity(text: str) -> Tuple[str, Dict[str, str]]:
    lowered = text.lower()
    if any("\\u4e00" <= char <= "\\u9fff" for char in text):
        return "high", {"reason": "contains_chinese_text", "confidence": "high"}
    for term in CHINA_PUBLIC_TERMS:
        if term in lowered:
            return "medium", {"reason": "public_china_related_term", "term": term, "confidence": "medium"}
    words = set(re.findall(r"[a-z]+", lowered))
    if words.intersection(CHINESE_NAME_HINTS):
        return "low", {"reason": "name_heuristic_only", "confidence": "low"}
    return "unknown", {"reason": "no_signal", "confidence": "unknown"}


def base_evidence(item: SourceItem, reason: str) -> List[Dict[str, str]]:
    return [{"url": item.url, "reason": reason, "source": item.source}]
