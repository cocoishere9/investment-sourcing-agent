import unittest
from pathlib import Path

from sourcing_agent.config import load_scoring_rubrics, load_sources, load_taste_prompt


class ConfigTests(unittest.TestCase):
    def test_load_taste_prompt_thresholds(self):
        taste = load_taste_prompt(Path("."))

        self.assertEqual(taste["thresholds"]["shortlist"], 70)
        self.assertIn("AI infrastructure", taste["preferred_themes"])

    def test_load_scoring_rubrics_by_artifact_type(self):
        rubrics = load_scoring_rubrics(Path("."))

        self.assertEqual(rubrics["company"]["theme_fit"], 20)
        self.assertEqual(rubrics["repo"]["growth_momentum"], 25)

    def test_load_sources(self):
        sources = load_sources(Path("."))

        self.assertEqual(sources["sources"][0]["artifact_type"], "company")
        self.assertEqual(sources["sources"][1]["kind"], "github")


if __name__ == "__main__":
    unittest.main()

