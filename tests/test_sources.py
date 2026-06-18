import json
import unittest

from sourcing_agent.models import ArtifactType
from sourcing_agent.sources.arxiv import parse_arxiv_feed
from sourcing_agent.sources.github import parse_github_search
from sourcing_agent.sources.hn import parse_hn_story
from sourcing_agent.sources.webpage import parse_webpage
from sourcing_agent.sources.x_search import parse_x_recent


class SourceTests(unittest.TestCase):
    def test_parse_github_search_returns_repo_items(self):
        payload = json.dumps(
            {
                "items": [
                    {
                        "full_name": "example/inference-runtime",
                        "html_url": "https://github.com/example/inference-runtime",
                        "description": "Inference runtime for AI agents",
                        "stargazers_count": 1800,
                        "forks_count": 80,
                        "language": "Python",
                        "pushed_at": "2026-06-18T00:00:00Z",
                        "owner": {"login": "example"},
                    }
                ]
            }
        )

        item = parse_github_search(payload)[0]

        self.assertEqual(item.artifact_type, ArtifactType.REPO)
        self.assertEqual(item.metadata["stars"], 1800)

    def test_parse_arxiv_feed_returns_paper_items(self):
        payload = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>https://arxiv.org/abs/2606.00001</id>
            <published>2026-06-18T00:00:00Z</published>
            <title>Efficient Inference for Robotics</title>
            <summary>We study efficient inference for robot fleets.</summary>
            <author><name>A. Researcher</name></author>
          </entry>
        </feed>
        """

        item = parse_arxiv_feed(payload)[0]

        self.assertEqual(item.artifact_type, ArtifactType.PAPER)
        self.assertEqual(item.metadata["authors"], ["A. Researcher"])

    def test_parse_webpage_defaults_to_company(self):
        item = parse_webpage("yc", "https://example.com", "<title>Robot AI</title><p>Company page</p>")[0]

        self.assertEqual(item.artifact_type, ArtifactType.COMPANY)
        self.assertEqual(item.title, "Robot AI")

    def test_parse_x_recent_returns_post_items(self):
        payload = json.dumps({"data": [{"id": "1", "text": "Launch: AI hardware devkit", "public_metrics": {"like_count": 99}}]})

        item = parse_x_recent(payload)[0]

        self.assertEqual(item.artifact_type, ArtifactType.POST)
        self.assertEqual(item.metadata["like_count"], 99)

    def test_parse_hn_story_returns_post_item(self):
        payload = json.dumps({"id": 42, "type": "story", "title": "Launch HN: Robotics AI", "score": 88})

        item = parse_hn_story(payload)[0]

        self.assertEqual(item.artifact_type, ArtifactType.POST)
        self.assertEqual(item.metadata["hn_score"], 88)


if __name__ == "__main__":
    unittest.main()

