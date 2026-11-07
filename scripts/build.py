#!/usr/bin/env python3
"""Build the site into _site/ from data/events.json and site/.

    python3 scripts/build.py            # pages + artwork (needs Playwright)
    python3 scripts/build.py --no-art   # pages only; the gallery draws missing art live

Change SITE_URL when the site moves to its own domain.
"""
import base64
import html
import json
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

SITE_URL = os.environ.get("SITE_URL", "https://chokebit.github.io/AISec-Timeline").rstrip("/")
REPO = "https://github.com/chokebit/AISec-Timeline"

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
OUT = ROOT / "_site"
LANGS = ("en", "zh")
HREFLANG = {"en": "en", "zh": "zh-Hans"}
HTML_LANG = {"en": "en", "zh": "zh-CN"}
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&family=Noto+Sans+SC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />'
)

T = {
    "en": {
        "site": "AI Chaotic Era",
        "home_title": "AI Chaotic Era: major security events of the AI era",
        "home_desc": "A sourced timeline of major security events in the AI era: the biggest losses, turning points such as autonomous AI attacks, and the human role in each one.",
        "all": "All events", "submit": "Submit an event", "fix": "Report a correction", "gallery": "View in the gallery",
        "human": "Where the humans were", "trace": "Attack trace", "sources": "Sources",
        "occurred": "Occurred ", "disclosed": "Disclosed ",
        "prev": "Previous", "next": "Next",
        "list_intro": "{n} events, updated {d}. Every entry grades the evidence for AI and says what people did. ",
        "data": "Download the data (JSON)", "search": "Search events, places, companies", "all_types": "All types", "all_ev": "Any evidence",
        "count": "{n} shown", "empty": "Nothing matches. Try fewer words, or tell us what is missing.",
        "foot": "Data and text CC BY 4.0, code MIT. This project summarizes public reporting. It is not legal, financial or security advice, and allegations remain unproven until a court decides.",
        "notfound": "This page does not exist.", "back": "Back to the gallery",
        "ev": {"confirmed": "AI confirmed", "assessed": "AI assessed", "self_reported": "AI self-reported", "unknown": "AI role unknown"},
        "kind": {"official": "primary", "news": "news", "secondary": "secondary"},
        "cat": {"voice": "Voice clone", "video": "Deepfake video", "breach": "Breach", "market": "Fake media", "aggregate": "Annual figure",
                "autonomous": "Autonomous attack", "theft": "Theft", "supply": "Supply chain", "vuln": "Vulnerability discovery", "malware": "AI malware"},
    },
    "zh": {
        "site": "AI 乱纪元",
        "home_title": "AI 乱纪元：AI 时代安全大事件",
        "home_desc": "AI 时代安全大事件时间线：金额最大的案件、AI 自主攻击这类转折点，每一条都有来源，并写明人在其中做了什么。",
        "all": "全部事件", "submit": "提交事件", "fix": "纠错", "gallery": "在展馆中查看",
        "human": "人在哪里", "trace": "攻击链路", "sources": "来源",
        "occurred": "发生 ", "disclosed": "披露 ",
        "prev": "上一条", "next": "下一条",
        "list_intro": "共 {n} 条，更新于 {d}。每一条都标明 AI 参与的证据强弱，并写清人做了什么。",
        "data": "下载数据（JSON）", "search": "搜索事件、地区、公司", "all_types": "全部类型", "all_ev": "全部证据",
        "count": "显示 {n} 条", "empty": "没有匹配的事件。少输几个词试试，或者告诉我们缺了什么。",
        "foot": "数据和文字采用 CC BY 4.0，代码采用 MIT。本站整理公开报道，不构成法律、财务或安全建议；嫌疑人在法院判决前均未被定罪。",
        "notfound": "这个页面不存在。", "back": "回到展馆",
        "ev": {"confirmed": "AI 已确认", "assessed": "AI 研判", "self_reported": "AI 自报", "unknown": "AI 参与未明"},
        "kind": {"official": "一手", "news": "新闻", "secondary": "二手"},
        "cat": {"voice": "声音克隆", "video": "深伪视频", "breach": "入侵与泄露", "market": "虚假信息", "aggregate": "年度统计",
                "autonomous": "自主攻击", "theft": "盗窃", "supply": "供应链", "vuln": "漏洞发现", "malware": "AI 恶意软件"},
    },
}

