# CLAUDE.md

## Spending rule (always applies)

**Never spend tokens, credits or money anywhere without explicit permission first.**

Before any action that costs credits, tokens or money, show the user:
- what you're about to run (tool, model, settings),
- what it's for,
- the exact cost, from a price check (`get_cost: true` or similar) where one exists,

then wait for a clear "yes". This covers Higgsfield, Artlist, Adobe and Descript generations, plus upscales, reframes, voiceovers, music and any other paid API call.

- If a tool has no price check (for example, `upscale_video`), don't call it just to find the price. Tell the user the price is unknown and ask first.
- Approval covers only the specific job shown. Batches, retries, extra variants or a different model each need a new approval.
- Free work doesn't need approval: local processing, sandbox ffmpeg edits, read-only lookups and price checks.

## Session start rule (always applies)

At the start of every session, before doing any work, suggest how to optimize the session for its goal:
- which skills to load (e.g. `sticker-designer`, `designer-base`, `sushi-ad-director`, `food-ad-3d-pipeline`),
- whether a quick web search for current references/trends would help,
- which existing assets to reuse (Higgsfield history, this repo) so no credits are wasted.

Keep it to a few lines and let the user pick before proceeding.
