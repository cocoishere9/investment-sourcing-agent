import json
import urllib.parse
import urllib.request
from typing import List, Optional

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind


def build_search_url(query: str, per_page: int = 20) -> str:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": str(per_page),
        }
    )
    return "https://api.github.com/search/repositories?" + params


def parse_github_search(payload: str) -> List[SourceItem]:
    data = json.loads(payload)
    items = []
    for repo in data.get("items", []):
        text = "\n".join(
            [
                repo.get("full_name", ""),
                repo.get("description") or "",
                repo.get("html_url", ""),
            ]
        )
        items.append(
            SourceItem(
                source="github",
                source_kind=SourceKind.GITHUB,
                artifact_type=ArtifactType.REPO,
                title=repo.get("full_name", "untitled repository"),
                url=repo.get("html_url", ""),
                raw_text=text,
                published_at=repo.get("pushed_at"),
                metadata={
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language"),
                    "owner": repo.get("owner", {}).get("login"),
                },
            )
        )
    return items


def fetch_github_search(query: str, token: Optional[str] = None, per_page: int = 20) -> List[SourceItem]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "investment-sourcing-agent"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(build_search_url(query, per_page), headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_github_search(response.read().decode("utf-8"))

