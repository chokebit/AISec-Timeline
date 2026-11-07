# AI Chaotic Era

Major security events of the AI era.

English | [中文](README.zh-CN.md)

**Live site: <https://chokebit.github.io/AISec-Timeline/>**

A sourced chronicle of the biggest losses, turning points and unexpected moments in security during the AI era. Each entry separates what was lost, what was recovered, how strong the evidence for AI use is, and where the humans were.

## Scope

An event is included if it meets one of these tests:

- **Money:** AI was used, or is credibly believed to have been used, and there is a public amount or a clear measured impact.
- **Turning point:** a first, or a step that changes what attackers or defenders can do, such as AI carrying out most of an intrusion or finding zero-days at scale. Every "first" says who claimed it and how far humans were involved.
- **Lesson:** a widely cited case where the attack failed or no funds moved, and it teaches something concrete.

Incidents where AI systems themselves are compromised, such as prompt injection or model supply chain attacks, are not covered yet.

## How AI use is graded

| `ai_evidence` | Meaning |
|---|---|
| `confirmed` | An authority, a court filing, the affected company or the AI's developer says AI was used, or analysis of the code shows it |
| `assessed` | Police, insurers, security firms or informed sources believe AI was used, but it is not established |
| `self_reported` | Only the people involved mention AI, without detail or an outside check, as in FBI IC3 complaints or a researcher's own write-up |
| `unknown` | No public evidence of AI use so far, and it cannot be ruled out |

## How amounts work

- Amounts are what was transferred or reported lost. Recovered and frozen funds are listed in the notes and never netted off.
- Annual totals are never added to single cases.
- Third-party estimates that nobody has verified do not count as the amount.
- Original currency is kept. USD figures are approximate.

## Major events with an unknown AI role

Some entries are here for their scale or as turning points, even though no public evidence so far shows AI was involved. Binance (October 2026, about $6.3B) and the Ledger hardware implants are examples. Investigations are still open, so AI is neither claimed nor ruled out. These entries are marked `unknown` and stay out of every AI total.

## Data

All events are in [`data/events.json`](data/events.json), so you can use them without the website. Site totals are calculated from that file.

The site has three parts, in English and Chinese:

- **Gallery** (home page): one event at a time, with its artwork, along a timeline.
- **All events** (`/events/`): search and filter by type and evidence.
- **Event pages** (`/events/<id>/`): one page per event, for sharing and search engines.

## Contributing

Corrections matter more than new entries. See [CONTRIBUTING.md](CONTRIBUTING.md), or open an issue with a source.

## Run locally

```sh
pip install playwright && python3 -m playwright install chromium   # once
python3 scripts/validate.py
python3 scripts/build.py          # add --no-art to skip rendering images
python3 -m http.server 8000 -d _site
```

Then open <http://localhost:8000/>. Source files are in `site/`; `_site/` is generated and not committed. Every push to `main` builds and deploys the site through GitHub Actions. `SITE_URL` at the top of `scripts/build.py` sets the address used in links for search engines.

## License

- Code: [MIT](LICENSE)
- Data and text: [CC BY 4.0](LICENSE-DATA). Credit "AI Chaotic Era" and link to this repository.

This project summarizes public reporting. It is not legal, financial or security advice, and allegations against suspects remain unproven until a court decides.
