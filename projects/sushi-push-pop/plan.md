# Production plan: "pro on a budget" (2026-11-18)

Based on research into AI ad workflows, hybrid real + AI food ads, and food ASMR hooks.

## Principles a pro follows
1. **Lock the timing before spending.** Build a free animatic (stills + temp sound) in ffmpeg, so we only generate what the cut needs.
2. **Iterate on stills, not video.** A still costs 0.25–2 credits, a video clip 5–50. Approve every keyframe first.
3. **Real wherever it's cheap and better.** The product and the ASMR sound get filmed for real. AI does only what can't be filmed: the kid in the four worlds.
4. **Hook within about 2 seconds.** Food ads open on the sensory moment. So: a 1s cold open of the push pop rising with *tik-tik-POP*, then the journey.
5. **First/last-frame chaining for the world changes.** Identical profile keyframes in every world, then a cheap start→end clip between each pair, with the wipe object (snow, spray, leaves) prompted inside the clip.
6. **Drafts cheap, finals sharp.** Low-res or cheap model for picking takes, upscale only the final selects.
7. **Reuse our own finishing.** The film grade, grain, halation and virtual camera from `projects/yoko-ono-red-dragon-tataki/scripts/finish_v2.py` cost nothing.

## Phases
| Phase | What | Tool | Cost |
|---|---|---|---|
| 0 | Animatic: brand stills + timing + temp SFX | local ffmpeg | 0 |
| 1 | Look test: brand kid, stylized vs photoreal, 2 each | GPT Image 2.6 | ~1 |
| 2 | Character sheet + 12 keyframes (identical profile pose per world, arrival, bite) | Nano Banana Pro, ~2 takes | ~48 |
| 3 | Film the real product macro: vial click, lid pop, soy pour, push up. Phone, close mic, quiet room | phone | 0 |
| 4a | Walk + 4 world transitions: first/last-frame chain, 3s each | Kling 3.0 pro, ~2.5 takes | ~53 |
| 4b | Arrival + draw from bag, 4s | Seedance 2.0 std (or Genjutsu if the motion keeps failing) | ~45 |
| 4c | Bite, 4s | Seedance 2.0 std | ~45 |
| 5 | Product rise with worlds flashing behind it: composite real footage over keyframe backgrounds | local | 0 |
| 6 | Sound design (real ASMR + SFX + music), grade, grain, end card | local | 0 |
| | **Total** | | **~192** (+ optional upscale of finals; price unknown, ask first) |

## Revised opening (hook)
0.0–1.0s: macro of the real push pop rising, *tik-tik-tik → POP*. Hard cut to the snow walk on the beat.
The rest of the treatment follows from there, so the product appears twice: as the hook and as the payoff.
