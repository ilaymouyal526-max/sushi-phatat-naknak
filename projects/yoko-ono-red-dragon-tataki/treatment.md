# Yoko Ono — "Red Dragon Tataki" · Director's Cut v2

**Source:** 14.5s AI spot, 16:9, 24fps, no audio. Every shot is locked off, the plate text is burned in, and a torch→chopsticks morph shows at 5.0–5.4s.
**Output:** 13.1s 9:16 master (1080×1920) plus a 4:5 feed cut. No generation credits used: this is all edit and finishing work, done by `finish_v2.py`.

## Structure: fire → craft → reveal, cut on a 96 BPM grid (1 beat = 15 frames)
| Frames | Shot | Camera / speed | Super |
|---|---|---|---|
| 0–30 | Flame macro (hook) | Tight crop; speed ramp 50%→100% | FIRE |
| 30–45 | Torch medium | 2-frame exposure flash cut in | FIRE |
| 45–90 | Hands spread tuna | 80% speed, slow push-in | CRAFT |
| 90–105 | Texture detail | Macro reframe | CRAFT |
| 105–150 | Chopsticks place tuna | 60% slow-mo with frame blending | |
| 150–165 | Crumbs macro | Macro reframe | |
| 165–210 | Sauce drizzle | Lateral slider move | RED DRAGON TATAKI |
| 210–255 | Hero | 50% speed; dolly-in with tilt down, dip to black | RED DRAGON TATAKI |
| 255–315 | Logo | Focus-pull reveal, slow push | ORDER NOW |

The rhythm alternates long and short shots (3 beats, then 1 beat). The AI morph and the burned-in source text are never on screen.

## Techniques that hide the AI feel
- **Virtual camera:** every static shot gets a move (push, slide, dolly/tilt). It also gets handheld weave from layered sine drift of ±2–3 px and a ±0.12° roll.
- **Short takes:** shots last 0.6–1.9s and are cut before AI artifacts build up.
- **Film finish:**
  - Halation on the highlights (red-orange bloom).
  - A filmic S-curve with lifted blacks.
  - Cool shadows and warm mids, plus vibrance.
  - 2px chromatic aberration, a vignette, and temporal luma grain.
- **Practical imperfections:** a warm light leak across the fire section and a flash cut.
- **Sound design,** synthesized because the source is silent:
  - Torch hiss and sear crackle.
  - Spreading texture, chopstick clicks, crumb patter, sauce pour.
  - Room tone.
  - A taiko/rim score locked to the cuts, with a whoosh into a big logo hit.
  - Loudness-normalized to about -15 LUFS.
- **Typography:** Montserrat Light in gold (#D6B26E), widely letter-spaced, with a soft shadow. It sits inside the 4:5 and TikTok UI safe areas.

## Posting notes
- Add a trending sound in the TikTok/Reels editor at about 20% volume under the foley track. Trending audio boosts reach, and the foley keeps it feeling real.
- The platforms will recompress the grain. That's expected and still reads as "shot on camera".
