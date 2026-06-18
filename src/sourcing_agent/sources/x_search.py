import json
import urllib.parse
import urllib.request
from typing import List, Optional

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind


def parse_x_recent(payload: str) -> List[SourceItem]:
    data = json.loads(payload)
    items = []
    for post in data.get("data", []):
        text = post.get("text", "")
        post_id = post.get("id", "")
        items.append(
            SourceItem(
                source="x",
                source_kind=SourceKind.X,
                artifact_type=ArtifactType.POST,
                title=text[:120] or "X post",
                url="https://x.com/i/web/status/" + post_id,
                raw_text=text,
                published_at=post.get("created_at"),
                metadata=post.get("public_metrics", {}),
            )
        )
    return items


def fetch_x_recent(query: str, bearer_token: Optional[str], max_results: int = 10) -> List[SourceItem]:
    if not bearer_token:
        return []
    params = urllib.parse.urlencode(
        {
            "query": query,
            "max_results": str(max_results),
            "tweet.fields": "created_at,public_metrics,author_id",
        }
    )
    request = urllib.request.Request(
        "https://api.x.com/2/tweets/search/recent?" + params,
        headers={"Authorization": "Bearer " + bearer_token, "User-Agent": "investment-sourcing-agent"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return parse_x_recent(response.read().decode("utf-8"))

