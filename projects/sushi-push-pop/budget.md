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
