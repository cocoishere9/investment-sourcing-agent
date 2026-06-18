import unittest

from sourcing_agent.models import ArtifactType, SourceItem, SourceKind
from sourcing_agent.routing import processor_name_for


class RoutingTests(unittest.TestCase):
    def test_processor_name_follows_artifact_type(self):
        cases = [
            (ArtifactType.COMPANY, "company"),
            (ArtifactType.REPO, "repo"),
            (ArtifactType.PAPER, "paper"),
            (ArtifactType.POST, "post"),
        ]

        for artifact_type, expected in cases:
            item = SourceItem(
                source="test",
                source_kind=SourceKind.WEBPAGE,
                artifact_type=artifact_type,
                title="Title",
                url="https://example.com",
                raw_text="Text",
            )
            self.assertEqual(processor_name_for(item), expected)


if __name__ == "__main__":
    unittest.main()

