# AI Security Incident Timeline

English | [中文](README.zh-CN.md)

**Live site: <https://chokebit.github.io/AISec-Timeline/>**

A sourced timeline of AI-enabled fraud and security incidents. Each entry separates three things that are often mixed up: what was lost, what was recovered, and how strong the evidence is that AI was used at all.

## Scope

An event is included if it meets one of these tests:

- AI was used, or is credibly believed to have been used, in an attack, and there is a public amount or a clear measured impact.
- It is a widely cited case where the attack failed or no funds moved, and it teaches something concrete.

Incidents where AI systems themselves are compromised, such as prompt injection or model supply chain attacks, are not covered yet.

## How AI use is graded

| `ai_evidence` | Meaning |
|---|---|
| `confirmed` | An authority, a court filing or the affected company says AI was used |
| `assessed` | Police, insurers, security firms or informed sources believe AI was used, but it is not established |
| `self_reported` | Complainants mentioned AI, as in FBI IC3 data |

## How amounts work

- Amounts are what was transferred or reported lost. Recovered and frozen funds are listed in the notes and never netted off.
- Annual totals are never added to single cases.
- Third-party estimates that nobody has verified do not count as the amount.
- Original currency is kept. USD figures are approximate.

## Considered and left out

These are large incidents with no evidence so far that AI caused them:

- **Binance, October 2026:** about $6.3B stolen.
- **Ledger hardware implants, 2026:** S$3.5M confirmed by Singapore police.

An event can be added if credible evidence of AI use appears.

## Data

All events are in [`data/events.json`](data/events.json), so you can use them without the website. Site totals are calculated from that file. The site has a story view with one event per screen, plus a searchable list. Each event has its own link, such as `#arup-deepfake-meeting-2024`.

## Contributing

Corrections matter more than new entries. See [CONTRIBUTING.md](CONTRIBUTING.md), or open an issue with a source.

## Run locally

```sh
python3 scripts/validate.py
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. The page reads a JSON file, so opening `index.html` directly will not work.

## License

- Code: [MIT](LICENSE)
- Data and text: [CC BY 4.0](LICENSE-DATA). Credit "AI Security Incident Timeline" and link to this repository.

This project summarizes public reporting. It is not legal, financial or security advice, and allegations against suspects remain unproven until a court decides.
