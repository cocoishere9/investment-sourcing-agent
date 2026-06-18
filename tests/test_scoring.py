import unittest

from sourcing_agent.models import ArtifactType, ProcessedSignal, SourceItem, SourceKind
from sourcing_agent.processors import process_item
from sourcing_agent.scoring.score import score_signal


class ScoringTests(unittest.TestCase):
    def test_company_score_uses_company_rubric_and_contactability(self):
        item = SourceItem(
            source="yc",
            source_kind=SourceKind.WEBPAGE,
            artifact_type=ArtifactType.COMPANY,
            title="Robotics AI Infrastructure",
            url="https://example.com",
            raw_text="YC company building robotics AI infrastructure. Founders: Wei Zhang. Contact founder@example.com. Launch 2026.",
        )
        signal = process_item(item)

        score = score_signal(signal)

        self.assertGreaterEqual(score.raw_score, 70)
        self.assertGreaterEqual(score.outreach_score, 70)
        self.assertGreater(score.breakdown["founder_signal"], 0)

    def test_repo_without_contact_caps_outreach_score(self):
        item = SourceItem(
            source="github",
            source_kind=SourceKind.GITHUB,
            artifact_type=ArtifactType.REPO,
            title="example/inference-runtime",
            url="https://github.com/example/inference-runtime",
            raw_text="AI infrastructure inference runtime with benchmark demo for robotics agents.",
            published_at="2026-06-18T00:00:00Z",
            metadata={"stars": 1800, "forks": 80, "language": "Python", "owner": "example"},
        )
        signal = process_item(item)

        score = score_signal(signal)

        self.assertGreaterEqual(score.raw_score, 70)
        self.assertEqual(score.outreach_score, 50)
        self.assertIn("no_contact_outreach", score.caps_applied)

    def test_pure_wrapper_gets_penalty(self):
        item = SourceItem(
            source="hackernews",
            source_kind=SourceKind.HN,
            artifact_type=ArtifactType.POST,
            title="Launch: pure AI wrapper app",
            url="https://news.ycombinator.com/item?id=1",
            raw_text="Launch: pure AI wrapper app with no technical artifact.",
            metadata={"hn_score": 50},
        )
        signal = process_item(item)

        score = score_signal(signal)

        self.assertIn("pure_wrapper", score.penalties_applied)
        self.assertLess(score.raw_score, 70)


if __name__ == "__main__":
    unittest.main()

