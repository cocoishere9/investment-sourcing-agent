import re
import urllib.request
from typing import List

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def clean_html(html: str) -> str:
    return " ".join(TAG_RE.sub(" ", html).split())


def parse_webpage(source: str, url: str, html: str, artifact_type: ArtifactType = ArtifactType.COMPANY) -> List[SourceItem]:
    title_match = TITLE_RE.search(html)
    title = " ".join(title_match.group(1).split()) if title_match else source
    return [
        SourceItem(
            source=source,
            source_kind=SourceKind.WEBPAGE,
            artifact_type=artifact_type,
            title=title,
            url=url,
            raw_text=clean_html(html),
            metadata={"parser": "webpage"},
        )
    ]


def fetch_webpage(source: str, url: str, artifact_type: ArtifactType = ArtifactType.COMPANY) -> List[SourceItem]:
    request = urllib.request.Request(url, headers={"User-Agent": "investment-sourcing-agent"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_webpage(source, url, response.read().decode("utf-8", errors="replace"), artifact_type)

