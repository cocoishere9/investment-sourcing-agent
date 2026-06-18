from sourcing_agent.models import ProcessedSignal, SourceItem
from sourcing_agent.processors.common import base_evidence, detect_china_affinity, extract_emails, extract_urls, short_summary


def process_post(item: SourceItem) -> ProcessedSignal:
    text = item.raw_text
    contacts = extract_emails(text)
    urls = extract_urls(text)
    china_affinity, china_reason = detect_china_affinity(text + " " + item.title)
    evidence = base_evidence(item, "social_or_launch_post")
    if china_affinity != "unknown":
        evidence.append({"url": item.url, "reason": china_reason["reason"], "confidence": china_reason["confidence"]})

    interaction_count = int(
        item.metadata.get("like_count", 0)
        or item.metadata.get("hn_score", 0)
        or item.metadata.get("retweet_count", 0)
        or 0
    )

    return ProcessedSignal(
        item=item,
        summary=short_summary(text),
        extracted={
            "traceable_urls": urls,
            "interaction_count": interaction_count,
            "is_launch_signal": "launch" in text.lower(),
        },
        evidence=evidence,
        china_affinity=china_affinity,
        contact_paths=contacts + urls,
    )

