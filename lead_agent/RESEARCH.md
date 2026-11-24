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

## Business types: who pays, who closes (24 Nov 2026)
Feeds `data/business_types.json` (the playbook used by `find --type`, `types suggest` and the website-lead-finder).
Published as the "Website Client Map" artifact. **Positions are estimates**: no public survey splits website budgets by
Israeli business type.
- **Price bands (₪, one-off build):** Midrag: landing page ₪1,000–3,500, brochure site ₪3,500–5,000, store ₪5,000–7,500;
  custom/premium above that. https://www.midrag.co.il/Content/Price/23030
- **Value of one customer, by industry:** Google Ads cost per lead 2025: legal services the highest at $131.63, restaurants
  among the lowest at $30.27, overall average $70.11 (LocaliQ/WordStream via Search Engine Land).
  https://searchengineland.com/google-ads-costs-keep-rising-but-conversion-rates-improved-in-2025-451167
- **Project values / easy niches:** personal-injury and family-law projects $8,000–15,000; home services and restaurants
  named the easiest niches to start (agency and lead-list sellers, so opinion).
  https://leadsbylocation.pages.dev/blog/best-niches-for-web-design/ · https://siteswan.com/how-to-sell-websites-to-law-firms
- **Healthcare and dental have higher customer lifetime value** than most local types (Datalane, qualitative).
- **Features by type:** booking for salons, dental and fitness; online ordering and menu for restaurants; quote form and
  click-to-call for home services; practice-area pages and intake for lawyers (Housecall Pro, Homebase, agency pages).
- **Accessibility (IS 5568, WCAG 2.0):** required for sites serving the public, but businesses with turnover of ₪1M or less
  are exempt without applying (gov.il, Kol Zchut). Old reporting cites civil claims up to ₪62,000 without proof of damage;
  check current rules.
- Quadrant rule: ease ≥ 5.5 and middle price (geometric) ≥ ₪5,000 → sweet spot. Re-place types from your own won/lost data.

## Restaurant management app: who pays, who closes, how to close (24 Nov 2026)
The app (the user's friend's product) is a **management app for the manager and staff**: shifts + time clock, tasks +
checklists, stock + supplier orders, and more. Feeds `data/app_types.json` (app playbook). Published as the "App Client Map"
artifact (https://claude.ai/artifact/QzngxhbHwP2vsKbpqWmJbE). Prices = first year (setup + 12 months), estimates.
(An earlier version of this section assumed a customer ordering/loyalty app; the user corrected it the same day.)
- **Hours record:** since the 2009 amendment every employer must keep an exact record of working hours, rest and overtime
  (Hours of Work and Rest Law §25(a1)). A time clock isn't required, but without one each day's record must be signed by the
  employee and approved. In overtime claims the burden of proof is on the employer up to 15 h/week or 60 h/month.
  https://www.workrights.co.il/פנקס-עבודה · https://www.bizportal.co.il/general/news/article/189561 · https://www.chamber.org.il/serviceslobby/legal/1856/2211/
- **Tips:** tips are wages, must appear on the payslip, and with the common "top-up to minimum wage" practice need records per
  shift and employee. Tips can't be used for employer contributions. https://www.kolzchut.org.il/he/תשר_למלצרים
- **Sector pressure (Israeli press, 2025):** severe staff shortage (quota of 2,000 foreign workers for restaurants), minimum wage
  up 17.9% since 2021 (₪6,247.67/month in 2025), ~4.6% of restaurants closed in 2025 (D&B), ~15% at risk (CofaceBDi).
- **Comparable tools (vendor/review pages):** 7shifts $39.99–134.99 per location/month (payroll extra; tasks add-on $12.99);
  Connecteam from ~$29/month (sources conflict); MarketMan $127–449 per location/month. Restigo (Israeli) has no public prices.
- **Vendor-claimed effects:** 1–3% of sales saved on labour (7shifts), ~2 points of labour cost (Restaurant365), turnover down
  up to 13% (sponsored QSR piece); replacing an hourly employee costs $2,305–5,864 (sources differ). Talking points, not promises.
- Quadrant rule: ease ≥ 5.5 and middle first-year price ≥ ₪8,000 → sweet spot.
