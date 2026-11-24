---
name: find-leads
description: Find Israeli local businesses that need a website or automation (booking, WhatsApp, lead capture), score each one's chance of becoming a paying client, verify the best ones online, draft a personal Hebrew opener and call script, and plan when to call (best hours, rush hours, holidays, follow-ups). Use for "/find-leads <city> [category] [count]", "find me leads in Haifa", "who needs a website in Ramat Gan", "/find-leads plan [date]" for a daily call plan, "/find-leads log …" or "I called X, no answer" to record calls, or "/find-leads learn <file>" to recalibrate from results.
---

# /find-leads: lead-finding agent (Israel, websites + automation)

You run the `lead_agent` Python package in this repo, then do the parts that need judgement:
verifying leads online and writing Hebrew openers. **Everything is free**: OpenStreetMap, direct website
checks and your own WebSearch/WebFetch. Never call a paid API (Google Places, etc.). If the user wants one,
follow CLAUDE.md: show the cost and get a clear yes first.

## Two lead finders: website vs. app
The work is split between two subagents. Pick by what the user wants to sell:
- **Quick website** → `website-lead-finder` (`.claude/agents/website-lead-finder.md`), which runs `find --focus website`.
  It keeps only businesses with no website of their own, or a site that doesn't open. This is the default for "/find-leads".
- **The app** → `app-lead-finder` (`.claude/agents/app-lead-finder.md`), which runs `find --focus app`. It needs the app
  profile, which gets built from a handoff file the user is waiting on from a friend. Until then it stops with that message.
- `find` with no `--focus` (= `all`) keeps the old mixed behaviour (website + redesign + automation).
For a big run (more than about 15 leads to verify), hand it to the subagent so the main conversation stays short.
For a small one, follow the steps below yourself, with `--focus website` and `--type <type>` on `find`.

## Always ask first: "Which type should we go for today?"
Every time the user starts the website lead finder (`/find-leads`, "find me leads", "run the lead finder", starting the
`website-lead-finder`), **unless they already named a business type in that message**, ask before running anything:
1. `python3 -m lead_agent types suggest` gives three suggestions: one sweet-spot type, one volume type and one big-fish
   type, each the one not run for the longest.
2. Ask with **AskUserQuestion**, header `Type today`, question "Which type of business should we go for today?", and these
   options in this order: the sweet-spot suggestion labelled `<name> (Recommended)`, then the volume one, then the big-fish one.
   Each option's description: quadrant, price band, ease and the pitch, e.g.
   "Sweet spot · ₪7,000–15,000 · ease 5.6/10 · Online booking and a look that matches the price of the treatment."
   The user can type any other type in "Other" (`types list` has all 18; Hebrew names work, e.g. צימרים).
   If the city is missing too, ask it in the same AskUserQuestion call as a second question.
3. Resolve the answer with `python3 -m lead_agent types show "<answer>"`. If it doesn't match, show `types list` and ask again.
4. Run with `--type <id>` (yourself, or pass `type` to the `website-lead-finder`). A type the playbook marks `skip`
   (garages) runs only because the user picked it, so say in one line that it's cheap and hard to close, then run it.
**Apps work the same way, with the restaurant app playbook.** When the user starts the app lead finder ("find app
leads", "app leads in Petah Tikva", starting `app-lead-finder`), ask the same question with
`python3 -m lead_agent types --app suggest` (sweet: busy sit-down restaurants / busy cafés / bars / bakeries; volume:
pizza-burger-delivery kitchens / fast-casual / ice cream; big fish: small chains / event halls & catering / chef /
multi-brand kitchens). Resolve with `types --app show "<answer>"` and pass `type` to the `app-lead-finder`.
The app is a **restaurant management app for the manager and staff** (shifts + time clock, tasks + checklists, stock +
supplier orders). `lead_agent/app_profile.json` describes it provisionally until the friend's handoff arrives.

## Arguments
- `/find-leads <city> [type] [count]`. Count defaults to `30` to verify and draft. With no type, ask (see above).
  `type` is a playbook type (`python3 -m lead_agent types list`); a raw `--category` still works for odd one-off searches.
  - City: English or Hebrew (`Tel Aviv`, `רמת גן`, `Haifa` …). Unknown cities fall back to free Nominatim geocoding.
  - Category: `all`, a group (`beauty, health, food, trades, fitness, professional, retail, auto, education, hospitality`),
    a raw OSM value (`dentist`, `hairdresser`, `car_repair`), or a comma list.
- `/find-leads learn <path-to-leads.xlsx>`: ingest the user's `status` column and recalibrate.
- `/find-leads plan [YYYY-MM-DD]`: today's (or that day's) call plan, see "Daily call plan".
- `/find-leads log <file.csv>` or plain words ("called המוסך שלי, no answer"): record calls, see "Call log".

