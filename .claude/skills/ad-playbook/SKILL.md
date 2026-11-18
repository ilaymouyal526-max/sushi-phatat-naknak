---
name: ad-playbook
description: "Lessons learned and verified prices for making AI food ads on Higgsfield (Seedance, Kling, Genjutsu) for Yoko Ono / Sushi Push Pop. Use together with sushi-ad-director whenever planning, pricing or generating an ad."
---

# Ad playbook: what we learned (extends `sushi-ad-director`)

Run `sushi-ad-director` for the method (concept → assets → shotlist). This file adds what we verified in practice.

## 0. Before anything
- Brand assets are in `brand/<brand>/README.md`, with Higgsfield media IDs. The full library catalog is `brand/higgsfield-library.md`. **Never ask the user for a logo, product or sticker.** Look there and in `show_medias` (free).
- Spending rule in `CLAUDE.md`: price-check first (`get_cost:true` or `estimate_video_cost`, both free), show the number, wait for a yes.

## 1. Prices (Higgsfield, checked 2026-11-17/18, 9:16). Billing is linear per second
| Model | Credits/second | Min length | Notes |
|---|---|---|---|
| Seedance 2.5 draft 480p | 3 | 4s | Finalize the chosen draft later. Same result |
| Seedance 2.5 720p | 7 | 4s | Multi-shot up to 30s, 30 image references |
| Seedance 2.5 1080p | 16 | 4s | |
| Seedance 2.0 fast 720p | 2.5 | 4s | |
| Seedance 2.0 std 720p | 4.5 | 4s | |
| Seedance 2.0 std 1080p | 12 | 4s | |
| Kling 3.0 std / pro / 4K | 1.5 / 1.75 / 6 | 3s | Start/end frames only, no references |
| Kling 4.0 1080p | 3.25 | 3s | |
| Grok Video 1.5 720p | 4.5 | 2s | Shortest minimum |
| Genjutsu motion transfer 720p / 1080p | 7 / 20 | ? | Billed by the length of the source video |
| Genjutsu object replace 720p / 1080p | 8.75 / 25 | 4s | Keeps the filmed background |
| GPT Image 2.6 / Nano Banana Pro | 0.25 / 2 per image | | |

- **AI audio is free** on Seedance (same price on or off). Always generate diegetic audio. It's raw ASMR/SFX material for the edit.
- You can't order a 1.5s clip. Instead, put several CUTs in one prompt (Seedance 2.5 handles multi-shot up to 30s). Fewer generations, and identity holds better inside one clip.

## 2. Draft → final math
- One draft + one final costs about 18% **more** than going straight to the final. Drafting only pays off when you expect **2+ takes**, which is almost always true for character or physics shots.
- Per final second at 720p: 3 drafts + 1 final = 3×3 + 7 = 16 credits. Seedance 2.0 std with 3 direct takes = 13.5 (cheaper, older model).
- Finalize within 7 days of the draft.

## 3. References (Elements)
- **Separate images beat one collaged grid sheet.** Make a character sheet as 3 separate images (profile / 3/4 / front).
- Put the primary reference first, since earlier references carry more weight. Name it in the prompt and repeat its key traits in words.
- Label what each reference is for.

## 4. Label and product truth
- AI redraws packaging text. When the label must read correctly, **film the real product** (phone, macro, quiet room, so the ASMR is real too) or composite the real label in post.
- In AI product shots: attach @label, keep the label flat to camera, and check the last frame. Warping shows up there most.

## 5. Process that saves credits
1. Animatic first (stills + timing), free in ffmpeg.
2. Look test on stills (GPT Image 0.25).
3. Lock assets as Elements.
4. **High-risk prompts first**, as drafts.
5. Fix a bad shot with Seedance 2.5 `video_edit` / `video_extension` instead of re-rolling the whole prompt.
6. Cut the best seconds from several takes.
7. Finish locally for free: grade, grain, virtual camera (`projects/yoko-ono-red-dragon-tataki/scripts/finish_v2.py`).

## 6. Hooks
- The swipe decision takes about 1.7s. Open on the sensory product moment (pour, crunch, push-up + pop), even if the story starts elsewhere.
- The music drops out for the ASMR beats, then hits on the logo.
