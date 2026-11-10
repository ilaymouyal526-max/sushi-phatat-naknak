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
