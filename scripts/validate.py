#!/usr/bin/env python3
"""Check data/events.json before it is published."""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "events.json"
DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
CATEGORIES = {"voice", "video", "breach", "market", "aggregate"}
OUTCOMES = {"loss", "blocked", "no_funds", "aggregate"}
EVIDENCE = {"confirmed", "assessed", "self_reported"}
KINDS = {"official", "news", "secondary"}
TEXT = ("title", "amount", "amount_note", "summary", "takeaway_label", "takeaway")


def check(ev):
    errors = []
    if not re.fullmatch(r"[a-z0-9-]+", ev.get("id", "")):
        errors.append("id must be lowercase letters, digits and hyphens")
    if not ev.get("occurred") and not ev.get("disclosed"):
        errors.append("needs occurred or disclosed")
    for key in ("occurred", "disclosed"):
        if ev.get(key) and not DATE.match(ev[key]):
            errors.append(f"{key} must be YYYY, YYYY-MM or YYYY-MM-DD")
    if ev.get("category") not in CATEGORIES:
        errors.append("unknown category")
    if ev.get("outcome") not in OUTCOMES:
        errors.append("unknown outcome")
    if ev.get("ai_evidence") not in EVIDENCE:
        errors.append("unknown ai_evidence")

    usd = ev.get("usd_m", "missing")
    if usd == "missing":
        errors.append("usd_m is required (null when there is no amount)")
    elif ev.get("outcome") in ("loss", "aggregate") and not (isinstance(usd, (int, float)) and usd > 0):
        errors.append("loss and aggregate events need usd_m above 0")
    elif ev.get("outcome") == "blocked" and usd != 0:
        errors.append("blocked events need usd_m of 0")
    elif ev.get("outcome") == "no_funds" and usd is not None:
        errors.append("no_funds events need usd_m of null")

    for lang in ("en", "zh"):
        block = ev.get(lang, {})
        for key in TEXT:
            if not str(block.get(key, "")).strip():
                errors.append(f"{lang}.{key} is empty")

    sources = ev.get("sources", [])
    if not sources:
        errors.append("needs at least one source")
    for src in sources:
        if not str(src.get("url", "")).startswith("https://"):
            errors.append(f"source must use https: {src.get('url')}")
        if src.get("kind") not in KINDS:
            errors.append(f"unknown source kind: {src.get('kind')}")
        if not src.get("name"):
            errors.append("source needs a name")
    return errors


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    failed = False
    seen = set()
    for ev in data["events"]:
        errors = check(ev)
        if ev.get("id") in seen:
            errors.append("duplicate id")
        seen.add(ev.get("id"))
        for err in errors:
            failed = True
            print(f"{ev.get('id', '?')}: {err}")
    if failed:
        sys.exit(1)
    print(f"OK: {len(data['events'])} events")


if __name__ == "__main__":
    main()
