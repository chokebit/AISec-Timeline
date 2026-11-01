# Contributing

Corrections and new events are both welcome. Open an issue, or send a pull request that edits `data/events.json`.

## Adding an event

1. Check that it fits the scope in the README.
2. Copy an existing entry in `data/events.json` and fill in both `en` and `zh`. If you only write one language, say so in the pull request and a maintainer will add the other.
3. Run `python3 scripts/validate.py`.

## Fields

| Field | Rule |
|---|---|
| `id` | Lowercase words with hyphens, ending in the year |
| `occurred` | When it happened: `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Use `null` if unknown |
| `disclosed` | When it first became public, in the same format |
| `category` | `voice`, `video`, `breach`, `market` or `aggregate` |
| `outcome` | `loss`, `blocked`, `no_funds` or `aggregate` |
| `ai_evidence` | `confirmed`, `assessed`, `self_reported` or `unknown` |
| `usd_m` | Approximate USD in millions. `0` for `blocked`, `null` for `no_funds` |
| `short` | In `en` and `zh`: a label of a few words for the time navigator |
| `steps` | In `en` and `zh`: the attack chain in order, in short phrases, with the same number of items |
| `sources` | At least one, each with `name`, `url` and `kind`: `official`, `news` or `secondary` |

## Evidence rules

- Grade AI use by what the source actually says. "Police believe" is `assessed`. Police warning about AI in general does not count for a specific case.
- Prefer official statements and original reporting. Use aggregators only when the original cannot be reached.
- When sources disagree, record both and say who said what.
- Do not name private individuals. Use roles.
- Text fields are plain text. HTML is shown literally.
