import unittest

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind
from sourcing_agent.processors import process_item


class ProcessorTests(unittest.TestCase):
    def test_company_processor_extracts_company_specific_fields(self):
        item = SourceItem(
            source="yc",
            source_kind=SourceKind.WEBPAGE,
            artifact_type=ArtifactType.COMPANY,
            title="Robot AI",
            url="https://example.com",
            raw_text="Robot AI builds robotics infrastructure. Founders: Wei Zhang and Anna Smith. Contact founder@example.com.",
        )

        signal = process_item(item)

        self.assertEqual(signal.extracted["company_name"], "Robot AI")
        self.assertEqual(signal.extracted["founders"], ["Wei Zhang", "Anna Smith"])
        self.assertEqual(signal.contact_paths, ["founder@example.com"])
        self.assertEqual(signal.china_affinity, "low")

    def test_repo_processor_extracts_repo_specific_fields(self):
        item = SourceItem(
            source="github",
            source_kind=SourceKind.GITHUB,
            artifact_type=ArtifactType.REPO,
            title="example/inference-runtime",
            url="https://github.com/example/inference-runtime",
            raw_text="Inference runtime with benchmark and demo.",
            metadata={"stars": 1800, "forks": 80, "language": "Python", "owner": "example"},
        )

        signal = process_item(item)

        self.assertEqual(signal.extracted["stars"], 1800)
        self.assertTrue(signal.extracted["has_benchmark"])
        self.assertTrue(signal.extracted["has_demo"])

    def test_paper_processor_extracts_paper_specific_fields(self):
        item = SourceItem(
            source="arxiv",
            source_kind=SourceKind.ARXIV,
            artifact_type=ArtifactType.PAPER,
            title="Efficient Robotics Inference",
            url="https://arxiv.org/abs/2606.00001",
            raw_text="We release code and benchmark results for robot fleets.",
            metadata={"authors": ["A. Researcher"]},
        )

        signal = process_item(item)

        self.assertEqual(signal.extracted["authors"], ["A. Researcher"])
        self.assertTrue(signal.extracted["has_code"])
        self.assertTrue(signal.extracted["has_benchmark"])

    def test_post_processor_extracts_traceable_urls_and_interaction(self):
        item = SourceItem(
            source="x",
            source_kind=SourceKind.X,
            artifact_type=ArtifactType.POST,
            title="Launch: AI hardware devkit",
            url="https://x.com/i/web/status/1",
            raw_text="Launch: AI hardware devkit https://example.com",
            metadata={"like_count": 99},
        )

        signal = process_item(item)

        self.assertEqual(signal.extracted["traceable_urls"], ["https://example.com"])
        self.assertEqual(signal.extracted["interaction_count"], 99)
        self.assertTrue(signal.extracted["is_launch_signal"])


if __name__ == "__main__":
    unittest.main()

