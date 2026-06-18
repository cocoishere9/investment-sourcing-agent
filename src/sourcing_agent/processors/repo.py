from sourcing_agent.models import ProcessedSignal, SourceItem
from sourcing_agent.processors.common import base_evidence, detect_china_affinity, extract_emails, short_summary


def process_repo(item: SourceItem) -> ProcessedSignal:
    text = item.raw_text
    lowered = text.lower()
    contacts = extract_emails(text)
    china_affinity, china_reason = detect_china_affinity(text + " " + item.title + " " + str(item.metadata.get("owner", "")))
    evidence = base_evidence(item, "github_repository")
    if china_affinity != "unknown":
        evidence.append({"url": item.url, "reason": china_reason["reason"], "confidence": china_reason["confidence"]})

    return ProcessedSignal(
        item=item,
        summary=short_summary(text),
        extracted={
            "repo_name": item.title,
            "stars": int(item.metadata.get("stars", 0) or 0),
            "forks": int(item.metadata.get("forks", 0) or 0),
            "language": item.metadata.get("language"),
            "owner": item.metadata.get("owner"),
            "has_demo": "demo" in lowered,
            "has_benchmark": "benchmark" in lowered,
            "looks_like_wrapper": "wrapper" in lowered and "infrastructure" not in lowered,
        },
        evidence=evidence,
        china_affinity=china_affinity,
        contact_paths=contacts,
    )