e_ = html.escape


def sort_date(ev):
    return ev["occurred"] or ev["disclosed"]


def ordered(events):
    return sorted(events, key=lambda ev: (sort_date(ev), ev["disclosed"] or ""))


def tone(ev):
    return {"loss": "loss", "blocked": "blocked"}.get(ev["outcome"], "other")


def date_text(d, lang):
    p = d.split("-")
    if lang == "zh":
        return p[0] + " 年" + (f" {int(p[1])} 月" if len(p) > 1 else "") + (f" {int(p[2])} 日" if len(p) > 2 else "")
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return (f"{int(p[2])} " if len(p) > 2 else "") + (months[int(p[1]) - 1] + " " if len(p) > 1 else "") + p[0]


def date_line(ev, lang):
    t, out = T[lang], []
    if ev["occurred"]:
        out.append(t["occurred"] + date_text(ev["occurred"], lang))
    if ev["disclosed"] and ev["disclosed"] != ev["occurred"]:
        out.append(t["disclosed"] + date_text(ev["disclosed"], lang))
    return " · ".join(out)


def clip(text, lang):
    """Meta description: whole sentences up to about 160 characters (90 in Chinese)."""
    limit = 90 if lang == "zh" else 160
    if len(text) <= limit:
        return text
    stops = "。；" if lang == "zh" else ".;"
    cut = max(text.rfind(s, 0, limit) for s in stops)
    return text[: cut + 1] if cut > limit // 3 else text[: limit - 1].rstrip() + "…"


def rel_root(path):
    return "../" * path.count("/")


def path_for(kind, lang, ev=None):
    prefix = "zh/" if lang == "zh" else ""
    return prefix + {"home": "", "list": "events/", "event": f"events/{ev['id'] if ev else ''}/"}[kind]


def url(path):
    return f"{SITE_URL}/{path}"


