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

## Naming: "מסך תצוגה" = the display screen
"מסך תצוגה" (display screen) means the in-store portrait TV loop in `menu-screen/` (`index.html` plus `render.js`). It is **not** the commercial in `commercial/`. When the user asks about the display screen (design, fonts, motion, slides), work only in `menu-screen/`, `fonts/` and `shared/`, and never touch or re-style the commercial.

## Delivery rule: everything goes to the user's Drive (always applies)
Every finished output (videos, images, PDFs, previews, comparison sheets) goes to the user's **own** Google Drive, into the folder **"Yoko Ono"** (folder id `18dCgXmIRH3EmFmXvIjyLCxt9JUi4tmyt`), in a subfolder per project. For example, the display screen's subfolder is **"מסך תצוגה"** (id `1XClm02iWIvbUTcxDGp5Z3Y8wbzzVIoap`).
- Don't deliver work as files in the chat; the user considers that unprofessional. Report in chat with the Drive link.
- Never upload to the shared "YOKO ONO" folder owned by someone else, unless the user asks for that specific upload.
- Known limits of the Drive connector:
  - About 3 MB per file uploaded from a cloud session.
  - The user's Drive can be full.

  If an upload fails for either reason, say which files were not uploaded and why, and ask how to proceed. Don't fall back to sending them in the chat without asking.
