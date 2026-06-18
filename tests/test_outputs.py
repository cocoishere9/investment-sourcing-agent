import unittest

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind
from sourcing_agent.outputs.digest import render_digest
from sourcing_agent.outputs.memo import render_memo
from sourcing_agent.outputs.outreach import render_outreach
from sourcing_agent.processors import process_item
from sourcing_agent.scoring.score import score_signal


class OutputTests(unittest.TestCase):
    def test_render_memo_contains_score_and_evidence(self):
        item = SourceItem(
            source="yc",
            source_kind=SourceKind.WEBPAGE,
            artifact_type=ArtifactType.COMPANY,
            title="Robotics AI Infrastructure",
            url="https://example.com",
            raw_text="YC company building robotics AI infrastructure. Founders: Wei Zhang. Contact founder@example.com.",
        )
        signal = process_item(item)
        score = score_signal(signal)

        memo = render_memo(signal, score)

        self.assertIn("Robotics AI Infrastructure", memo)
        self.assertIn("Raw score", memo)
        self.assertIn("https://example.com", memo)

    def test_digest_orders_by_raw_score(self):
        strong_item = SourceItem(
            source="github",
            source_kind=SourceKind.GITHUB,
            artifact_type=ArtifactType.REPO,
            title="Strong Repo",
            url="https://github.com/example/strong",
            raw_text="AI infrastructure runtime benchmark demo.",
            published_at="2026-06-18",
            metadata={"stars": 2000, "owner": "example"},
        )
        weak_item = SourceItem(
            source="x",
            source_kind=SourceKind.X,
            artifact_type=ArtifactType.POST,
            title="Weak Post",
            url="https://x.com/i/web/status/1",
            raw_text="A vague note.",
        )
        strong = process_item(strong_item)
        weak = process_item(weak_item)

        digest = render_digest([(weak, score_signal(weak)), (strong, score_signal(strong))])

        self.assertLess(digest.index("Strong Repo"), digest.index("Weak Post"))

    def test_outreach_has_english_and_chinese_templates(self):
        item = SourceItem(
            source="yc",
            source_kind=SourceKind.WEBPAGE,
            artifact_type=ArtifactType.COMPANY,
            title="Robot AI",
            url="https://example.com",
            raw_text="Robot AI builds infrastructure for China robotics customers. Contact founder@example.com.",
        )
        signal = process_item(item)

        zh = render_outreach(signal, language="zh")
        en = render_outreach(signal, language="en")

        self.assertIn("想就 Robot AI 做一次技术交流", zh.subject)
        self.assertIn("Frontier Bridge Ventures", en.body)
        self.assertIn("前沿桥资本", zh.body)


if __name__ == "__main__":
    unittest.main()

