import unittest

from sourcing_agent.models import ArtifactType, ProcessedSignal, SourceItem, SourceKind


class ModelTests(unittest.TestCase):
    def test_source_item_keeps_only_shared_envelope(self):
        item = SourceItem(
            source="github",
            source_kind=SourceKind.GITHUB,
            artifact_type=ArtifactType.REPO,
            title="agent-runtime",
            url="https://github.com/example/agent-runtime",
            raw_text="An agent runtime for inference workflows.",
            metadata={"stars": 1200},
        )

        restored = SourceItem.from_dict(item.to_dict())

        self.assertEqual(restored.artifact_type, ArtifactType.REPO)
        self.assertEqual(restored.metadata["stars"], 1200)

    def test_processed_signal_carries_type_specific_extracted_payload(self):
        item = SourceItem(
            source="arxiv",
            source_kind=SourceKind.ARXIV,
            artifact_type=ArtifactType.PAPER,
            title="Efficient Robotics Inference",
            url="https://arxiv.org/abs/2606.00001",
            raw_text="Paper text",
        )
        signal = ProcessedSignal(
            item=item,
            summary="A paper about robotics inference.",
            extracted={"authors": ["A. Researcher"], "has_code": True},
            evidence=[{"url": item.url, "reason": "paper source"}],
        )

        self.assertEqual(signal.extracted["authors"], ["A. Researcher"])
        self.assertEqual(signal.item.artifact_type, ArtifactType.PAPER)


if __name__ == "__main__":
    unittest.main()

