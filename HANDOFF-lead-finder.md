# HANDOFF: Israeli lead finder (`/find-leads`)

Handoff from the session of 10–24 Nov 2026. To continue in a new session, say:
**"Read `HANDOFF-lead-finder.md` and continue the lead finder."**

## Start here
- **Branch:** `claude/wizardly-allen-y5msa0` (repo `ilaymouyal526-max/sushi-phatat-naknak`, **public**). It contains the
  original work from `claude/jolly-meitner-s4e01m` (merged) plus the lead-burn scheduler (section 8). No pull request has been opened.
- **Tests:** `python3 -m unittest discover -s tests` (51 tests, stdlib `unittest`, no pytest needed). All pass.
- **Needs:** Python 3.10+ with `requests`, `beautifulsoup4`, `openpyxl` (and `zoneinfo`, built in).
- **The repo also holds an unrelated project** (`commercial/`, the AI sushi commercial). The lead finder is self-contained in
  `lead_agent/`, `tests/` and `.claude/skills/find-leads/`.
- **Spending rule (CLAUDE.md):** never spend credits or money without showing the cost and getting a clear yes.
  The lead finder is built to be **100% free**.

## What the user chose
| Question | Answer |
|---|---|
| Region | **Israel** (Hebrew + English city names, Hebrew outreach) |
| Business types | **Any local business**, scored on digital gaps |
| Lead signals | "research online for tactics and calculate % of succeeding", which became a researched logistic model that learns |
| Data source | **Free only**: OpenStreetMap + direct website checks + Claude's own web search |
| Interface | **Claude Code skill** (`/find-leads`) wrapping a Python engine |
| Output | **CSV / Excel**, plus (added later) a **phone page** (`.html`), because a friend opened the Excel on a phone and saw only the rating |
| Outreach | **Hebrew drafts, never auto-sent** |
| Success % | **Research baseline + learns** from won/lost results |
| Calling add-ons | **All 8**: daily call plan, follow-up tracker, holidays, learn my best hours, phone script, objection answers, "missed you" WhatsApp, calendar file |

## What's built
### 1. Find → verify → merge (core flow)
```bash
python3 -m lead_agent find "Tel Aviv" --category beauty --limit 150   # OSM search + website audit + score
python3 -m lead_agent show leads/<run>.json --band hot,warm --top 30   # leads to verify
python3 -m lead_agent merge leads/<run>.json updates.json             # Claude's findings + openers -> rescore
```
- `find` searches OpenStreetMap over a city bounding box (~28 Israeli cities built in, Hebrew aliases, Nominatim fallback, or `--bbox`).
  Categories: `all`, groups (`beauty, health, food, trades, fitness, professional, retail, auto, education, hospitality`), raw OSM values, or a comma list.
- It excludes chains (`brand` tags), institutions (hospitals, schools, banks…), leads delivered before (`leads/seen.csv`) and do-not-contact leads.
- Directory pages (easy.co.il, d.co.il, b144, Wolt, 10bis…) are **not** counted as a website. Facebook/Instagram "websites" move to the social fields.
- The website audit checks: reachable / SSL / HTTPS / mobile viewport / © year / speed / free builder / booking / WhatsApp / tel: / form / chat / analytics.
  A bot-blocked site (401/403/429/503) is "blocked", not "dead".
- The skill (step 2) has Claude **verify** top leads with one WebSearch each (own website, phone, socials, opening hours, owner name),
  then write `outreach_he`, `call_script_he` and `missed_he`, and merge them. Merge re-audits new websites and keeps what the user typed in the sheet.

### 2. Success % (`score.py`, `data/weights.json`, `learn.py`)
- Logistic model with a prior of 1.5% for an unfiltered business. Website/automation gaps are capped as a group (1.1 log-odds).
  Typical results: about 5% for a no-website lead with a phone, about 9–10% for the best (high-value category, active, social), 1–3% for weak leads.
  Bands: **Hot ≥ 7%**, **Warm ≥ 3.5%**.
- Lead types: WEBSITE / REDESIGN / AUTOMATION / REDESIGN+AUTOMATION / LOW_FIT.
- `python3 -m lead_agent learn <sheet.xlsx>` reads the `status` column (won = 1; lost / no_reply / not_interested = 0).
  It needs at least 5 closed outcomes with at least 1 win, and refits with L2 toward the baseline (so about 100 outcomes dominate).
  It saves `leads/weights.learned.json`, which is used automatically.

