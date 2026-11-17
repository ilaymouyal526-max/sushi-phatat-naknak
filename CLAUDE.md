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

## Organization rule (always applies)

- Start every session by reading `README.md` (the project index and brand shortcuts).
- **Brand names map to brand kits.** "Sushi Push Pop" / "סושי פוש פופ" / "Yoko Ono" → `brand/yoko-ono/` (logo, product photos, how-to, brand kid, with Higgsfield media IDs). NEVER ask the user for a logo or product photo that's already there. For a new brand, create `brand/<name>/` the first time its assets appear, and add it to the shortcut table in `README.md`.
- Before asking for any image, check `brand/higgsfield-library.md` and run `show_medias` (it's free).
- Work for a project goes in `projects/<name>/`: `brief.md`, `treatment.md`, `assets.md`, `prompts/`, `scripts/`.
- **Log every asset** received or generated in that project's `assets.md` as soon as it exists: tool/model, job or media ID, URL, cost, prompt file, status. Prompts that were actually run get saved in `prompts/`.
- Before asking the user to re-send or re-find anything, search `assets.md` and `grep -ri` the repo first.
- Record decisions in `brief.md` → "Decisions made". Commit and push at the end of every working block, because the container is wiped.
