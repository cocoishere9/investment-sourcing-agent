from typing import Any, Dict, List

from sourcing_agent.config import load_scoring_rubrics, load_taste_prompt
from sourcing_agent.models import ArtifactType, ProcessedSignal, ScoreResult


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _text(signal: ProcessedSignal) -> str:
    return " ".join([signal.item.title, signal.item.raw_text, signal.summary]).lower()


def _has_any(text: str, words: List[str]) -> bool:
    return any(word.lower() in text for word in words)


def _has_email_contact(signal: ProcessedSignal) -> bool:
    return any("@" in path for path in signal.contact_paths)


def _theme_fit(signal: ProcessedSignal, weight: int, taste: Dict[str, Any]) -> int:
    return weight if _has_any(_text(signal), taste.get("preferred_themes", [])) else 0


def _china_points(signal: ProcessedSignal, weight: int) -> int:
    if signal.china_affinity == "high":
        return weight
    if signal.china_affinity == "medium":
        return int(weight * 0.7)
    if signal.china_affinity == "low":
        return max(1, int(weight * 0.3))
    return 0


def _score_company(signal: ProcessedSignal, weights: Dict[str, int], taste: Dict[str, Any]) -> Dict[str, int]:
    text = _text(signal)
    extracted = signal.extracted
    return {
        "theme_fit": _theme_fit(signal, weights["theme_fit"], taste),
        "founder_signal": weights["founder_signal"] if extracted.get("founders") else 0,
        "product_clarity": weights["product_clarity"] if extracted.get("has_product_signal") else int(weights["product_clarity"] * 0.5),
        "traction": weights["traction"] if _has_any(text, ["yc", "customer", "revenue", "demo", "invested", "funding"]) else 0,
        "timing": weights["timing"] if _has_any(text, ["launch", "new", "recent", "2026"]) or signal.item.published_at else 0,
        "china_affinity": _china_points(signal, weights["china_affinity"]),
        "contactability": weights["contactability"] if _has_email_contact(signal) else 0,
    }


def _score_repo(signal: ProcessedSignal, weights: Dict[str, int], taste: Dict[str, Any]) -> Dict[str, int]:
    text = _text(signal)
    extracted = signal.extracted
    stars = int(extracted.get("stars", 0))
    if stars >= 1000:
        growth = weights["growth_momentum"]
    elif stars >= 300:
        growth = int(weights["growth_momentum"] * 0.72)
    elif stars >= 100:
        growth = int(weights["growth_momentum"] * 0.4)
    else:
        growth = 0
    return {
        "growth_momentum": growth,
        "maintenance": weights["maintenance"] if signal.item.published_at else int(weights["maintenance"] * 0.5),
        "technical_depth": weights["technical_depth"] if extracted.get("has_benchmark") or _has_any(text, ["runtime", "inference", "scheduler", "compiler"]) else 0,
        "commercialization": weights["commercialization"] if _has_any(text, ["platform", "infra", "enterprise", "agents", "robotics", "hardware"]) else 0,
        "maintainer_credibility": weights["maintainer_credibility"] if extracted.get("owner") else 0,
        "theme_fit": _theme_fit(signal, weights["theme_fit"], taste),
        "contactability": weights["contactability"] if _has_email_contact(signal) else 0,
    }


def _score_paper(signal: ProcessedSignal, weights: Dict[str, int], taste: Dict[str, Any]) -> Dict[str, int]:
    text = _text(signal)
    extracted = signal.extracted
    return {
        "novelty": weights["novelty"] if _has_any(text, ["new", "novel", "efficient", "benchmark", "state-of-the-art"]) else int(weights["novelty"] * 0.4),
        "commercialization": weights["commercialization"] if _has_any(text, ["robotics", "inference", "hardware", "platform", "deployment", "enterprise"]) else 0,
        "author_credibility": weights["author_credibility"] if extracted.get("authors") else 0,
        "implementation": weights["implementation"] if extracted.get("has_code") or extracted.get("has_benchmark") else 0,
        "theme_fit": _theme_fit(signal, weights["theme_fit"], taste),
        "freshness": weights["freshness"] if signal.item.published_at else 0,
        "china_affinity": _china_points(signal, weights["china_affinity"]),
    }


