---
name: find-leads
description: Find Israeli local businesses that need a website or automation (booking, WhatsApp, lead capture), score each one's chance of becoming a paying client, verify the best ones online and draft a personal Hebrew opener. Use for "/find-leads <city> [category] [count]", "find me leads in Haifa", "who needs a website in Ramat Gan", or "/find-leads learn <file>" to recalibrate from results.
---

# /find-leads: lead-finding agent (Israel, websites + automation)

You run the `lead_agent` Python package in this repo, then do the parts that need judgement:
verifying leads online and writing Hebrew openers. **Everything is free**: OpenStreetMap, direct website
checks and your own WebSearch/WebFetch. Never call a paid API (Google Places, etc.). If the user wants one,
follow CLAUDE.md: show the cost and get a clear yes first.

## Arguments
- `/find-leads <city> [category] [count]`. Defaults: category `all`, count `30` to verify and draft.
  - City: English or Hebrew (`Tel Aviv`, `רמת גן`, `Haifa` …). Unknown cities fall back to free Nominatim geocoding.
  - Category: `all`, a group (`beauty, health, food, trades, fitness, professional, retail, auto, education, hospitality`),
    a raw OSM value (`dentist`, `hairdresser`, `car_repair`), or a comma list.
- `/find-leads learn <path-to-leads.xlsx>`: ingest the user's `status` column and recalibrate.

If the city is missing, ask for it (and offer the category groups). Don't ask about anything else.

## Workflow

1. **Find + audit + score** (≈20 s to 2 min):
   ```bash
   python3 -m lead_agent find "<city>" --category <category> --limit 150
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
   Only use WebFetch when a result is clearly the business's page and you need one detail. Keep it light.

3. **Write a Hebrew opener** (`outreach_he`) for every verified Hot/Warm lead. Rules:
   - 2–4 short sentences, WhatsApp tone, first person, addressed to the business (use the owner's name if found).
   - Name **one specific, true gap** you found ("ראיתי שאין לכם אתר ושקביעת תורים רק בטלפון…" / "I saw you don't have a website and booking is by phone only…",
     "האתר לא נפתח בנייד…" / "Your site doesn't open on mobile…", "אין כפתור וואטסאפ באתר…" / "There's no WhatsApp button on your site…"). Never invent a gap.
   - One concrete benefit tied to their category (fewer missed calls, bookings at night, reminders that cut no-shows).
   - End with a low-pressure question (offer to send a short example) **and** an opt-out line
     ("אם לא רלוונטי, רק תגידו ולא אפנה שוב." / "If it's not relevant, just say so and I won't contact you again.").
   - Use the placeholder `[השם שלך]` ("[your name]") for the sender. Don't add prices or fake case studies.

4. **Merge** everything in one JSON file (in the scratchpad or /tmp), keyed by `lead_id`:
   ```json
   {"osm:node/123": {"phone": "...", "website": "...", "facebook": "...", "instagram": "...",
                      "email": "...", "notes": "...", "outreach_he": "..."}}
   ```
   ```bash
   python3 -m lead_agent merge <run.json> <updates.json>
   ```
   Only include fields you actually found. Merge re-audits new websites, rescores, marks the leads
   `verified_online = yes`, and keeps anything the user already typed in the sheet (status, notes).

5. **Report** to the user in plain language:
   - Stats: businesses found, chains/institutions excluded, websites checked, verified, Hot / Warm counts.
   - The top 10 as a table: name, type (WEBSITE / REDESIGN / AUTOMATION), success %, the main reason, phone.
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

## Rules
- **Never send messages, call, or email anyone.** The agent drafts; the user sends personally, one at a time.
- Compliance line (always include in the report): Israel's Communications Law §30A ("spam law") restricts
  bulk commercial messages. Send one personal message asking if they're interested, and stop if they say no.
  Personal phone calls are the safest channel. *Not legal advice.*
- Lead data stays in `leads/` (git-ignored). Don't commit it or paste phone lists into external services.
- If every Overpass mirror fails, say so and suggest retrying in a few minutes. Don't fabricate leads.
