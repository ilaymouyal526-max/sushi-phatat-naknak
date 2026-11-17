# CLAUDE.md

## Image library rule (always applies)

**Don't ask the user to upload photos or the logo before checking the library.**
Every known image (Drive, the shared YOKO ONO folder, Higgsfield uploads) is indexed in
`library/catalog.csv` (Hebrew description, Drive file ID, proposed name, duplicates), with an overview in
`library/CATALOG.md` and contact sheets in `library/previews/`.
- **Skill `yoko-image-library` is installed in this repo** at `.claude/skills/yoko-image-library/`
  (SKILL.md + catalog.csv + logo + heic2jpg.py), so it loads in every Claude Code session here.
  Invoke it whenever a task needs any Yoko Ono image, photo, logo or brand asset.
- The same skill as a zip for claude.ai (Settings → Capabilities → Skills → Upload): `library/skill/yoko-image-library.zip`.
- When `catalog.csv` changes, copy it to `.claude/skills/yoko-image-library/` and `library/skill/yoko-image-library/`,
  then re-zip, so all three stay identical.
- Drive storage is full (Nov 2026): uploads to Drive fail. The user clears space themselves. **Never delete or trash
  anything in their Drive.**
- Find the asset there first, then fetch it by ID (`download_file_content`); HEIC → `library/tools/heic2jpg.py`.
- Logo: `library/brand/yoko-ono-logo_gold-on-black.png` (low-res working copy). Ask only for a vector original.
- Ask the user for an image only if the catalog truly has nothing that fits, and say what you searched.
- When new images are added or generated, add them to `catalog.csv` using the naming convention in CATALOG.md.

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