If the city or the business type is missing, ask for them (see "Always ask first"). Don't ask about anything else.

## Workflow

1. **Find + audit + score** (≈20 s to 2 min):
   ```bash
   python3 -m lead_agent find "<city>" --type <type> --focus website --limit 150
   ```
   This writes `leads/<date>-<city>-<category>.json|csv|xlsx|html`, skips businesses delivered in earlier runs
   (`leads/seen.csv`; `--include-seen` overrides), excludes chains and institutions, and prints stats plus the top leads.

2. **Verify the top leads online.** OSM often lacks websites and phones, so a "no website" lead is a *claim
   to verify*, not a fact. List the leads to check:
   ```bash
   python3 -m lead_agent show <run.json> --band hot,warm --top <count>
   ```
   For each lead (up to `<count>`, best first), run **one** WebSearch: `"<name>" <city>` (Hebrew name as given;
   add the category word in Hebrew if the name is generic, e.g. מספרה, רופא שיניים, וטרינר). From the results:
   - Their **own website** (not easy.co.il / d.co.il / b144 / Facebook / Wolt / 10bis, which are directories) → put it in `website`.
     The merge step re-audits it automatically, and the lead may drop from WEBSITE to REDESIGN, AUTOMATION or LOW_FIT. That's correct.
   - A phone number, Facebook or Instagram page if missing.
   - Useful context for the opener (owner name, specialty, review themes) → `notes` (short).
   - Signs the business has closed → `notes: "possibly closed"` and skip the opener.
   - **Opening hours** if Google shows them → `opening_hours` in OSM format, e.g. `Su-Th 09:00-19:00; Fr 09:00-14:00`
     (days Su Mo Tu We Th Fr Sa, ranges with `-`, several time ranges with `,`, closed days `Sa off`). They make the
     "when to call" advice and the live badge exact for that business.
   Only use WebFetch when a result is clearly the business's page and you need one detail. Keep it light.

