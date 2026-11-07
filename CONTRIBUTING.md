# Contributing

Corrections and new events are both welcome, and you do not need to write code.

- **Missing event:** [open the event form](https://github.com/chokebit/AISec-Timeline/issues/new?template=new-event.yml).
- **Something is wrong:** [open the correction form](https://github.com/chokebit/AISec-Timeline/issues/new?template=correction.yml).
- **Comfortable with Git:** send a pull request that edits `data/events.json`.

Every event gets artwork automatically from its `category`, so you never need to draw anything. Totals, event pages and the list update by themselves. A maintainer may add custom artwork to `site/art.js` later.

## Adding an event

1. Check that it fits the scope in the README.
2. Copy an existing entry in `data/events.json` and fill in both `en` and `zh`. If you only write one language, say so in the pull request and a maintainer will add the other.
3. Run `python3 scripts/validate.py`, then `python3 scripts/build.py --no-art` to check the pages build.

## Fields

| Field | Rule |
|---|---|
| `id` | Lowercase words with hyphens, ending in the year |
| `occurred` | When it happened: `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Use `null` if unknown |
| `disclosed` | When it first became public, in the same format |
| `category` | `voice`, `video`, `breach`, `market`, `theft`, `supply`, `autonomous`, `vuln` (AI finding vulnerabilities), `malware` (AI inside malware) or `aggregate` |
| `outcome` | `loss`, `blocked`, `no_funds` or `aggregate` |
| `ai_evidence` | `confirmed`, `assessed`, `self_reported` or `unknown` |
| `usd_m` | Approximate USD in millions. `0` for `blocked`, `null` for `no_funds` |
| `short` | In `en` and `zh`: a label of a few words for the time navigator |
| `plate` | The name on the exhibit label, in capitals. Text only, no logos |
| `steps` | In `en` and `zh`: the attack chain in order, in short phrases, with the same number of items |
| `art_note` | Optional, in `en` and `zh`: one line explaining the artwork |
| `sources` | At least one, each with `name`, `url` and `kind`: `official`, `news` or `secondary` |

## Evidence rules

- Grade AI use by what the source actually says. "Police believe" is `assessed`. Police warning about AI in general does not count for a specific case. If only the people involved mention AI, with no detail, it is `self_reported`.
- Prefer official statements and original reporting. Use aggregators only when the original cannot be reached.
- When sources disagree, record both and say who said what.
- Do not name private individuals. Use roles.
- Text fields are plain text. HTML is shown literally.
