# Budget: Sushi Push Pop "Anywhere"

Prices are from Higgsfield `get_cost` (free price checks) on 2026-11-17. Balance at that time: **1,030.75 credits** (Plus plan).
All video prices are for a 5s clip with no AI audio, since sound is designed in post.

## Unit prices
| Model | Settings | Credits / 5s clip | Notes |
|---|---|---|---|
| Kling 3.0 | std, no sound | 7.5 | Cheapest. Start/end frame only, no reference images |
| Kling 3.0 | pro, no sound | 8.75 | Strong motion, good value |
| Seedance 2.0 | fast 720p | 12.5 | Reference images (character + product) |
| Seedance 2.5 | draft 480p | 15 | Draft you can later finalize at full resolution, same result |
| Kling 4.0 | 1080p, image-to-video | 16.25 | 1080p, reference images |
| Seedance 2.0 | std 720p | 22.5 | Higher quality, references |
| Kling 3.0 | 4K, no sound | 30 | Sharpest per credit, start frame only |
| Seedance 2.5 | 720p | 35 | Newest Seedance |
| Seedance 2.0 | std 1080p | 60 | Premium, references |
| Seedance 2.5 | 1080p | 80 | Top tier |
| GPT Image 2.6 | image 9:16 | 0.25 | Start frames, character sheet |
| Nano Banana Pro | image 9:16 | 2 | Best image references / product fidelity |

## Packages (10 shots, 5s each, plus about 12 start-frame images)
| Package | Video | Images | Takes per shot | Estimated total | Fits the balance? |
|---|---|---|---|---|---|
| **A. Test / pitch** | Kling 3.0 std | GPT Image 2.6 | 2 | 10×2×7.5 + 12×3×0.25 = **~159** | ✅ |
| **B. Budget** | Seedance 2.0 fast 720p | Nano Banana Pro | 2 | 250 + 48 = **~298** | ✅ |
| **C. Balanced** ⭐ | Kling 4.0 1080p (walk) + Seedance 2.0 std 720p (product/ASMR) | Nano Banana Pro | 2.5 | 4×2.5×16.25 + 6×2.5×22.5 + 48 = **~548** | ✅ |
| **D. High** | Seedance 2.5: 3 drafts at 480p → finalize the best at 1080p | Nano Banana Pro | 3 drafts + 1 final | 10×(45 + ~80*) + 48 = **~1,298** | ❌ needs a top-up |
| **E. Premium** | Seedance 2.0 std 1080p | Nano Banana Pro | 3 | 10×3×60 + 72 = **~1,872** | ❌ |

\*The finalize price is assumed to equal the 1080p price. Check it with `get_cost` before running.

## Notes
- Generating 4s instead of 5s clips (the minimum on Seedance and Kling 4) should cut video costs by about 20%. Only 1.2–2s of each clip is used anyway.
- "Takes" is an average. Some shots land on the first try, the product macros usually need more.
- Not included: AI music or SFX (price not checked yet) and upscaling (no price check exists, so ask first).
- Style (animated vs photoreal) doesn't change the price. Only the model and resolution do.

## Update 2026-11-17: shortest-possible clips (we only use 1.5–2s of each)
Video is billed per second. Each model has a **minimum length**, so a 1.5–2s clip can't be ordered (only Grok goes down to 2s).

| Model | Min length | Price at min (checked) | Per second | 2s if it were possible |
|---|---|---|---|---|
| Grok Video 1.5 720p | **2s** | 9 | 4.5 | 9 (real) |
| Kling 3.0 std | 3s | 4.5 | 1.5 | 3 |
| Kling 3.0 pro | 3s | 5.25 | 1.75 | 3.5 |
| Kling 3.0 4K | 3s | 18 | 6 | 12 |
| Kling 4.0 1080p | 3s | 9.75 | 3.25 | 6.5 |
| Seedance 2.0 fast 720p | 4s | 10 | 2.5 | 5 |
| Seedance 2.0 std 720p | 4s | 18 | 4.5 | 9 |
| Seedance 2.0 std 1080p | 4s | 48 | 12 | 24 |
| Seedance 2.5 draft 480p | 4s | 12 | 3 | 6 |
| Seedance 2.5 1080p | 4s | 64 | 16 | 32 |

### Packages at minimum length (10 shots)
| Package | Was (5s) | **Now (min length)** | Theoretical floor (2s, not orderable) |
|---|---|---|---|
| A. Kling 3.0 std, 2 takes | 159 | **~99** | ~69 |
| B. Seedance 2.0 fast, 2 takes | 298 | **~248** | ~148 |
| C. Kling 4.0 walk + Seedance 2.0 std product, 2.5 takes | 548 | **~416** | ~248 |
| C+. Same as C, but merged into 8 generations (see below) | — | **~348** | — |
| D. Seedance 2.5: 3 drafts + 1080p final | 1,298 | **~1,048** (final assumed 64) | — |
| E. Seedance 2.0 std 1080p, 3 takes | 1,872 | **~1,512** | ~792 |

**C+ merge:** shots 7+8+9 (click → pop → soy pour → push up) become one continuous 6s macro (27 credits per take), and the arrival + the draw become one clip. That's 8 generations instead of 10.
Calculation: 4×2.5×9.75 + 3×2.5×18 + 2.5×27 + 48 images = **~348**.

## Option G: film it ourselves + Genjutsu (checked 2026-11-18)
Billed by the **length of the source video** we upload. Quotes used library video `e7b9e53c…` (4.0s) and `27fc00f6…` (15.1s).

| Genjutsu mode | What it does | 720p | 1080p |
|---|---|---|---|
| Motion transfer (`hf_mult_motion_control`) | Our filmed motion → the brand kid in a reference image (the image sets the world) | 28 per 4s = **7/s** (15s = 105) | 80 per 4s = **20/s** |
| Object replace (`hf_mult_replace_object`) | Swaps an object or person but **keeps the filmed background**. Source must be 4–30s | 35 per 4s = **8.75/s** | 100 per 4s = **25/s** |

Per second this is more than generating from scratch (Seedance 2.0 std 720p = 4.5/s, Kling 4.0 1080p = 3.25/s).
For this concept the right mode is **motion transfer**, because object replace keeps our real background and we need snow, desert, sea and jungle.

### Packages
| Package | Kid shots (6 × 4s) | Product shots | Images | Total |
|---|---|---|---|---|
| G1. Everything via Genjutsu 720p, 1.5 takes (the motion is fixed, so fewer retries) | 6×1.5×28 = 252 | 2 clips (4s + 6s) via Genjutsu = 1.5×(28+42) = 105 | 48 | **~405** |
| **G2. Hybrid** ⭐: kid via Genjutsu 720p + **product filmed for real** (no AI) | 252 | 0 (real footage + real ASMR sound) | 6 world start frames + 4 background plates ≈ 32 | **~284** |
| G3. Hybrid at 1080p | 6×1.5×80 = 720 | 0 | 32 | **~752** |