### 3. Outputs per run (`leads/<date>-<city>-<category>.*`)
- **`.html` phone page** (`cards.py`): one self-contained file with no external scripts. One card per lead, with:
  - rating, reasons in Hebrew, and the opener (with a Copy button);
  - Call, WhatsApp (opener pre-filled, mobile numbers only) and "💬 ניסיתי להתקשר…" ("I tried to call…") WhatsApp buttons;
  - links, and filter chips: All / 📞 טוב עכשיו ("good now") / Hot / Warm / Cold;
  - the **"when to call" block** with a live badge (🟢 good now / 🟠 rush, with a better time / ⚪ closed or holiday), computed in Israel time even if the phone is in another time zone;
  - **call-log buttons**: ענה (answered) / לא ענה (no answer) / לחזור ב… (call back at…) / פגישה (meeting) / לא מעוניין (not interested) / נסגר ✓ (closed ✓), plus undo,
    a next-try line, and an **export call log** button;
  - expandable call script and objection answers.
- **`.xlsx`**: phone-friendly. Name is the first column, only the header row and name column are frozen, and the call columns sit after "what to sell".
  Includes the script and missed-you columns, a status dropdown, an "התנגדויות · Objections" sheet and a "How to use" sheet.
  The headers `status`, `notes`, `outreach_he`, `signals` and `lead_id` are machine-read: **don't rename them**.
- **`.csv`** (same columns) and **`.json`** (the working file that `merge` / `plan` / `log` read).

### 4. Call timing (`call_times.py`, `holidays.py`, `data/holidays_il.json`)
- Profiles by business type: restaurant, cafe, bar, beauty, clinic, trades, garage, school, office, accountant, fitness, retail, hotel, default.
  Each has best windows, rush windows and a reason, and a Hebrew tip.
- Trades use a mobile phone, so their windows are **not** trimmed to shop hours. Other types are trimmed to OSM `opening_hours` when it can be parsed.
  If nothing fits, the window becomes the first 30 minutes after opening.
- Israeli rules: Sun–Thu; Sunday from 10:00 (premises); Friday only until 11:00 (not for beauty or retail); never Friday afternoon or Saturday;
  calls only between 07:30 and 20:30. Accountants: no calls on the 10th–15th of the month (VAT reporting).
