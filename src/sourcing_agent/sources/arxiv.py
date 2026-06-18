import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind

ATOM = "{http://www.w3.org/2005/Atom}"


def build_query_url(query: str, max_results: int = 20) -> str:
    params = urllib.parse.urlencode(
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
    )
    return "https://export.arxiv.org/api/query?" + params


def _text(parent: ET.Element, name: str) -> str:
    node = parent.find(ATOM + name)
    return " ".join((node.text or "").split()) if node is not None else ""


def parse_arxiv_feed(payload: str) -> List[SourceItem]:
    root = ET.fromstring(payload)
    items = []
    for entry in root.findall(ATOM + "entry"):
        paper_url = _text(entry, "id")
        title = _text(entry, "title")
        summary = _text(entry, "summary")
        authors = [_text(author, "name") for author in entry.findall(ATOM + "author")]
        items.append(
            SourceItem(
                source="arxiv",
                source_kind=SourceKind.ARXIV,
                artifact_type=ArtifactType.PAPER,
                title=title,
                url=paper_url,
                raw_text=title + "\n" + summary,
                published_at=_text(entry, "published"),
                metadata={"authors": authors},
            )
        )
    return items


def fetch_arxiv(query: str, max_results: int = 20) -> List[SourceItem]:
    request = urllib.request.Request(build_query_url(query, max_results), headers={"User-Agent": "investment-sourcing-agent"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_arxiv_feed(response.read().decode("utf-8"))

