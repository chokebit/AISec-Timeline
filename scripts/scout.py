#!/usr/bin/env python3
"""Collect candidate AI security events from news feeds.

Fetches a fixed list of security and crypto news feeds, keeps items from the
last few days that mention AI, drops links already in data/events.json or in
earlier scout issues, and prints a Markdown checklist ranked by how likely the
item fits the timeline (money lost, arrests, exploits, breaches).

It never edits data/events.json. Every candidate still needs a human to check
the sources and the AI evidence before it becomes an event.

Usage:
  python3 scripts/scout.py                 # print the checklist
  python3 scripts/scout.py --days 14       # look further back
  python3 scripts/scout.py --issue         # open a GitHub issue (needs GITHUB_TOKEN, GITHUB_REPOSITORY)
"""
import argparse
import datetime as dt
import email.utils
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (AISec-Timeline scout; +https://github.com/chokebit/AISec-Timeline)"
LABEL = "scout"

FEEDS = [
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("SecurityWeek", "https://www.securityweek.com/feed/"),
    ("The Register", "https://www.theregister.com/security/headlines.atom"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("SecurityAffairs", "https://securityaffairs.com/feed"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("Infosecurity Magazine", "https://www.infosecurity-magazine.com/rss/news/"),
    ("The Record", "https://therecord.media/feed"),
    ("CyberScoop", "https://www.cyberscoop.com/feed/"),
    ("Cointelegraph hacks", "https://cointelegraph.com/rss/tag/hacks"),
    ("Web3 is Going Great", "https://www.web3isgoinggreat.com/feed.xml"),
]

# An item must match at least one of these to be a candidate.
AI_TERMS = re.compile(
    r"\bAI\b|\bA\.I\.|artificial intelligence|\bLLMs?\b|large language model|deepfake|deep-fake|"
    r"voice clon|cloned voice|chatbot|ChatGPT|\bGPT-?\d|OpenAI|Anthropic|\bClaude\b|Gemini|Copilot|"
    r"\bagentic\b|AI agent|prompt injection|jailbreak|generative|GenAI|machine learning",
    re.I,
)

# Signals that the story has a concrete event behind it. Weights are rough.
SIGNALS = [
    (3, "money", re.compile(r"[$€£¥]\s?\d|\d\s?(million|billion|crore|won|yuan)\b|stolen|stole|drained|lost|losses", re.I)),
    (3, "fraud", re.compile(r"scam|fraud|swindl|impersonat|extort|ransom", re.I)),
    (2, "law", re.compile(r"arrest|charged|indict|sentenc|convicted|police|court|seized", re.I)),
    (2, "breach", re.compile(r"breach|leak|exfiltrat|compromis|hacked|hack\b|stolen data", re.I)),
    (2, "vuln", re.compile(r"\bCVE-\d|zero-day|0-day|exploit|vulnerabilit|RCE\b", re.I)),
    (2, "malware", re.compile(r"malware|ransomware|infostealer|backdoor|trojan", re.I)),
    (1, "first", re.compile(r"first|record|largest|biggest|unprecedented", re.I)),
]


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"&[#\w]+;", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_feed(raw):
    """Yield (title, link, date, text) from RSS 2.0 or Atom."""
    root = ET.fromstring(raw)
    for el in root.iter():
        name = local(el.tag)
        if name not in ("item", "entry"):
            continue
        f = {}
        link = None
        for c in el:
            n = local(c.tag)
            if n == "link":
                href = c.get("href")
                if href and c.get("rel", "alternate") == "alternate":
                    link = link or href
                elif c.text and c.text.strip():
                    link = link or c.text.strip()
            elif c.text:
                f.setdefault(n, c.text)
        title = strip_html(f.get("title"))
        date = parse_date(f.get("pubDate") or f.get("published") or f.get("updated") or f.get("date"))
        text = strip_html(f.get("description") or f.get("summary") or f.get("content") or "")
        if title and link:
            yield title, link, date, text


def norm(url):
    url = url.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", url).lower()


def known_urls():
    data = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
    return {norm(s["url"]) for e in data["events"] for s in e.get("sources", [])}


def gh(method, path, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
            "Accept": "application/vnd.github+json",
            "User-Agent": UA,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def previous_issue_urls(repo):
    """Links already listed in earlier scout issues, open or closed."""
    seen = set()
    issues = gh("GET", f"/repos/{repo}/issues?labels={LABEL}&state=all&per_page=20")
    for it in issues:
        for u in re.findall(r"\]\((https?://[^)\s]+)\)", it.get("body") or ""):
            seen.add(norm(u))
    return seen


def collect(days, skip):
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    out, failed, seen = [], [], set()
    for source, url in FEEDS:
        try:
            items = list(parse_feed(fetch(url)))
        except Exception as e:  # one broken feed should not stop the run
            failed.append(f"{source} ({type(e).__name__})")
            continue
        for title, link, date, text in items:
            if date and date < since:
                continue
            key = norm(link)
            if key in skip or key in seen:
                continue
            blob = f"{title} {text[:600]}"
            if not AI_TERMS.search(blob):
                continue
            seen.add(key)
            score, tags = 0, []
            for w, tag, rx in SIGNALS:
                if rx.search(blob):
                    score += w
                    tags.append(tag)
            # A title hit counts more than a passing mention in the summary.
            if AI_TERMS.search(title):
                score += 2
            out.append({"title": title, "link": link, "source": source, "date": date, "score": score, "tags": tags})
    out.sort(key=lambda c: (-c["score"], -(c["date"].timestamp() if c["date"] else 0)))
    return out, failed


def render(cands, failed, days, limit):
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d")
    lines = [
        f"Automatic scan of {len(FEEDS)} news feeds for the last {days} days ({today}, UTC+8). "
        "Items mention AI and are not yet in `data/events.json`. Most will not qualify.",
        "",
        "自动扫描结果，只是候选，大多数不会收录。勾选值得查的，核实来源和 AI 证据后再写成事件；不会自动改数据。",
        "",
    ]
    strong = [c for c in cands if c["score"] >= 5][:limit]
    rest = [c for c in cands if c["score"] < 5][: max(0, limit - len(strong))]
    for head, group in (("Likely / 可能相关", strong), ("Weaker signals / 信号较弱", rest)):
        if not group:
            continue
        lines += [f"### {head}", ""]
        for c in group:
            d = c["date"].strftime("%m-%d") if c["date"] else "?"
            tags = ", ".join(c["tags"]) or "ai only"
            title = c["title"].replace("[", "(").replace("]", ")")
            lines.append(f"- [ ] [{title}]({c['link']}) · {c['source']} · {d} · {tags}")
        lines.append("")
    left = len(cands) - len(strong) - len(rest)
    if left > 0:
        lines.append(f"{left} more low-signal items were left out.")
    if failed:
        lines.append("Feeds that failed this run: " + ", ".join(failed))
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=8)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--issue", action="store_true", help="open a GitHub issue instead of printing")
    a = ap.parse_args()

    skip = known_urls()
    repo = os.environ.get("GITHUB_REPOSITORY")
    if a.issue:
        skip |= previous_issue_urls(repo)
    cands, failed = collect(a.days, skip)
    body = render(cands, failed, a.days, a.limit)

    if not a.issue:
        sys.stdout.write(body)
        return
    if not cands:
        print("No new candidates; no issue opened.")
        return
    week = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d")
    it = gh("POST", f"/repos/{repo}/issues", {"title": f"[Scout] Candidate events, week of {week}", "body": body, "labels": [LABEL]})
    print("Opened", it["html_url"])


if __name__ == "__main__":
    main()
