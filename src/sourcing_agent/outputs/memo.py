from sourcing_agent.models import ProcessedSignal, ScoreResult


def render_memo(signal: ProcessedSignal, score: ScoreResult) -> str:
    artifact = signal.item.artifact_type.value
    evidence_lines = "\n".join("- {url}: {reason}".format(**item) for item in signal.evidence)
    return "\n".join(
        [
            "# " + signal.item.title,
            "",
            "类型：" + artifact,
            "来源：" + signal.item.source,
            "URL：" + signal.item.url,
            "Raw score：" + str(score.raw_score),
            "Outreach score：" + str(score.outreach_score),
            "置信度：" + score.confidence,
            "",
            "## 一句话总结",
            signal.summary,
            "",
            "## 关键信息",
            str(signal.extracted),
            "",
            "## 证据",
            evidence_lines or "- 暂无证据",
            "",
            "## 建议动作",
            "建议进入人工审核。" if score.raw_score >= 70 else "暂时观察，不建议主动建联。",
        ]
    )

