import json
from typing import List

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind


def parse_hn_story(payload: str) -> List[SourceItem]:
    data = json.loads(payload)
    if data.get("type") != "story":
        return []
    return [
        SourceItem(
            source="hackernews",
            source_kind=SourceKind.HN,
            artifact_type=ArtifactType.POST,
            title=data.get("title", "Hacker News story"),
            url=data.get("url") or "https://news.ycombinator.com/item?id=" + str(data.get("id")),
            raw_text=data.get("text") or data.get("title", ""),
            published_at=str(data.get("time")) if data.get("time") else None,
            metadata={"hn_score": data.get("score", 0), "id": data.get("id")},
        )
    ]

