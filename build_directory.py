#!/usr/bin/env python3
"""
build_directory.py — regenerate directory.json from the questions/ folder.

Scans questions/<section>/*.json, reads the tag fields (id, section, module,
topic) out of each question file, and writes directory.json at the repo root.

Run from the repo root before every push:

    python build_directory.py

Idempotent, fast, and validates every file. Never hand-edit directory.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
QUESTIONS = ROOT / "questions"
OUT = ROOT / "directory.json"

VALID_SECTIONS = {"math", "reading-writing"}
REQUIRED_CONTENT = {"stem", "choices", "answer"}


def main():
    if not QUESTIONS.is_dir():
        sys.exit(f"error: no questions/ folder at {QUESTIONS}")

    entries = []
    errors = []
    seen_ids = {}

    # rglob picks up questions/<section>/*.json but NOT images/ (those are .png)
    for path in sorted(QUESTIONS.rglob("*.json")):
        rel = path.relative_to(ROOT)
        try:
            qd = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON ({e})")
            continue

        stem_id = path.stem
        qid = qd.get("id", stem_id)
        if qid != stem_id:
            errors.append(f"{rel}: id '{qid}' != filename '{stem_id}.json'")

        folder_section = path.parent.name
        section = qd.get("section", folder_section)
        if section != folder_section:
            errors.append(f"{rel}: section '{section}' != folder '{folder_section}/'")
        if section not in VALID_SECTIONS:
            errors.append(f"{rel}: section must be one of {sorted(VALID_SECTIONS)}, got '{section}'")
            continue

        module = qd.get("module")
        if module not in (1, 2):
            errors.append(f"{rel}: module must be 1 or 2, got {module!r}")
            continue

        topic = qd.get("topic")
        if not isinstance(topic, str) or not topic.strip():
            errors.append(f"{rel}: topic must be a non-empty string")
            continue

        missing = REQUIRED_CONTENT - qd.keys()
        if missing:
            errors.append(f"{rel}: missing content field(s) {sorted(missing)}")
        elif qd["answer"] not in qd["choices"]:
            errors.append(f"{rel}: answer {qd['answer']!r} not among choices")

        # image, if present, must point at an existing file under images/
        if "image" in qd:
            img = QUESTIONS / section / "images" / qd["image"]
            # We don't fail on a missing PNG (it may be added later), but note it.
            if not img.exists():
                # informational only, not an error
                pass

        if qid in seen_ids:
            errors.append(f"{rel}: duplicate id '{qid}' (also {seen_ids[qid]})")
        seen_ids[qid] = rel

        entries.append({
            "id": qid,
            "section": section,
            "module": module,
            "topic": topic,
        })

    if errors:
        print("Problems found \u2014 directory NOT written:\n", file=sys.stderr)
        for e in errors:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    OUT.write_text(json.dumps(entries, ensure_ascii=False, indent=0), encoding="utf-8")
    n_m = sum(e["section"] == "math" for e in entries)
    n_rw = sum(e["section"] == "reading-writing" for e in entries)
    print(f"Wrote {OUT.name}: {len(entries)} questions ({n_m} math, {n_rw} reading-writing)")

    # list any referenced images that are missing, so you know what to add
    missing_imgs = []
    for path in sorted(QUESTIONS.rglob("*.json")):
        qd = json.loads(path.read_text(encoding="utf-8"))
        if "image" in qd:
            img = QUESTIONS / qd["section"] / "images" / qd["image"]
            if not img.exists():
                missing_imgs.append(f"{qd['section']}/images/{qd['image']}  (for {qd['id']})")
    if missing_imgs:
        print(f"\n{len(missing_imgs)} referenced image(s) not yet added:")
        for m in missing_imgs:
            print("  -", m)


if __name__ == "__main__":
    main()
