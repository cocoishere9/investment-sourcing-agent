from sourcing_agent.models import ProcessedSignal, SourceItem
from sourcing_agent.processors.common import base_evidence, detect_china_affinity, extract_emails, short_summary


def process_paper(item: SourceItem) -> ProcessedSignal:
    text = item.raw_text
    lowered = text.lower()
    authors = list(item.metadata.get("authors", []))
    contacts = extract_emails(text)
    china_affinity, china_reason = detect_china_affinity(text + " " + " ".join(authors))
    evidence = base_evidence(item, "paper_source")
    if china_affinity != "unknown":
        evidence.append({"url": item.url, "reason": china_reason["reason"], "confidence": china_reason["confidence"]})

    return ProcessedSignal(
        item=item,
        summary=short_summary(text),
        extracted={
            "paper_title": item.title,
            "authors": authors,
            "has_code": "github.com" in lowered or "code" in lowered,
            "has_dataset": "dataset" in lowered,
            "has_benchmark": "benchmark" in lowered,
        },
        evidence=evidence,
        china_affinity=china_affinity,
        contact_paths=contacts,
    )

