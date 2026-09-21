from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_content import ROOT, find_unmanifested_json, is_safe_manifest_path, validate_news_article


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
        self.path = ROOT / "content/daily-news/2026/09/test.json"

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

    def test_daily_news_manifest_path_stays_inside_daily_news_collection(self):
        self.assertTrue(
            is_safe_manifest_path(
                "daily-news",
                "content/daily-news/2026/09/article.json",
            )
        )
        self.assertFalse(
            is_safe_manifest_path(
                "daily-news",
                "content/grammar/article.json",
            )
        )
        self.assertFalse(
            is_safe_manifest_path(
                "daily-news",
                "content/daily-news/../grammar/article.json",
            )
        )

    def test_detects_unmanifested_json_resources(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_name:
            temp_root = Path(temp_name)
            collection = temp_root / "content" / "daily-news"
            collection.mkdir(parents=True)
            article = collection / "article.json"
            article.write_text("{}", encoding="utf-8")

            manifest = {"items": []}
            self.assertEqual(
                find_unmanifested_json(collection, manifest, root=temp_root),
                ["content/daily-news/article.json"],
            )

            manifest["items"] = [
                {
                    "id": "article",
                    "path": "content/daily-news/article.json",
                }
            ]
            self.assertEqual(
                find_unmanifested_json(collection, manifest, root=temp_root),
                [],
            )


if __name__ == "__main__":
    unittest.main()
