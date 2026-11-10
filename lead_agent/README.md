# lead_agent: find Israeli businesses that need a website or automation

Free and local. Uses OpenStreetMap plus direct checks of each business's own website. No paid APIs.

## Use it from Claude Code (recommended)
```
/find-leads Tel Aviv beauty 30
/find-leads רמת גן all 20
/find-leads learn leads/2026-11-10-tel-aviv-beauty.xlsx
```
Claude finds, audits and scores the businesses. It then verifies the best leads online, writes a personal Hebrew
opener for each and hands you an Excel sheet. See `.claude/skills/find-leads/SKILL.md`.

## Or run the engine directly
```bash
python3 -m lead_agent find "Tel Aviv" --category beauty --limit 100
python3 -m lead_agent show leads/<run>.json --band hot --top 20
python3 -m lead_agent merge leads/<run>.json updates.json
python3 -m lead_agent learn leads/<run>.xlsx
```
Requires Python 3.10+ with `requests`, `beautifulsoup4` and `openpyxl`.

## What you get (`leads/<date>-<city>-<category>.xlsx`)
| column | meaning |
|---|---|
| success_% (estimate) / band | chance of becoming a paying client after personal outreach; Hot ≥ 7%, Warm ≥ 3.5% |
| lead_type | WEBSITE (no own site) · REDESIGN (broken/outdated site) · AUTOMATION (no booking/WhatsApp/lead capture) · LOW_FIT |
| why / why (עברית) | the top reasons behind the score |
| outreach_he | a Hebrew opener naming a real gap, which you send yourself |
| verified_online | `yes` once Claude has checked the business online |
| status | fill this in: contacted / replied / meeting / won / lost / no_reply / not_interested |

Then run `learn` on the sheet. Your results recalibrate the model (`leads/weights.learned.json`).
How the % is built and its sources: [RESEARCH.md](RESEARCH.md).

## Files
- `leads/` (git-ignored) holds your lead sheets, `seen.csv` (so reruns skip delivered leads), `outcomes.csv` and learned weights.
  Set `LEAD_AGENT_HOME` to keep them elsewhere.
- `data/weights.json` holds the research baseline weights.

## Rules of the road
Never bulk-message. Israel's Communications Law §30A restricts bulk commercial messages. Send one personal message
asking if they're interested, and stop if they say no. Phone calls are safest. Not legal advice.

Tests: `python3 -m unittest discover -s tests`