3. **Write a Hebrew opener** (`outreach_he`) for every verified Hot/Warm lead. Rules:
   - 2–4 short sentences, WhatsApp tone, first person, addressed to the business (use the owner's name if found).
   - Name **one specific, true gap** you found ("ראיתי שאין לכם אתר ושקביעת תורים רק בטלפון…" / "I saw you don't have a website and booking is by phone only…",
     "האתר לא נפתח בנייד…" / "Your site doesn't open on mobile…", "אין כפתור וואטסאפ באתר…" / "There's no WhatsApp button on your site…"). Never invent a gap.
   - One concrete benefit tied to their category (fewer missed calls, bookings at night, reminders that cut no-shows).
   - End with a low-pressure question (offer to send a short example) **and** an opt-out line
     ("אם לא רלוונטי, רק תגידו ולא אפנה שוב." / "If it's not relevant, just say so and I won't contact you again.").
   - Use the placeholder `[השם שלך]` ("[your name]") for the sender. Don't add prices or fake case studies.

   Also write, for the same leads:
   - `call_script_he`: a short phone script. Numbered lines: opener that states the reason for the call with the
     real gap (stating the reason early doubles success; never open with "is this a bad time?"), two short
     questions about how customers reach them today, one line on what you'd do for them, and the next step
     (send an example on WhatsApp / 10 minutes to talk). End with "אם אומרים לא – להודות ולא לחזור שוב."
     ("If they say no, thank them and don't call again.")
   - `missed_he`: a WhatsApp for when they didn't answer: "ניסיתי להתקשר אליכם קודם…" ("I tried calling you earlier…") + the gap +
     one-line offer + the opt-out line.
   Leads you don't personalise get generic templates automatically (marked "תבנית", template, on the card).

4. **Merge** everything in one JSON file (in the scratchpad or /tmp), keyed by `lead_id`:
   ```json
   {"osm:node/123": {"phone": "...", "website": "...", "facebook": "...", "instagram": "...",
                      "email": "...", "notes": "...", "opening_hours": "...",
                      "outreach_he": "...", "call_script_he": "...", "missed_he": "..."}}
   ```
   ```bash
   python3 -m lead_agent merge <run.json> <updates.json>
   ```
   Only include fields you actually found. Merge re-audits new websites, rescores, marks the leads
   `verified_online = yes`, and keeps anything the user already typed in the sheet (status, notes).

5. **Report** to the user in plain language:
   - Stats: businesses found, chains/institutions excluded, websites checked, verified, Hot / Warm counts.
   - The top 10 as a table: name, type (WEBSITE / REDESIGN / AUTOMATION), success %, the main reason, phone,
     **best time to call** (`call_best`).
   - Suggest `/find-leads plan` for a ready-made call schedule for tomorrow (or today).
   - The path to the **`.html` lead cards** (for phones: one card per lead with Call / WhatsApp buttons and the
     opener pre-filled; good to send to a partner) and the **`.xlsx`** (for tracking status and `learn`).
   - One line explaining the %: *an estimate of the chance this business becomes a paying client after one
     personal outreach, based on published outreach benchmarks; it gets more accurate as you log results.*
   - The compliance line below, and the learn reminder.

## Learning (`/find-leads learn <file>`)
The user fills the `status` column (contacted / replied / meeting / won / lost / no_reply / not_interested).
```bash
python3 -m lead_agent learn <file.xlsx>
```
`won` counts as a success, and `lost`/`no_reply`/`not_interested` count as failures. Open statuses are kept for later.
It needs at least 5 closed outcomes including 1 win. Report the observed win rate, the new baseline %, and the biggest
weight changes in plain words (e.g. "no-website leads are converting better than expected for you").
Learned weights live in `leads/weights.learned.json` and are used automatically by the next `find`.

## When to call (automatic)
Every lead gets `call_best` (best windows), `call_avoid` (rush hours), opening hours and a tip, from its type of business
(restaurant, café, bar, beauty, clinic, trades, garage, school, office, accountant, gym, retail, hotel, default),
trimmed to its real opening hours. Israeli rules apply: calls Sun–Thu, Sunday from 10:00, Friday only until 11:00,
never Saturday, holidays from `data/holidays_il.json` (holiday = no calls, eve = like Friday, Chol HaMoed = low
availability, memorial days = no sales calls). The phone page shows a live 🟢/🟠/⚪ badge in Israel time and a
"📞 טוב עכשיו" ("good now") filter. Sources and which windows are inferred: `lead_agent/RESEARCH.md`.

## Daily call plan (`/find-leads plan [date]`)
```bash
python3 -m lead_agent plan [--date YYYY-MM-DD] [--max 25]
```
Uses every run in `leads/`. Order: callbacks the business asked for (at their time) → due follow-ups → Hot → Warm
(verified first), each placed in its own best window, 8 minutes apart. It skips do-not-contact leads, finished
leads and leads without a phone. Writes `leads/plan-<date>.html` (cards in time order) and `plan-<date>.ics` (calendar:
one event per call block + a reminder for each callback). On Saturday or a holiday it says so and, without `--date`,
plans the next working day. Report: the blocks with times and counts, the first few calls, and both file paths.
Tell the user to open the `.ics` on their phone to add the blocks to their calendar.

## Call log (`/find-leads log …`)
- When the user tells you about calls in plain words, log each one:
  ```bash
  python3 -m lead_agent log add <lead_id> <answered|no_answer|call_back|not_interested|meeting|won|lost> \
      [--at "YYYY-MM-DD HH:MM"] [--callback "YYYY-MM-DD HH:MM"] [--note "..."]
  ```
  Find the `lead_id` with `python3 -m lead_agent show <run.json>` (match by name). Times are Israel time; default now.
- Calls logged with the buttons on the phone page stay on that phone until the user taps "ייצוא יומן שיחות"
  (export call log) and sends you the CSV: `python3 -m lead_agent log import <file.csv>` (duplicates are skipped).
- `log show` summarises calls and the user's own best hours.
- Effects: no answer → next try in a different window or day (2+ hours later). After 4 no-answers → stop and send
  the "missed you" WhatsApp. `call_back` → planned at that time. `not_interested` → added to
  `leads/do_not_contact.csv` and never shown again. meeting/won/lost update the sheet's `status` (used by `learn`).
  After ~20 calls per type of business, the cards show the user's own best answer hours and the planner prefers them.
- After logging, tell the user the next step for that lead (the command prints it).

## Rules
- **Never send messages, call, or email anyone.** The agent drafts; the user sends personally, one at a time.
- Compliance line (always include in the report): Israel's Communications Law §30A ("spam law") restricts
  bulk commercial messages. Send one personal message asking if they're interested, and stop if they say no.
  Personal phone calls are the safest channel. *Not legal advice.*
- Lead data stays in `leads/` (git-ignored). Don't commit it or paste phone lists into external services.
- If every Overpass mirror fails, say so and suggest retrying in a few minutes. Don't fabricate leads.
