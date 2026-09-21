# AtlasNorsk Content

Content repository for [AtlasNorsk](https://github.com/julian-passebecq/atlasnorsk).

This repository stores **structured Norwegian-learning content**, not application code.

## Structure

```
content/
├── index.json
├── daily-news/
│   └── manifest.json
├── vocabulary/
│   └── manifest.json
├── grammar/
│   └── manifest.json
├── tablebooks/
│   └── manifest.json
├── phrases/
│   └── manifest.json
├── cheatsheets/
│   └── manifest.json
└── courses/
    └── manifest.json

schemas/
└── news-article.schema.json

prompts/
└── DAILY_NEWS_IMPORT.md
```

## Daily workflow

1. Give an AI a news article or article URL.
2. Ask it to follow `prompts/DAILY_NEWS_IMPORT.md`.
3. The AI creates one JSON resource under `content/daily-news/YYYY/MM/`.
4. It adds that resource to `content/daily-news/manifest.json`.
5. AtlasNorsk reads the manifest and displays the new article.

## Copyright/source rule

Do **not** use this public repository as a mirror of publisher articles.

Store:
- source title, publisher, date and URL;
- learning-oriented translations, summaries and notes;
- vocabulary, grammar and useful phrases;
- source text only when it is user-provided, licensed, public-domain, or otherwise appropriate to store.

## Stable contract

Every content resource has a `schemaVersion` and `type`. AtlasNorsk should reject unsupported schema versions rather than silently guessing.

The live content channel is `main`.
