from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_content import validate_news_article


def valid_article():
    return {
        "schemaVersion": 1,
        "type": "newsArticle",
        "id": "news-test",
        "title": "Test article",
        "date": "2026-09-21",
        "level": "B1",
        "themes": ["learning"],
        "source": {
            "title": "Source",
            "publisher": "AtlasNorsk",
            "url": "https://example.com",
            "language": "en",
        },
        "rights": {"storageMode": "public-domain"},
        "sections": [{"id": "s1", "sourceText": "Synthetic.", "norsk": "Syntetisk."}],
        "vocabulary": [],
        "grammar": [],
        "usefulPhrases": [],
    }


class NewsValidationTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("content/daily-news/2026/09/test.json")

    def validate(self, article):
        errors = []
        validate_news_article(self.path, article, errors)
        return errors

    def test_accepts_valid_article(self):
        self.assertEqual(self.validate(valid_article()), [])

    def test_rejects_link_only_source_text(self):
        article = valid_article()
        article["rights"] = {"storageMode": "link-only"}
        errors = self.validate(article)
        self.assertTrue(any("must not mirror source text" in error for error in errors))

    def test_rejects_duplicate_section_ids(self):
        article = valid_article()
        article["sections"].append({"id": "s1", "norsk": "En til."})
        errors = self.validate(article)
        self.assertTrue(any("duplicate id s1" in error for error in errors))

    def test_rejects_bad_cefr(self):
        article = valid_article()
        article["level"] = "B3"
        errors = self.validate(article)
        self.assertTrue(any(".level" in error for error in errors))

    def test_requires_norwegian_section_text(self):
        article = valid_article()
        article["sections"][0]["norsk"] = ""
        errors = self.validate(article)
        self.assertTrue(any(".norsk" in error for error in errors))

    def test_rejects_unsafe_source_protocol(self):
        article = valid_article()
        article["source"]["url"] = "javascript:alert(1)"
        errors = self.validate(article)
        self.assertTrue(any("only http/https URLs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
