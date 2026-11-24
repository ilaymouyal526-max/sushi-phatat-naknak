# How the success % is calculated

`success_%` estimates **the chance that a business becomes a paying client after one personal
outreach sequence** (a call or a one-to-one WhatsApp message plus a follow-up). It is a logistic model:

```
log-odds = intercept + Σ weight × signal        (website/automation gaps capped as a group)
success  = 1 / (1 + e^-log-odds)
```

The weights are in `data/weights.json`, each with a note. Bands: **Hot ≥ 7%**, **Warm ≥ 3.5%**, Cold below.

## Where the baseline comes from (researched Nov 2026)

| Finding | Used for |
|---|---|
| Cold B2B email: ~3–7% reply rate; 0.2–2% become paying customers; 2% is "solid", 5% exceptional ([Belkins](https://belkins.io/blog/cold-email-outreach-statistics.md), [Martal](https://www.martal.ca/cold-emailing-statistics), [Hunter](https://hunter.io/the-state-of-cold-email)) | Intercept = 1.5% for an unfiltered local business |
| Advanced personalization ≈ 18% reply vs ≈ 9% generic; messages naming a *specific* problem on the prospect's site get far more replies (same sources plus practitioner reports) | Openers always name one real, verified gap |
| First follow-up lifts replies ~49%; a third follow-up lowers them | Model assumes one opener + one follow-up |
| Practitioner report: 340 cold calls to local businesses with **no website**, ~68% pickup, 41 discovery calls, ~$23k closed; med spas, dentists and restaurants converted best (self-reported, anecdotal, so weighted conservatively) | `no_website` is the strongest signal; `high_value_cat`; phone reachability (`has_phone`) |
| Agency lead scorers weight: dead site / SSL errors highest, then no mobile viewport, slow, stale © year, no HTTPS, no booking link, no contact form / click-to-call ([Apify lead-readiness auditor](https://apify.com/signalengine/lead-readiness-auditor), [Google Maps website lead scorer](https://apify.com/market_radar_tools/google-maps-website-lead-scorer)) | The site-quality signals and their relative order |
| Israel: WhatsApp penetration > 99% of smartphone users and the default business channel; > 99% of businesses have < 20 employees ([ToI blog, a promotional source](https://blogs.timesofisrael.com/why-whatsapp-first-is-now-table-stakes-for-israeli-small-businesses/), CBS) | `no_booking_or_whatsapp` is the automation pitch |

Sanity check: the no-website call campaign above closed roughly 3% of all businesses called. Our model gives an
average no-website lead with a phone about 5%, and the best (high-value category, active, social presence) about 9–10%.
A redesign lead with many problems is capped around 10–12%.

## Honest limits
- The benchmarks are mostly email/B2B and partly self-reported. Treat the % as a **ranking with a realistic
  scale**, not a promise.
- OpenStreetMap often lacks websites. "No website" is only a claim until the skill verifies it online
  (`verified_online` column).
- The model improves only if you log outcomes: `python -m lead_agent learn <sheet.xlsx>`. Learning uses
  L2 regularisation toward this baseline, so a handful of results nudges the weights and ~100 results dominate.

# When to call

`call_times.py` gives every lead best windows, rush hours to avoid and a tip, based on its type of business,
and trims them to its real opening hours when known. Researched Nov 2026.

| Finding | Used for |
|---|---|
| Studies agree that mid-week (Tue–Thu, in Israel Mon–Wed) and mid-day work best, but disagree on the exact hour (10:00, 11:00–12:00 or 16:00–17:00). In one well-known analysis the best day was barely 1% better than the worst ([Close](https://www.close.com/blog/best-days-times-to-cold-call), [Sales Gravy](https://salesgravy.com/best-time-to-cold-call/)) | Default windows 10:00–11:30 and 14:30–16:30. The hour matters less than avoiding the business's rush |
| Restaurants and salons are reachable mid-morning before lunch and mid-afternoon between lunch and dinner; calling at 12:30 annoys whoever picks up ([Cleverly](https://www.cleverly.co/blog/cold-calling-local-businesses)) | **Sourced**: restaurant profile |
| Local owners are often at the counter, on a job site or with a customer when you call; timing drives connect rates ([Cleverly](https://www.cleverly.co/blog/cold-calling-local-businesses)) | Every profile avoids its own "with customers" hours |
| 93% of conversations happen by the 3rd attempt and 98.6% by the 5th; per-dial connect ≈ 10% vs per-prospect ≈ 25% ([Cognism](https://cognism.com/reports/state-of-outbound-2026), [Belkins](https://belkins.io/blog/cold-calling-benchmarks)) | Follow-ups in a different window or day, stop after 4 no-answers |
| Stating the reason for the call increases success ~2.1×; "is this a bad time?" makes a meeting ~40% less likely; successful calls are a quick back-and-forth ([Gong](https://www.gong.io/resources/labs/cold-calling-tips/)) | Call scripts open with the real gap and use short questions |
| Israeli week: Friday is a short day and Saturday is Shabbat; holidays from [Hebcal](https://www.hebcal.com) (Israel schedule) | Sun–Thu calls, Friday until 11:00, holiday rules |

**Inferred (not from a source)**, so treat these as a reasonable starting point and let your own call log correct them:
café breakfast rush; bars before the evening shift; beauty Thu–Fri busiest; clinics before patients and at lunch;
trades before and after site work (their phone is a mobile); garages' drop-off and pick-up rushes; schools'
afternoon lessons; accountants avoiding the 10th–15th (VAT reporting); gyms' morning and evening peaks; retail
afternoons; hotels' check-out and check-in; Sunday from 10:00.

Your own data takes over: answer rates per type of business and hour are smoothed toward these priors
(best ≈ 30%, other ≈ 20%, rush ≈ 10%, weight of 5 calls). From ~20 logged calls per type, the cards show your
own best hour and the daily plan prefers it.
