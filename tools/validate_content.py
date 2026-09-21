#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

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
for manifest_path in sorted(CONTENT.rglob("manifest.json")):
    manifest = load(manifest_path)
    if manifest.get("schemaVersion") != 1:
        errors.append(f"{manifest_path.relative_to(ROOT)}: unsupported schemaVersion")
    for item in manifest.get("items", []):
        item_id = item.get("id")
        rel = item.get("path")
        if not item_id:
            errors.append(f"{manifest_path.relative_to(ROOT)}: item missing id")
        elif item_id in seen_ids:
            errors.append(f"{manifest_path.relative_to(ROOT)}: duplicate id {item_id}")
        else:
            seen_ids.add(item_id)
        if not rel or not (ROOT / rel).exists():
            errors.append(f"{manifest_path.relative_to(ROOT)}: missing referenced file {rel!r}")

if errors:
    print("\n".join(f"ERROR: {error}" for error in errors))
    raise SystemExit(1)

print(f"AtlasNorsk content OK: {len(seen_ids)} manifested resources")