def seo_head(lang, title, desc, paths, image, og_type="website", ld=None):
    out = [
        f"<title>{e_(title)}</title>",
        f'<meta name="description" content="{e_(desc)}" />',
        f'<link rel="canonical" href="{url(paths[lang])}" />',
    ]
    out += [f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{url(paths[l])}" />' for l in LANGS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{url(paths["en"])}" />')
    out += [
        f'<meta property="og:type" content="{og_type}" />',
        f'<meta property="og:site_name" content="{e_(T[lang]["site"])}" />',
        f'<meta property="og:title" content="{e_(title)}" />',
        f'<meta property="og:description" content="{e_(desc)}" />',
        f'<meta property="og:url" content="{url(paths[lang])}" />',
        f'<meta property="og:image" content="{url(image)}" />',
        f'<meta property="og:locale" content="{"zh_CN" if lang == "zh" else "en_US"}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
    ]
    if ld:
        out.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n    ".join(out)


def page(lang, path, head, body):
    root = rel_root(path)
    return f"""<!doctype html>
<html lang="{HTML_LANG[lang]}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="color-scheme" content="dark" />
    <meta name="theme-color" content="#08080b" />
    <link rel="icon" href="data:," />
    {head}
    {FONTS}
    <link rel="stylesheet" href="{root}site.css" />
  </head>
  <body>
{body}
    <script>
      document.addEventListener("click", function (e) {{
        var a = e.target.closest("[data-lang]");
        if (a) try {{ localStorage.setItem("aisec-lang", a.getAttribute("data-lang")); }} catch (err) {{}}
      }});
    </script>
  </body>
</html>
"""


def bar(lang, path, other_paths):
    t, root = T[lang], rel_root(path)
    home = root + path_for("home", lang) or "./"
    langs = "".join(
        f'<a href="{root + other_paths[l] or "./"}" data-lang="{l}" hreflang="{HREFLANG[l]}" aria-current="{str(l == lang).lower()}">{"中文" if l == "zh" else "EN"}</a>'
        for l in ("zh", "en")
    )
    return f"""    <header class="bar">
      <a class="mark" href="{home}">{e_(t["site"])}</a>
      <nav class="top-r">
        <a href="{root + path_for("list", lang)}">{e_(t["all"])}</a>
        <a class="wide" href="{REPO}/issues/new?template=new-event.yml" target="_blank" rel="noopener noreferrer">{e_(t["submit"])} ↗</a>
        <span class="sep"></span>{langs}
      </nav>
    </header>"""


def footer(lang, path, updated):
    t, root = T[lang], rel_root(path)
    return f"""    <footer class="foot">
      {e_(t["site"])} · {e_(updated)} · <a href="{root}data/events.json">events.json</a> · <a href="{REPO}" target="_blank" rel="noopener noreferrer">GitHub</a><br />
      {e_(t["foot"])}
    </footer>"""


def event_page(ev, lang, prev, nxt, updated):
    t, l = T[lang], ev[lang]
    path = path_for("event", lang, ev)
    root = rel_root(path)
    paths = {x: path_for("event", x, ev) for x in LANGS}
    plate_date = ".".join(sort_date(ev).split("-")[:2])
    sources = "".join(
        f'<li><a href="{e_(s["url"])}" target="_blank" rel="noopener noreferrer">{e_(s["name"])} ↗</a> <small>{e_(t["kind"][s["kind"]])}</small></li>'
        for s in ev["sources"]
    )
    steps = "".join(f"<li>{e_(s)}</li>" for s in l["steps"])

    def card(other, cls, label):
        if not other:
            return ""
        return (f'<a class="{cls}" href="{root + path_for("event", lang, other)}"><img src="{root}art/{other["id"]}-t.webp" width="256" height="128" alt="" loading="lazy" />'
                f'<span><small>{label}</small>{e_(other[lang]["short"])}</span></a>')

    ld = {
        "@context": "https://schema.org", "@type": "Article", "headline": l["title"], "description": clip(l["summary"], lang),
        "image": url(f"art/{ev['id']}.jpg"), "inLanguage": HTML_LANG[lang], "dateModified": updated, "url": url(path),
        "isPartOf": {"@type": "Dataset", "name": "AI Chaotic Era", "url": url("")},
        "citation": [s["url"] for s in ev["sources"]],
    }
    head = seo_head(lang, f'{l["title"]} · {t["site"]}', clip(l["summary"], lang), paths, f"art/{ev['id']}.jpg", "article", ld)
    body = f"""{bar(lang, path, paths)}
    <main class="wrap">
      <div class="ev">
        <figure class="art {tone(ev)}">
          <div class="piece">
            <img src="{root}art/{ev["id"]}.webp" width="960" height="690" alt="{e_(l.get("art_note", l["short"]))}" />
            <div class="tag"><b class="{"long" if ev["usd_m"] is None else ""}">{e_(l["amount"])}</b></div>
            <div class="plate"><b>{e_(ev["plate"])}</b><span>{e_(plate_date)}</span></div>
          </div>
          {f'<figcaption class="cap">{e_(l["art_note"])}</figcaption>' if l.get("art_note") else ""}
        </figure>
        <article class="text">
          <div class="meta"><span>{e_(date_line(ev, lang))}</span><em class="{ev["ai_evidence"]}">{e_(t["ev"][ev["ai_evidence"]])}</em><span>{e_(t["cat"][ev["category"]])}</span></div>
          <h1>{e_(l["title"])}</h1>
          <div class="note">{e_(l["amount_note"])}</div>
          <div class="human"><b>{e_(t["human"])}</b>{e_(l["human_role"])}</div>
          <p class="sum">{e_(l["summary"])}</p>
          <h2>{e_(t["trace"])}</h2>
          <ol>{steps}</ol>
          <h2>{e_(l["takeaway_label"])}</h2>
          <p class="take">{e_(l["takeaway"])}</p>
          <h2>{e_(t["sources"])}</h2>
          <ol class="src">{sources}</ol>
          <div class="acts">
            <a href="{root + path_for("home", lang) or "./"}#{ev["id"]}">{e_(t["gallery"])} →</a>
            <a href="{REPO}/issues/new?template=correction.yml&amp;event={quote(ev["id"])}" target="_blank" rel="noopener noreferrer">{e_(t["fix"])} ↗</a>
          </div>
        </article>
      </div>
      <nav class="pn">{card(prev, "prev", "← " + t["prev"])}{card(nxt, "next", t["next"] + " →")}</nav>
    </main>
{footer(lang, path, updated)}"""
    return path, page(lang, path, head, body)


def list_page(events, lang, updated):
    t = T[lang]
    path = path_for("list", lang)
    root = rel_root(path)
    paths = {x: path_for("list", x) for x in LANGS}
    newest = list(reversed(ordered(events)))
    cats = [c for c in t["cat"] if any(ev["category"] == c for ev in events)]
    rows = []
    for ev in newest:
        l = ev[lang]
        hay = " ".join([l["short"], l["title"], l["summary"], l["human_role"], ev["plate"], ev["id"], t["cat"][ev["category"]]]).lower()
        rows.append(
            f'<li><a class="row {tone(ev)}" href="{ev["id"]}/" data-cat="{ev["category"]}" data-ev="{ev["ai_evidence"]}" data-q="{e_(hay)}">'
            f'<img src="{root}art/{ev["id"]}-t.webp" width="256" height="128" alt="" loading="lazy" />'
            f'<div><span class="d">{e_(date_text(sort_date(ev), lang))} · {e_(t["cat"][ev["category"]])}</span><span class="t">{e_(l["title"])}</span><span class="h">{e_(l["human_role"])}</span></div>'
            f'<div class="a">{e_(l["amount"])}<em>{e_(t["ev"][ev["ai_evidence"]])}</em></div></a></li>'
        )
    chips_cat = f'<button type="button" data-v="" aria-pressed="true">{e_(t["all_types"])}</button>' + "".join(
        f'<button type="button" data-v="{c}" aria-pressed="false">{e_(t["cat"][c])}</button>' for c in cats)
    chips_ev = f'<button type="button" data-v="" aria-pressed="true">{e_(t["all_ev"])}</button>' + "".join(
        f'<button type="button" data-v="{k}" aria-pressed="false">{e_(v)}</button>' for k, v in t["ev"].items())
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": url(path_for("event", lang, ev)), "name": ev[lang]["title"]} for i, ev in enumerate(newest)]}
    head = seo_head(lang, f'{t["all"]} · {t["site"]}', t["home_desc"], paths, "art/cover.jpg", ld=ld)
    body = f"""{bar(lang, path, paths)}
    <main class="wrap">
      <section class="head">
        <h1>{e_(t["all"])}</h1>
        <p>{e_(t["list_intro"].format(n=len(events), d=updated))}<a href="{root}data/events.json">{e_(t["data"])}</a> · <a href="{REPO}/issues/new?template=new-event.yml" target="_blank" rel="noopener noreferrer">{e_(t["submit"])} ↗</a></p>
      </section>
      <div class="tools" id="tools" hidden>
        <input id="q" type="search" placeholder="{e_(t["search"])}" aria-label="{e_(t["search"])}" autocomplete="off" />
        <div class="chips" data-key="cat">{chips_cat}</div>
        <div class="chips" data-key="ev">{chips_ev}</div>
        <div class="count" id="count" data-tpl="{e_(t["count"])}"></div>
      </div>
      <ol class="rows">{"".join(rows)}</ol>
      <p class="empty" id="empty" hidden>{e_(t["empty"])}</p>
    </main>
{footer(lang, path, updated)}
    <script src="{root}list.js"></script>"""
    return path, page(lang, path, head, body)


def gallery_page(data, lang):
    t = T[lang]
    path = path_for("home", lang)
    root = rel_root(path)
    paths = {x: path_for("home", x) for x in LANGS}
    ld = {
        "@context": "https://schema.org", "@type": "Dataset", "name": "AI Chaotic Era", "alternateName": "AI 乱纪元",
        "description": T["en"]["home_desc"], "url": url(""), "license": "https://creativecommons.org/licenses/by/4.0/",
        "creator": {"@type": "Person", "name": "chokebit", "url": "https://github.com/chokebit"},
        "dateModified": data["updated"], "inLanguage": ["en", "zh-CN"], "isAccessibleForFree": True,
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": url("data/events.json")}],
    }
    head = seo_head(lang, t["home_title"], t["home_desc"], paths, "art/cover.jpg", ld=ld)
    boot = json.dumps({"lang": lang, "root": root, "data": data}, ensure_ascii=False).replace("</", "<\\/")
    src = (SRC / "index.html").read_text(encoding="utf-8")
    for marker, value in (("<!--HEAD-->", head), ("<!--LANG-->", HTML_LANG[lang]), ("<!--ROOT-->", root), ("/*BOOT*/null", boot)):
        assert marker in src, marker
        src = src.replace(marker, value)
    return path, src


def not_found():
    base = urlparse(SITE_URL).path.rstrip("/") + "/"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex" />
    <title>404 · AI Chaotic Era</title>
    <link rel="stylesheet" href="{base}site.css" />
  </head>
  <body>
    <main class="wrap head">
      <h1>404</h1>
      <p>{T["en"]["notfound"]} <a href="{base}">{T["en"]["back"]}</a></p>
      <p>{T["zh"]["notfound"]} <a href="{base}zh/">{T["zh"]["back"]}</a></p>
    </main>
  </body>
</html>
"""


def sitemap(events, updated):
    groups = [{l: path_for("home", l) for l in LANGS}, {l: path_for("list", l) for l in LANGS}]
    groups += [{l: path_for("event", l, ev) for l in LANGS} for ev in ordered(events)]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for g in groups:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG[l]}" href="{url(g[l])}"/>' for l in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{url(g["en"])}"/>'
        for l in LANGS:
            out.append(f"  <url><loc>{url(g[l])}</loc><lastmod>{updated}</lastmod>{alts}</url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def render_art(events, art_dir):
    """Draw every event with site/art.js in headless Chromium and save the images."""
    from playwright.sync_api import sync_playwright

    art_dir.mkdir(parents=True, exist_ok=True)
    script = """(ev) => {
      const full = document.createElement("canvas"); full.width = 960; full.height = 690;
      if (ev) AISecArt.draw(full, ev); else AISecArt.cover(full);
      const th = document.createElement("canvas"); th.width = 256; th.height = 128;
      const h = 960 * 128 / 256;
      th.getContext("2d").drawImage(full, 0, (690 - h) / 2, 960, h, 0, 0, 256, 128);
      return [full.toDataURL("image/webp", 0.9), th.toDataURL("image/webp", 0.85), full.toDataURL("image/jpeg", 0.88)];
    }"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        pg.set_content("<!doctype html><script>" + (SRC / "art.js").read_text(encoding="utf-8") + "</script>")
        for ev in [None] + events:
            name = ev["id"] if ev else "cover"
            for suffix, data_url in zip(("webp", "t.webp", "jpg"), pg.evaluate(script, ev)):
                head, b64 = data_url.split(",", 1)
                expected = "image/jpeg" if suffix == "jpg" else "image/webp"
                if expected not in head:
                    sys.exit(f"Chromium could not encode {expected}")
                (art_dir / (f"{name}-t.webp" if suffix == "t.webp" else f"{name}.{suffix}")).write_bytes(base64.b64decode(b64))
        browser.close()
    print(f"art: {len(events) + 1} images")


def main():
    data = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
    events, updated = data["events"], data["updated"]
    keep_art = (OUT / "art").exists() and "--no-art" in sys.argv
    if OUT.exists():
        for child in OUT.iterdir():
            if keep_art and child.name == "art":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    OUT.mkdir(exist_ok=True)

    files = {}
    for lang in LANGS:
        path, doc = gallery_page(data, lang)
        files[path + "index.html"] = doc
        path, doc = list_page(events, lang, updated)
        files[path + "index.html"] = doc
        seq = ordered(events)
        for i, ev in enumerate(seq):
            path, doc = event_page(ev, lang, seq[i - 1] if i else None, seq[i + 1] if i + 1 < len(seq) else None, updated)
            files[path + "index.html"] = doc
    files["404.html"] = not_found()
    files["sitemap.xml"] = sitemap(events, updated)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {url('sitemap.xml')}\n"
    files[".nojekyll"] = ""
    for name, text in files.items():
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    for name in ("art.js", "site.css", "list.js"):
        shutil.copy(SRC / name, OUT / name)
    (OUT / "data").mkdir(exist_ok=True)
    shutil.copy(ROOT / "data" / "events.json", OUT / "data" / "events.json")
    print(f"pages: {len(files)} files in {OUT.relative_to(ROOT)}/")

    if "--no-art" not in sys.argv:
        render_art(events, OUT / "art")


if __name__ == "__main__":
    main()
