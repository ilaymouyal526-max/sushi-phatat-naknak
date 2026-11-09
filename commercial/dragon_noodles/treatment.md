# Yoko Ono: "Dragon Wok" (House Wok Noodles)

**Idea:** the dragon from the bar's round sign comes to life. It sears the House Wok Noodles with a blast of fire, devours them, and the video cuts to the menu card.
**Output:** a 9:16 master at 1080×1920, about 13s (10s generated plus a 3s end card).

## Beats
| Time | Shot |
|---|---|
| 0–2s | The noodle bowl in darkness, steam curling, slow push-in, low rumble |
| 2–4s | The dragon descends from the dark above, roars, and its eyes ignite |
| 4–6.5s | A fire blast onto the bowl: wok-hei flames, sizzle, an explosion of embers |
| 6.5–10s | The dragon devours a huge mouthful, smoke curling from its nostrils (lands on the generated end frame) |
| 10–13s | Crossfade to the real menu card with a slow push-in |

## Pipeline
1. **`prep.py` (local, free):** crops the sign's dragon disc (partial grey-world correction removes the red bar light), crops the noodle photo out of the menu card, and builds the 9:16 start frame and the 1080×1920 end card.
2. **End frame:** GPT Image 2.6 (high quality, 2K, 9:16), with the dragon and noodle crops as references.
3. **Video:** Seedance 2.5 `omni_reference`, 10s at 9:16, with sound, between a start frame and the step 2 end frame. A 480p draft comes first, then a 1080p finalize from `draft_job_id`.
4. **`finish.sh` (local, free):** grade, grain and vignette, a 0.8s crossfade into the menu card with a push-in, and audio faded and loudnormed to -15 LUFS.

Higgsfield media: dragon_ref `b4483813-2308-42ce-96c6-7bb418afc0fe`, noodles_ref `376931f5-027c-4efc-96a2-99ea0a9cc7de`, start_frame `c7ea0266-5f0f-4deb-a36a-86e55f4689b1`.

## v1: photoreal (done, draft only)
- End frame: photoreal dragon devouring the bowl, job `3a69b15a-572a-4876-9f98-b80fc77601b7`.
- 480p draft: job `a040244e-5c53-4424-9089-22e946cbe9b3`. All four beats came out in order.
- 1080p finalize: quoted at 160 credits, not approved, not run.

## v2: cartoon / animated-film 3D (the current direction)
**Why:** in the photoreal draft the fire and noodles read as mushy AI texture. A stylised animated-film look gives the fire clean, readable flame shapes and lets the noodles be thick, glossy and bouncy, with exaggerated motion that AI video renders more convincingly than real physics.

**Look:** a high-end stylised 3D animated feature. The dragon keeps the sign's design (golden horns, jewelled silver crown, amber eyes, whisker lanterns, indigo-violet scales) with animated-film proportions: big expressive eyes, a rounded muzzle, a hungry grin.

**Same story and the same gates as v1**, with one change: the start frame is also cartoon (the bowl alone, matching `start_frame.png`'s composition). The clip is then one style end to end, and there's no mid-shot morph from photo to cartoon. The real menu card stays as the ending.

**Animation direction for the video prompt:**
- **Fire:** thick, swirling stylised flame volumes; anticipation (inhale, chest glows) before the blast; flames that wrap around the bowl and curl off in clean shapes.
- **Noodles:** springy squash-and-stretch as the fire hits; strands jumping and wobbling; a long stretchy slurp with a snap-back.
- **Dragon:** smooth arcs and follow-through on the whiskers and lanterns.

### Gates (price-checked 2026-11-09, balance 1,100.5)
| Gate | What | Credits |
|---|---|---|
| 1a | Cartoon end frame, `gpt_image_2_6` high 2K 9:16, refs dragon_ref + noodles_ref | 2.75 |
| 1b | Cartoon start frame, `gpt_image_2_6` high 2K 9:16, refs start_frame + noodles_ref | 2.75 |
| 2 | 480p draft, `seedance_2_5` omni_reference 10s 9:16 with audio, start = 1b, end = 1a, ref = dragon_ref | 30 |
| 3 | 1080p finalize of the chosen draft | Price check after the draft (v1 was 160) |

Each gate needs its own explicit "yes" (see CLAUDE.md). Retries and variants are never automatic.

## Credits spent
| Item | Credits |
|---|---|
| Gold-leaf screen painting (an abandoned style test) | 2.75 |
| v1 photoreal end frame | 2.75 |
| v1 480p draft | 30 |
| v2 cartoon | 0 so far |