- Holidays 2026–2028 come from the Hebcal API (Israel schedule) and are committed as JSON:
  - `closed` (Yom Tov / Atzmaut): no calls
  - `sensitive` (memorial days): no sales calls
  - `eve`: treated like Friday
  - `low` (Chol HaMoed / Purim / Tisha B'Av): allowed, with a warning
- Opening hours are shown in Hebrew (`hours_he`). Time ranges use an **ASCII hyphen** on purpose: an en dash reverses the range inside Hebrew text.

### 5. Call log, follow-ups, do-not-contact, personal best hours (`calls.py`)
```bash
python3 -m lead_agent log add <lead_id> no_answer [--at "YYYY-MM-DD HH:MM"] [--callback "..."] [--note "..."]
python3 -m lead_agent log import calls-2026-11-17.csv    # file exported from the phone page
python3 -m lead_agent log show
```
- Log files: `leads/calls.csv` and `leads/do_not_contact.csv`.
- No answer: the next try goes in a **different window or day**, at least 2 hours later. After **4 no-answers** it stops and suggests the missed-you WhatsApp.
  `call_back` is scheduled at the time given. `not_interested` adds the lead to do-not-contact (matched by id and by phone).
  Meeting, won and lost move the sheet's `status` forward only.
- Personal best hours: answer rate per profile and hour, smoothed toward priors (best 30%, other 20%, rush 10%, k = 5).
  They appear on cards and steer the planner after about 20 calls per profile.

### 6. Daily plan + calendar (`plan.py`)
```bash
python3 -m lead_agent plan [--date YYYY-MM-DD] [--max 25]
```
- Reads every run in `leads/`. Order: callbacks → due retries → Hot → Warm (verified first), 8-minute slots inside each lead's best window.
  Skips leads without a phone, do-not-contact leads and finished leads.
- Writes `plan-<date>.html` and `plan-<date>.ics`: one event per call block with a 5-minute alarm, and one per callback with a 10-minute alarm.
  Times are UTC via `zoneinfo`, with CRLF line endings and folding.
- On Saturday or a holiday it reports the reason. Without `--date`, it plans the next working day.

### 7. Scripts, objections, missed-you (`scripts_he.py`, `data/objections_he.json`)
- Templates by lead type fill in the real gap, and show "(תבנית)" ("template") until Claude writes a personal version.
- The script opens with the reason for the call and never asks "is this a bad time?".
- `objections_he.json` holds 7 common objections (Instagram is enough, too expensive, no time, already have someone, send me an email,
  need to think, word of mouth) with variants per lead type. The user can edit it.

### 8. Lead burn: spend leftover usage before the reset (`burn.py`, `/lead-burn`, `lead-finder` subagent)
Added 24 Nov 2026. The user asked: "make it a subagent that uses credits an hour before the reset times; if there are still
a lot of credits, ask for permission and notify me beforehand in case I have another project to work on."
- **Subagent** `.claude/agents/lead-finder.md`: one full find → verify → texts → merge run for a city/category, with a deadline.
- **Skill** `.claude/skills/lead-burn/SKILL.md`: a chain of one-shot `send_later` checks named `lead-burn check` (one pending
  at a time). Each check reads `get_session` → `external_metadata.rate_limit_info` (`resetsAt`, `status`, `isUsingOverage`)
  and runs `python3 -m lead_agent burn decide`.
  - 70 min before the reset, if `status == allowed` and no overage, it sends a **push notification + chat question**. It runs
    the subagent only on the user's "go", until 5 min before the reset. No answer = no run.
  - Warning/overage, < 25 min left, or quiet hours (23:00–08:00 Israel) → skip that window. Otherwise it just schedules the next check.
  - After a run: `burn finish` records counts + **hashed** lead ids, advances the rotation (16 cities × 6 categories),
    sends the `.html` + `.xlsx` with SendUserFile, and pushes a "done" notification.
- **State** `lead_agent/state/burn.json` is committed (settings, rotation, asked_for, run counts, salted-hash seen/dnc ids).
  The repo is public, so it holds no names or phones (a test checks this). `find` skips hashed seen/dnc ids too, so runs don't
  repeat leads after the container (and `leads/`) is reset.
- **Limit:** there's no exact "% left", only `allowed` vs `allowed_warning`/`rejected` and the reset time.

## File map
| Path | Role |
|---|---|
| `.claude/skills/find-leads/SKILL.md` | The agent workflow: find, verify, write Hebrew texts, merge, report, plan, log, learn |
| `lead_agent/cli.py` | Commands: `find`, `show`, `merge`, `learn`, `log add/import/show`, `plan` |
| `lead_agent/osm.py` | Overpass query + mirrors, categories, exclusions, lead records |
| `lead_agent/cities.py` | City bounding boxes + Hebrew aliases + Nominatim fallback |
| `lead_agent/audit.py` | Website checks (`analyse_html` is pure and tested offline) |
| `lead_agent/score.py` / `learn.py` / `data/weights.json` | Signals → success %, bands, reasons; refit from outcomes |
| `lead_agent/call_times.py` / `holidays.py` / `data/holidays_il.json` | When to call |
| `lead_agent/calls.py` | Call log, follow-ups, do-not-contact, personal stats |
| `lead_agent/plan.py` | Daily plan + `.ics` |
| `lead_agent/scripts_he.py` / `data/objections_he.json` | Scripts, missed-you, objections |
| `lead_agent/export.py` | JSON / CSV / XLSX writer, carries over sheet edits, applies the call log |
| `lead_agent/cards.py` | Phone page and plan page (HTML + JS) |
| `lead_agent/burn.py` / `state/burn.json` | Lead-burn decisions, rotation, hashed memory (section 8) |
| `.claude/skills/lead-burn/SKILL.md` / `.claude/agents/lead-finder.md` | Scheduled leftover-usage runs + the subagent |
| `lead_agent/paths.py` | User data folder: `./leads` or `$LEAD_AGENT_HOME` |
| `lead_agent/RESEARCH.md` | Sources for the % and the call times (sourced vs. inferred) |
| `lead_agent/README.md` | User guide |
| `tests/` | 51 tests: audit, score/learn/osm, cards, CLI end-to-end, call times/holidays, call log/plan, lead burn |
| `leads/` (**git-ignored**) | Run files, `seen.csv`, `calls.csv`, `do_not_contact.csv`, `outcomes.csv`, `weights.learned.json`, plans |

## Research summary (details and links in `lead_agent/RESEARCH.md`)
- **Close rate:** cold outreach converts about 0.2–2% (Belkins, Martal, Hunter). Personalised messages that name a real problem
  get about twice the replies. One self-reported campaign calling 340 businesses with no website closed about 3% of them, which sets the baseline scale.
- **Signals:** agency scorers weight a dead site or SSL error highest, then no mobile version, slowness, an old © year, no HTTPS, no booking, no form (Apify scorers).
  In Israel, WhatsApp is the default business channel.
- **When to call:** studies agree on mid-week and mid-day but disagree on the exact hour, and the difference can be about 1% (Close, Sales Gravy).
  Avoiding the business's own rush matters more. Only the **restaurant** windows (Cleverly) and the generic default are sourced;
  the other profiles are **inferred** and should be corrected by the user's call log.
- **Follow-up:** 93% of conversations happen by the 3rd attempt (Cognism). Per-dial connect rate is about 10% vs. about 25% per prospect (Belkins).
- **Openers:** stating the reason for the call gives about 2.1× success; "bad time?" makes a meeting about 40% less likely (Gong).
- **Compliance:** Israel's Communications Law §30A restricts bulk commercial messages. Send one personal message, and stop on "no".
  Phone calls are the safest channel. Not legal advice.

## Verified in this session
- Live `find` runs: Ramat Gan (beauty + health: 149 OSM elements, 39 chains excluded) and Haifa (trades + auto: 25 leads).
  Each took about 20 seconds through the `maps.mail.ru` mirror.
- Enrichment was tested by hand: one WebSearch confirmed a Ramat Gan vet has only a Dapei Zahav listing.
- Merge, learn (simulated outcomes), carry-over of sheet edits, and the merge-vs-sheet conflict (fields merge just updated win).
- Phone page screenshots (iPhone size): name, phone, rating and reasons are readable without scrolling sideways.
  The live badge was checked at Tue 12:45, Tue 15:30 and Sat 10:00, including with the phone set to New York time.
- Phone log loop: tap no-answer / call-back / meeting and undo → export CSV → `log import` → the sheet updated.
- `.ics`: valid structure, correct UTC times (15:30 Israel = 13:30Z), lines folded to 75 bytes or less.
- Plan rules: retry in a different window, callback at the exact time, do-not-contact excluded, Saturday and Yom Kippur empty.

## Known limits and gotchas
- **OSM data is thin.** In one test box only 3 of 34 hairdressers had a website tag and 9 had a phone.
  "No website" stays unverified until the skill checks online (the `verified_online` column).
- **Overpass mirrors:** in this cloud environment only `maps.mail.ru` answered (overpass-api.de reset the connection; kumi and private.coffee timed out).
  The code tries all four in order. **DuckDuckGo HTML search was rate-limited**, so enrichment uses Claude's WebSearch.
  b144 and d.co.il are reachable but not scraped (terms of use).
- **Calls logged on the phone stay in that phone's browser storage** until exported. If the page is opened on two phones, their logs don't sync.
- The success % and the call windows are **estimates**. Most call windows are inferred.
- The holiday table covers **2026–2028 only**. Regenerate it from Hebcal before 2029.
- The sample files sent in this session (Haifa run, the plan for 16/11, `.ics`) were in the session scratchpad and **are not kept**.
  Re-create them with `find` and `plan`.
- No full end-to-end `/find-leads` run with Claude's verification and personal openers for all top leads has been done yet.
  Only one lead was enriched by hand.

## Ideas not built yet
1. Publish the phone page as a shared artifact with a shared database, so call logs from several phones sync with no export step.
2. An optional **paid** Google Places mode for better phones and review counts. It must show the cost and get a yes first (CLAUDE.md).
3. A one-page website **mockup** per no-website lead to send with the WhatsApp opener.
4. Refresh `holidays_il.json` beyond 2028 (a small script against the Hebcal API).
5. Record the call hour in the `learn` model too, so timing and close rate learn together.
6. Open a pull request for the branch when the user asks.

## Timeline of this session
1. "Create a lead finding agent for businesses that need websites and automation; ask me questions". Choices made (table above), then research and the plan.
2. Built `lead_agent` + `/find-leads` (OSM, audit, score, learn, CSV/XLSX, merge), with live tests in Ramat Gan and Haifa. Commit `6e88a80`.
3. "My friend opened it and saw only the rating". The cause was freeze panes at E2 hiding the other columns on a phone.
   Re-laid the sheet phone-first and added the `.html` lead-cards page. Commit `e12a9e9`.
4. Asked (in Hebrew) what time is best to call, and how to improve sales. Answered with research: Sun–Thu 10:00–11:30 / 14:30–16:30,
   avoid each business's rush, follow up 3–5 times, state the reason early.
5. "Add it to the lead finder: best times, rush hours". The plan was rejected with "suggest some more add-ons"; the user picked all 8.
   Built call timing, holidays, call log, follow-ups, do-not-contact, personal best hours, daily plan + `.ics`, scripts, objections and missed-you.
   Commit `53f3f9b`.
6. "Give me a handoff file". This file.
7. (New session, 24 Nov) "Make it a subagent that uses credits an hour before the reset times; ask permission and notify me first."
   Built section 8 and armed the first check.
