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

## Who you work for, and how
The user runs creative work for **YOKO ONO, Asian Kitchen** (Achuza 124, Ra'anana): the in-store screen, the website, ads and reels, print, the dice-game happy hour. They write in Hebrew; answer in Hebrew unless asked otherwise.

Be the one who knows the whole picture. When the user asks for something:
1. Say what we **already have** for it (photo codes, branch, file, Higgsfield job).
2. Say what's **missing** and must come from them (prices, hours, real photos, approvals).
3. Propose the concrete next step, the free route first, with any paid step priced and waiting for a "yes".

## Read this first: `knowledge/ASSETS.md`
- **The full catalog:**
  - the restaurant facts and brand (logo, colors, fonts, dice-game rules);
  - every Drive photo and video, by code and by dish;
  - all Higgsfield work;
  - every project branch with its status and next step;
  - an "I want X" guide (screen, website, ad, print).
- **Drive photos:**
  - `python3 knowledge/tools/drive_get.py OUT_DIR Y421 R145` downloads by code, free;
  - `--find <word>` searches the titles;
  - `knowledge/drive-sheets/*.jpg` are labelled contact sheets to look at before picking a photo.
- **Best references for Higgsfield:** the professional shoot (codes Y001 to Y426, Google Drive folder `images_yoko`).
- **The current menu, with prices and the photo for each dish:** `knowledge/menu/MENU.md`.
- **Keep it current:** when you make, find or get approval for something, update `knowledge/ASSETS.md` in the same commit.
