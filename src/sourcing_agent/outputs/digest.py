from typing import Iterable, Tuple

from sourcing_agent.models import ProcessedSignal, ScoreResult


def render_digest(rows: Iterable[Tuple[ProcessedSignal, ScoreResult]], limit: int = 20) -> str:
    ordered = sorted(rows, key=lambda row: row[1].raw_score, reverse=True)[:limit]
    lines = ["# 每日 AI 投资 Sourcing Digest", ""]
    for index, (signal, score) in enumerate(ordered, start=1):
        lines.extend(
            [
                "{idx}. [{title}]({url})".format(idx=index, title=signal.item.title, url=signal.item.url),
                "   - 类型：" + signal.item.artifact_type.value,
                "   - 来源：" + signal.item.source,
                "   - Raw score：" + str(score.raw_score) + "，Outreach score：" + str(score.outreach_score),
                "   - 摘要：" + signal.summary,
                "",
            ]
        )
    return "\n".join(lines)

