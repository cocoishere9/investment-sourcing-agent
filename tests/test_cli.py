import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sourcing_agent.cli import main
from sourcing_agent.scheduler import codex_automation_prompt, daily_command


class CliTests(unittest.TestCase):
    def test_run_daily_cli_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["run-daily", "--dry-run", "--db", str(Path(tmp) / "test.db")])

            self.assertEqual(code, 0)
            self.assertIn("采集条数: 4", output.getvalue())
            self.assertIn("生成草稿: 1", output.getvalue())

    def test_review_queue_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            main(["run-daily", "--dry-run", "--db", str(db_path)])
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["review-queue", "--db", str(db_path)])

            self.assertEqual(code, 0)
            self.assertIn("Robotics AI Infrastructure", output.getvalue())

    def test_scheduler_describes_reusable_command(self):
        self.assertIn("run-daily", daily_command())
        self.assertIn("human approval", codex_automation_prompt())


if __name__ == "__main__":
    unittest.main()

