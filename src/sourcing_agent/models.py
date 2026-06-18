from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ArtifactType(str, Enum):
    COMPANY = "company"
    REPO = "repo"
    PAPER = "paper"
    POST = "post"


class SourceKind(str, Enum):
    WEBPAGE = "webpage"
    GITHUB = "github"
    ARXIV = "arxiv"
    X = "x"
    HN = "hn"


@dataclass
class SourceItem:
    source: str
    source_kind: SourceKind
    artifact_type: ArtifactType
    title: str
    url: str
    raw_text: str
    published_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source_kind"] = self.source_kind.value
        data["artifact_type"] = self.artifact_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceItem":
        return cls(
            source=data["source"],
            source_kind=SourceKind(data["source_kind"]),
            artifact_type=ArtifactType(data["artifact_type"]),
            title=data["title"],
            url=data["url"],
            raw_text=data.get("raw_text", ""),
            published_at=data.get("published_at"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ProcessedSignal:
    item: SourceItem
    summary: str
    extracted: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    china_affinity: str = "unknown"
    contact_paths: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict(),
            "summary": self.summary,
            "extracted": self.extracted,
            "evidence": self.evidence,
            "china_affinity": self.china_affinity,
            "contact_paths": self.contact_paths,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessedSignal":
        return cls(
            item=SourceItem.from_dict(data["item"]),
            summary=data["summary"],
            extracted=dict(data.get("extracted", {})),
            evidence=list(data.get("evidence", [])),
            china_affinity=data.get("china_affinity", "unknown"),
            contact_paths=list(data.get("contact_paths", [])),
        )


@dataclass
class ScoreResult:
    raw_score: int
    outreach_score: int
    breakdown: Dict[str, int]
    confidence: str
    reasons: List[str]
    caps_applied: List[str] = field(default_factory=list)
    penalties_applied: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OutreachDraft:
    signal: ProcessedSignal
    language: str
    subject: str
    body: str
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal": self.signal.to_dict(),
            "language": self.language,
            "subject": self.subject,
            "body": self.body,
            "approved": self.approved,
        }

