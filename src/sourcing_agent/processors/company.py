import re

from sourcing_agent.models import ProcessedSignal, SourceItem
from sourcing_agent.processors.common import base_evidence, detect_china_affinity, extract_emails, short_summary


FOUNDER_RE = re.compile(r"founders?:\s*([^\.\n]+)", re.IGNORECASE)


def process_company(item: SourceItem) -> ProcessedSignal:
    text = item.raw_text
    founder_match = FOUNDER_RE.search(text)
    founders = []
    if founder_match:
        founders = [name.strip() for name in re.split(r",| and ", founder_match.group(1)) if name.strip()]

    contacts = extract_emails(text)
    china_affinity, china_reason = detect_china_affinity(text + " " + item.title)
    evidence = base_evidence(item, "company_source")
    if china_affinity != "unknown":
        evidence.append({"url": item.url, "reason": china_reason["reason"], "confidence": china_reason["confidence"]})

    return ProcessedSignal(
        item=item,
        summary=short_summary(text),
        extracted={
            "company_name": item.title,
            "founders": founders,
            "has_product_signal": any(word in text.lower() for word in ["build", "platform", "product", "customers", "yc"]),
        },
        evidence=evidence,
        china_affinity=china_affinity,
        contact_paths=contacts,
    )
