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

## Ad workflow rule (always applies)

For ANY food, restaurant or Yoko Ono / Sushi Push Pop ad, **invoke the `sushi-ad-director` skill first**, before concepts, budgets or prompts. It was built from the Higgsfield "3-Step Workflow To Make Ultra-Realistic AI Ads" video the user chose. Follow its stages in order:
1. **Concept**: 6-line brief, hook in the first 1–2s.
2. **Assets**: lock every recurring thing as a named Higgsfield Element (@name) from real photos.
3. **Shotlist**: style prefix + up-to-15s prompts made of CUTs, with ENDS ON, delivered as an HTML shotlist.

Also load the repo skill `ad-playbook` (`.claude/skills/ad-playbook/SKILL.md`): verified prices, draft math, reference and label rules learned in practice. Update it whenever a new lesson or price is verified.
When camera or composition must be exact, also use `food-ad-3d-pipeline` (blockout → locked first frame → motion reference).
Stills and animatic come before any video. Cheap drafts come before finals. Save each stage's output in the project folder.

## Organization rule (always applies)

- Start every session by reading `README.md` (the project index and brand shortcuts).
- **Brand names map to brand kits.** "Sushi Push Pop" / "סושי פוש פופ" / "Yoko Ono" → `brand/yoko-ono/` (logo, product photos, how-to, brand kid, with Higgsfield media IDs). NEVER ask the user for a logo or product photo that's already there. For a new brand, create `brand/<name>/` the first time its assets appear, and add it to the shortcut table in `README.md`.
- Before asking for any image, check `brand/higgsfield-library.md` and run `show_medias` (it's free).
- Work for a project goes in `projects/<name>/`: `brief.md`, `treatment.md`, `assets.md`, `prompts/`, `scripts/`.
- **Log every asset** received or generated in that project's `assets.md` as soon as it exists: tool/model, job or media ID, URL, cost, prompt file, status. Prompts that were actually run get saved in `prompts/`.
- Before asking the user to re-send or re-find anything, search `assets.md` and `grep -ri` the repo first.
- Record decisions in `brief.md` → "Decisions made". Commit and push at the end of every working block, because the container is wiped.
