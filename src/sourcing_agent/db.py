import json
import sqlite3
from pathlib import Path
from typing import List

from sourcing_agent.models import OutreachDraft, ProcessedSignal, SourceItem


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS source_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            artifact_type TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            artifact_type TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS outreach_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            language TEXT NOT NULL,
            approved INTEGER NOT NULL DEFAULT 0,
            payload TEXT NOT NULL,
            UNIQUE(url, language)
        )
        """
    )
    conn.commit()


def save_source_item(conn: sqlite3.Connection, item: SourceItem) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO source_items (source, url, artifact_type, payload)
        VALUES (?, ?, ?, ?)
        """,
        (item.source, item.url, item.artifact_type.value, json.dumps(item.to_dict())),
    )
    conn.commit()


def list_source_items(conn: sqlite3.Connection) -> List[SourceItem]:
    rows = conn.execute("SELECT payload FROM source_items ORDER BY id").fetchall()
    return [SourceItem.from_dict(json.loads(row["payload"])) for row in rows]


def save_processed_signal(conn: sqlite3.Connection, signal: ProcessedSignal) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO processed_signals (url, artifact_type, payload)
        VALUES (?, ?, ?)
        """,
        (
            signal.item.url,
            signal.item.artifact_type.value,
            json.dumps(signal.to_dict()),
        ),
    )
    conn.commit()


def list_processed_signals(conn: sqlite3.Connection) -> List[ProcessedSignal]:
    rows = conn.execute("SELECT payload FROM processed_signals ORDER BY id").fetchall()
    return [ProcessedSignal.from_dict(json.loads(row["payload"])) for row in rows]


def save_outreach_draft(conn: sqlite3.Connection, draft: OutreachDraft) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO outreach_drafts (url, language, approved, payload)
        VALUES (?, ?, ?, ?)
        """,
        (
            draft.signal.item.url,
            draft.language,
            1 if draft.approved else 0,
            json.dumps(draft.to_dict()),
        ),
    )
    conn.commit()


def list_outreach_drafts(conn: sqlite3.Connection) -> List[OutreachDraft]:
    rows = conn.execute("SELECT payload FROM outreach_drafts ORDER BY id").fetchall()
    drafts = []
    for row in rows:
        data = json.loads(row["payload"])
        drafts.append(
            OutreachDraft(
                signal=ProcessedSignal.from_dict(data["signal"]),
                language=data["language"],
                subject=data["subject"],
                body=data["body"],
                approved=bool(data.get("approved", False)),
            )
        )
    return drafts
