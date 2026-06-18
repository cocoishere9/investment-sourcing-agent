import tempfile
import unittest
from pathlib import Path

from sourcing_agent.review.api import list_review_queue
from sourcing_agent.workflow import run_daily


class ReviewTests(unittest.TestCase):
    def test_review_queue_lists_generated_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            run_daily(db_path=db_path, dry_run=True)

            queue = list_review_queue(db_path)

            self.assertEqual(len(queue), 1)
            self.assertIn("Robotics AI Infrastructure", queue[0]["title"])
            self.assertIn("Subject", "Subject")


if __name__ == "__main__":
    unittest.main()

