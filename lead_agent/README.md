# lead_agent: find Israeli businesses that need a website or automation

> Full project history, decisions and next steps: [`HANDOFF-lead-finder.md`](../HANDOFF-lead-finder.md).

Free and local. Uses OpenStreetMap plus direct checks of each business's own website. No paid APIs.

## Use it from Claude Code (recommended)
```
/find-leads Tel Aviv beauty 30
/find-leads רמת גן all 20
/find-leads learn leads/2026-11-10-tel-aviv-beauty.xlsx
/find-leads plan                 # today's call plan (or the next working day) + calendar file
/find-leads log calls-2026-11-17.csv   # or just tell Claude: "called המוסך שלי, no answer"
/lead-burn status                # leftover-usage runs: ~70 min before each plan reset Claude asks, you reply "go"
```
**Lead burn:** before each usage reset, if plenty is left, Claude notifies you and asks. Reply `go` (or
`go haifa trades 30`) and the `lead-finder` subagent runs until 5 minutes before the reset. Ignore it and nothing runs.
`/lead-burn off` stops the checks. Details: `.claude/skills/lead-burn/SKILL.md`.
Claude finds, audits and scores the businesses. It then verifies the best leads online, writes a personal Hebrew
opener for each and hands you an Excel sheet. See `.claude/skills/find-leads/SKILL.md`.

## Or run the engine directly
```bash
python3 -m lead_agent find "Tel Aviv" --category beauty --limit 100
python3 -m lead_agent show leads/<run>.json --band hot --top 20
python3 -m lead_agent merge leads/<run>.json updates.json
python3 -m lead_agent learn leads/<run>.xlsx
python3 -m lead_agent plan --date 2026-11-17
python3 -m lead_agent log add osm:node/123 no_answer
python3 -m lead_agent log import calls-2026-11-17.csv
```
Requires Python 3.10+ with `requests`, `beautifulsoup4` and `openpyxl`.

## What you get
- **`leads/<date>-<city>-<category>.html`: open this on a phone.** One card per lead, best first, with rating,
  reasons, the Hebrew opener (with a Copy button), and Call / WhatsApp / website / map buttons. WhatsApp opens with the
  message pre-filled and you press send yourself. It's a single self-contained file, so you can share it over WhatsApp or email.
  Each card also shows **when to call** (best hours, rush hours, opening hours, a tip) with a live 🟢/🟠/⚪ badge in
  Israel time, buttons to log each call (answered / no answer / call back / meeting / not interested / closed), the
  next suggested try, a call script, answers to common objections, and a "ניסיתי להתקשר…" ("I tried calling…") WhatsApp button.
  Filter "📞 טוב עכשיו" ("good now") shows who to call right now. Logged calls stay on the phone until you tap
  "ייצוא יומן שיחות" ("export call log") and give the file to Claude.
- **`plan-<date>.html` + `plan-<date>.ics`**: the daily call plan in time order, and a calendar file with the call
  blocks and callback reminders.
- **`.xlsx` (and `.csv`)** for tracking and learning. Columns start with what you act on:

| column | meaning |
|---|---|
| name / phone | who to contact (the name column stays frozen while you scroll) |
| rating | band + estimated chance of becoming a paying client; Hot ≥ 7%, Warm ≥ 3.5% |
| best time to call / rush hours / opening hours | when the owner is most likely free, and when not to call |
| attempts / next try | from your call log |
| what to sell | New website (no own site) · Redesign (broken/outdated site) · Automation (no booking/WhatsApp/lead capture) · Low fit |
| why / why (English) | the top reasons behind the score |
| outreach_he | a Hebrew opener naming a real gap, which you send yourself |
| verified_online | `yes` once Claude has checked the business online |
| status | fill this in: contacted / replied / meeting / won / lost / no_reply / not_interested |

Then run `learn` on the sheet. Your results recalibrate the model (`leads/weights.learned.json`).
How the % is built and its sources: [RESEARCH.md](RESEARCH.md).

## Files
- `leads/` (git-ignored) holds your lead sheets, `seen.csv` (so reruns skip delivered leads), `outcomes.csv` and learned weights.
  Set `LEAD_AGENT_HOME` to keep them elsewhere.
- `leads/calls.csv` and `leads/do_not_contact.csv` hold your call log and the businesses that said no.
- `data/weights.json` holds the research baseline weights. `data/holidays_il.json` holds Israeli holidays 2026–2028
  (from Hebcal). `data/objections_he.json` holds the objection answers, which you can edit.

## Rules of the road
Never bulk-message. Israel's Communications Law §30A restricts bulk commercial messages. Send one personal message
asking if they're interested, and stop if they say no. Phone calls are safest. Not legal advice.

Tests: `python3 -m unittest discover -s tests`
