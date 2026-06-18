import tempfile
import unittest
from pathlib import Path

from sourcing_agent.db import connect, list_processed_signals, list_source_items, save_processed_signal, save_source_item
from sourcing_agent.models import ArtifactType, ProcessedSignal, SourceItem, SourceKind


class StorageTests(unittest.TestCase):
    def test_save_and_read_source_item_and_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "test.db")
            item = SourceItem(
                source="yc",
                source_kind=SourceKind.WEBPAGE,
                artifact_type=ArtifactType.COMPANY,
                title="Example AI",
                url="https://example.com",
                raw_text="Example AI builds robotics infrastructure.",
            )
            signal = ProcessedSignal(
                item=item,
                summary="Robotics infrastructure company.",
                extracted={"company_name": "Example AI"},
                evidence=[{"url": "https://example.com", "reason": "company website"}],
            )

            save_source_item(conn, item)
            save_processed_signal(conn, signal)

            self.assertEqual(list_source_items(conn)[0].title, "Example AI")
            self.assertEqual(list_processed_signals(conn)[0].extracted["company_name"], "Example AI")


if __name__ == "__main__":
    unittest.main()

