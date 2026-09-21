# AtlasNorsk daily-news import prompt

Use this when asking an AI to turn a news article into AtlasNorsk content.

## Instruction

Create one AtlasNorsk `newsArticle` JSON resource compatible with:

`schemas/news-article.schema.json`

Write it to:

`content/daily-news/YYYY/MM/YYYY-MM-DD-short-slug.json`

Then add a manifest entry to:

`content/daily-news/manifest.json`

## Learning priorities

1. Preserve the meaning of the article.
2. Produce natural Bokmål, not word-for-word Norwegian.
3. Prefer useful B1/B2 vocabulary over rare trivia.
4. Extract whole semantic units such as `glede seg til`, not meaningless fragments.
5. Mark noun/verb information when useful.
6. Include concise English and French support.
7. Identify only grammar that is genuinely useful to learn from this article.
8. Extract reusable phrases/connectors.
9. Keep explanations compact enough for the AtlasNorsk inspector.
10. Do not invent facts not present in the source.

## Source/copyright handling

Every article **must** declare `rights.storageMode`.

For a normal publisher URL:
- set `rights.storageMode` to `link-only`;
- keep source title, publisher, date and URL;
- do not store publisher source text in `sections[].sourceText`;
- store only AtlasNorsk learning transformations, summaries, vocabulary, grammar and reusable phrases.

If the user supplied the text directly and wants it stored, set `rights.storageMode` to `user-provided`.
Use `licensed` or `public-domain` only when that status is actually known.

## Manifest entry

Add:

```json
{
  "id": "news-YYYY-MM-DD-short-slug",
  "path": "content/daily-news/YYYY/MM/YYYY-MM-DD-short-slug.json",
  "title": "Display title",
  "date": "YYYY-MM-DD",
  "level": "B2",
  "themes": ["society"]
}
```

Newest articles should appear first.
