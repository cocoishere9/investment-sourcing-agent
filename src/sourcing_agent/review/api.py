from pathlib import Path
from typing import List

from sourcing_agent.workflow import pending_drafts


def list_review_queue(db_path: Path) -> List[dict]:
    return [
        {
            "title": draft.signal.item.title,
            "url": draft.signal.item.url,
            "language": draft.language,
            "subject": draft.subject,
            "body": draft.body,
        }
        for draft in pending_drafts(db_path)
    ]

