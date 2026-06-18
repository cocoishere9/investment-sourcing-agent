from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from sourcing_agent.db import (
    connect,
    list_processed_signals,
    save_outreach_draft,
    save_processed_signal,
    save_source_item,
)
from sourcing_agent.models import ArtifactType, OutreachDraft, ProcessedSignal, ScoreResult, SourceItem, SourceKind
from sourcing_agent.outputs.digest import render_digest
from sourcing_agent.outputs.outreach import render_outreach
from sourcing_agent.processors import process_item
from sourcing_agent.scoring.score import score_signal


@dataclass
class DailyRunResult:
    source_count: int
    signal_count: int
    draft_count: int
    digest_markdown: str


def sample_items() -> List[SourceItem]:
    return [
        SourceItem(
            source="yc",
            source_kind=SourceKind.WEBPAGE,
            artifact_type=ArtifactType.COMPANY,
            title="Robotics AI Infrastructure",
            url="https://example.com/robotics-ai",
            raw_text="YC company building robotics AI infrastructure. Founders: Wei Zhang. Contact founder@example.com. Launch 2026.",
            published_at="2026-06-18",
        ),
        SourceItem(
            source="github",
            source_kind=SourceKind.GITHUB,
            artifact_type=ArtifactType.REPO,
            title="example/inference-runtime",
            url="https://github.com/example/inference-runtime",
            raw_text="AI infrastructure inference runtime with benchmark demo for robotics agents.",
            published_at="2026-06-18",
            metadata={"stars": 1800, "forks": 80, "language": "Python", "owner": "example"},
        ),
        SourceItem(
            source="arxiv",
            source_kind=SourceKind.ARXIV,
            artifact_type=ArtifactType.PAPER,
            title="Efficient Inference for Robot Fleets",
            url="https://arxiv.org/abs/2606.00001",
            raw_text="We release code and benchmark results for efficient inference deployment in robot fleets.",
            published_at="2026-06-18",
            metadata={"authors": ["A. Researcher"]},
        ),
        SourceItem(
            source="x",
            source_kind=SourceKind.X,
            artifact_type=ArtifactType.POST,
            title="Launch: AI hardware devkit",
            url="https://x.com/i/web/status/1",
            raw_text="Launch: AI hardware devkit for edge inference https://example.com/devkit",
            published_at="2026-06-18",
            metadata={"like_count": 120},
        ),
    ]


def process_and_score_items(items: List[SourceItem]) -> List[Tuple[ProcessedSignal, ScoreResult]]:
    rows = []
    for item in items:
        signal = process_item(item)
        score = score_signal(signal)
        rows.append((signal, score))
    return rows


def has_email_contact(signal: ProcessedSignal) -> bool:
    return any("@" in path for path in signal.contact_paths)


def run_daily(db_path: Path, dry_run: bool = True) -> DailyRunResult:
    conn = connect(db_path)
    items = sample_items() if dry_run else sample_items()
    rows = process_and_score_items(items)
    draft_count = 0

    for item in items:
        save_source_item(conn, item)

    for signal, score in rows:
        save_processed_signal(conn, signal)
        if score.outreach_score >= 75 and has_email_contact(signal):
            draft = render_outreach(signal)
            save_outreach_draft(conn, draft)
            draft_count += 1

    digest = render_digest(rows)
    return DailyRunResult(
        source_count=len(items),
        signal_count=len(rows),
        draft_count=draft_count,
        digest_markdown=digest,
    )


def build_digest_from_db(db_path: Path) -> str:
    conn = connect(db_path)
    signals = list_processed_signals(conn)
    rows = [(signal, score_signal(signal)) for signal in signals]
    return render_digest(rows)


def pending_drafts(db_path: Path) -> List[OutreachDraft]:
    from sourcing_agent.db import list_outreach_drafts

    conn = connect(db_path)
    return [draft for draft in list_outreach_drafts(conn) if not draft.approved]
