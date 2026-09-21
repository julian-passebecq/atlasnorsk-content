#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ALLOWED_LEVELS = {"A2", "B1", "B2", "C1"}


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_text(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: expected non-empty string")


def validate_date(value: Any, label: str, errors: list[str]) -> None:
    try:
        date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{label}: expected YYYY-MM-DD date")


def is_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_news_article(path: Path, article: Any, errors: list[str]) -> None:
    label = str(path.relative_to(ROOT))
    if not isinstance(article, dict):
        errors.append(f"{label}: article root must be an object")
        return

    if article.get("schemaVersion") != 1:
        errors.append(f"{label}: unsupported schemaVersion")
    if article.get("type") != "newsArticle":
        errors.append(f"{label}: type must be newsArticle")

    for field in ("id", "title"):
        require_text(article.get(field), f"{label}.{field}", errors)

    validate_date(article.get("date"), f"{label}.date", errors)

    if article.get("level") not in ALLOWED_LEVELS:
        errors.append(f"{label}.level: expected one of {sorted(ALLOWED_LEVELS)}")

    themes = article.get("themes")
    if not isinstance(themes, list) or not themes or not all(isinstance(x, str) and x.strip() for x in themes):
        errors.append(f"{label}.themes: expected non-empty string array")

    source = article.get("source")
    if not isinstance(source, dict):
        errors.append(f"{label}.source: expected object")
    else:
        for field in ("title", "publisher", "url", "language"):
            require_text(source.get(field), f"{label}.source.{field}", errors)
        if source.get("url") and not is_http_url(source.get("url")):
            errors.append(f"{label}.source.url: only http/https URLs are allowed")

    rights = article.get("rights") or {}
    storage_mode = rights.get("storageMode")
    if storage_mode not in {None, "link-only", "user-provided", "licensed", "public-domain"}:
        errors.append(f"{label}.rights.storageMode: unsupported value")

    sections = article.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append(f"{label}.sections: expected at least one section")
        sections = []

    section_ids: set[str] = set()
    for index, section in enumerate(sections):
        section_label = f"{label}.sections[{index}]"
        if not isinstance(section, dict):
            errors.append(f"{section_label}: expected object")
            continue
        require_text(section.get("id"), f"{section_label}.id", errors)
        require_text(section.get("norsk"), f"{section_label}.norsk", errors)
        section_id = section.get("id")
        if isinstance(section_id, str):
            if section_id in section_ids:
                errors.append(f"{section_label}.id: duplicate id {section_id}")
            section_ids.add(section_id)
        if storage_mode == "link-only" and section.get("sourceText"):
            errors.append(
                f"{section_label}.sourceText: link-only resources must not mirror source text"
            )

    vocabulary = article.get("vocabulary")
    if not isinstance(vocabulary, list):
        errors.append(f"{label}.vocabulary: expected array")
        vocabulary = []
    for index, entry in enumerate(vocabulary):
        entry_label = f"{label}.vocabulary[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_label}: expected object")
            continue
        for field in ("term", "type", "english", "french"):
            require_text(entry.get(field), f"{entry_label}.{field}", errors)
        if entry.get("level") not in ALLOWED_LEVELS:
            errors.append(f"{entry_label}.level: unsupported CEFR level")

    grammar = article.get("grammar")
    if not isinstance(grammar, list):
        errors.append(f"{label}.grammar: expected array")
        grammar = []
    for index, entry in enumerate(grammar):
        entry_label = f"{label}.grammar[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_label}: expected object")
            continue
        require_text(entry.get("topic"), f"{entry_label}.topic", errors)
        require_text(entry.get("example"), f"{entry_label}.example", errors)

    phrases = article.get("usefulPhrases")
    if not isinstance(phrases, list):
        errors.append(f"{label}.usefulPhrases: expected array")
        phrases = []
    for index, entry in enumerate(phrases):
        entry_label = f"{label}.usefulPhrases[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_label}: expected object")
            continue
        for field in ("norsk", "english", "french"):
            require_text(entry.get(field), f"{entry_label}.{field}", errors)


def validate_manifest(path: Path, manifest: Any, errors: list[str], seen_ids: set[str]) -> int:
    label = str(path.relative_to(ROOT))
    if not isinstance(manifest, dict):
        errors.append(f"{label}: manifest root must be object")
        return 0
    if manifest.get("schemaVersion") != 1:
        errors.append(f"{label}: unsupported schemaVersion")
    if manifest.get("type") != "atlasnorsk-manifest":
        errors.append(f"{label}: unexpected manifest type")
    if not isinstance(manifest.get("items"), list):
        errors.append(f"{label}: items must be an array")
        return 0

    count = 0
    manifest_dates: list[str] = []
    for index, item in enumerate(manifest["items"]):
        item_label = f"{label}.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label}: expected object")
            continue

        item_id = item.get("id")
        rel = item.get("path")
        require_text(item_id, f"{item_label}.id", errors)
        require_text(rel, f"{item_label}.path", errors)

        if isinstance(item_id, str):
            if item_id in seen_ids:
                errors.append(f"{item_label}: duplicate id {item_id}")
            else:
                seen_ids.add(item_id)

        if not isinstance(rel, str) or not rel:
            continue

        if not rel.startswith("content/") or ".." in Path(rel).parts or "://" in rel:
            errors.append(f"{item_label}: unsafe content path {rel!r}")
            continue

        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{item_label}: path escapes repository root")
            continue

        if not target.exists():
            errors.append(f"{item_label}: missing referenced file {rel!r}")
            continue

        resource = load(target)
        if manifest.get("collection") == "daily-news":
            validate_news_article(target, resource, errors)
            if isinstance(resource, dict):
                if resource.get("id") != item_id:
                    errors.append(f"{item_label}: manifest id does not match article id")
                for field in ("title", "date", "level"):
                    if resource.get(field) != item.get(field):
                        errors.append(
                            f"{item_label}.{field}: manifest value does not match article"
                        )
                if resource.get("themes") != item.get("themes"):
                    errors.append(f"{item_label}.themes: manifest value does not match article")
                if isinstance(item.get("date"), str):
                    manifest_dates.append(item["date"])
        count += 1

    if manifest.get("collection") == "daily-news" and manifest_dates != sorted(manifest_dates, reverse=True):
        errors.append(f"{label}: Daily News items must be newest first")

    return count


def main() -> None:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*.json")):
        try:
            load(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")

    index_path = CONTENT / "index.json"
    if index_path.exists():
        index = load(index_path)
        if index.get("schemaVersion") != 1:
            errors.append("content/index.json: unsupported schemaVersion")
        for name, rel in index.get("collections", {}).items():
            target = ROOT / rel
            if not target.exists():
                errors.append(f"content/index.json: missing manifest for {name}: {rel}")

    seen_ids: set[str] = set()
    manifested_resources = 0
    for manifest_path in sorted(CONTENT.rglob("manifest.json")):
        manifested_resources += validate_manifest(
            manifest_path,
            load(manifest_path),
            errors,
            seen_ids,
        )

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        raise SystemExit(1)

    print(f"AtlasNorsk content OK: {manifested_resources} manifested resources")


if __name__ == "__main__":
    main()