def _score_post(signal: ProcessedSignal, weights: Dict[str, int], taste: Dict[str, Any]) -> Dict[str, int]:
    text = _text(signal)
    extracted = signal.extracted
    interactions = int(extracted.get("interaction_count", 0))
    if interactions >= 100:
        interaction_score = weights["interaction_quality"]
    elif interactions >= 30:
        interaction_score = int(weights["interaction_quality"] * 0.65)
    else:
        interaction_score = int(weights["interaction_quality"] * 0.25)
    return {
        "signal_quality": weights["signal_quality"] if extracted.get("is_launch_signal") or _has_any(text, ["founder", "built", "demo"]) else int(weights["signal_quality"] * 0.4),
        "interaction_quality": interaction_score,
        "traceability": weights["traceability"] if extracted.get("traceable_urls") else 0,
        "freshness": weights["freshness"] if signal.item.published_at or _has_any(text, ["launch", "today", "new"]) else 0,
        "theme_fit": _theme_fit(signal, weights["theme_fit"], taste),
        "contact_path": weights["contact_path"] if signal.contact_paths else 0,
    }


def score_signal(signal: ProcessedSignal, taste: Dict[str, Any] = None, rubrics: Dict[str, Any] = None) -> ScoreResult:
    taste = taste or load_taste_prompt()
    rubrics = rubrics or load_scoring_rubrics()
    artifact_type = signal.item.artifact_type
    if artifact_type == ArtifactType.COMPANY:
        breakdown = _score_company(signal, rubrics["company"], taste)
    elif artifact_type == ArtifactType.REPO:
        breakdown = _score_repo(signal, rubrics["repo"], taste)
    elif artifact_type == ArtifactType.PAPER:
        breakdown = _score_paper(signal, rubrics["paper"], taste)
    elif artifact_type == ArtifactType.POST:
        breakdown = _score_post(signal, rubrics["post"], taste)
    else:
        breakdown = {}

    reasons: List[str] = []
    caps_applied: List[str] = []
    penalties_applied: List[str] = []
    raw_score = sum(breakdown.values())
    text = _text(signal)

    if not signal.item.url:
        raw_score = min(raw_score, int(rubrics["caps"]["no_url"]))
        caps_applied.append("no_url")
    if artifact_type == ArtifactType.POST and not signal.extracted.get("traceable_urls"):
        raw_score = min(raw_score, int(rubrics["caps"]["post_without_traceable_entity"]))
        caps_applied.append("post_without_traceable_entity")
    if _has_any(text, ["pure ai wrapper", "wrapper app", "thin wrapper"]):
        raw_score -= int(rubrics["penalties"]["pure_wrapper"])
        penalties_applied.append("pure_wrapper")
    if _has_any(text, ["series c", "series d", "ipo", "public company"]):
        raw_score -= int(rubrics["penalties"]["too_late_stage"])
        penalties_applied.append("too_late_stage")

    raw_score = _clamp(raw_score)
    outreach_score = raw_score
    if not _has_email_contact(signal):
        outreach_score = min(outreach_score, int(rubrics["caps"]["no_contact_outreach"]))
        caps_applied.append("no_contact_outreach")
    if not signal.evidence:
        outreach_score = min(outreach_score, 50)
        caps_applied.append("no_evidence")

    if raw_score >= int(taste["thresholds"]["shortlist"]):
        reasons.append("shortlist_threshold_met")
    if outreach_score >= int(taste["thresholds"]["draft_outreach"]):
        reasons.append("outreach_threshold_met")

    positive_parts = len([value for value in breakdown.values() if value > 0])
    confidence = "high" if positive_parts >= 5 else "medium" if positive_parts >= 3 else "low"

    return ScoreResult(
        raw_score=raw_score,
        outreach_score=_clamp(outreach_score),
        breakdown=breakdown,
        confidence=confidence,
        reasons=reasons,
        caps_applied=caps_applied,
        penalties_applied=penalties_applied,
    )
