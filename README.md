# Studio index

**Start here.** Every project lives in `projects/<client-or-product>/`, and every brand's kit lives in `brand/<brand>/`.

## Brand shortcuts: say the name, the files are here
| When the user says | Brand kit (logo, product, how-to, character) |
|---|---|
| Yoko Ono / יוקו אונו / Sushi Push Pop / סושי פוש פופ / Red Dragon Tataki | `brand/yoko-ono/README.md` |

All Higgsfield library media, with IDs and descriptions: `brand/higgsfield-library.md`.

## Projects
Search tip: `grep -ri "<word>" projects/` finds any prompt, job ID, URL or decision.

| Project | Client / product | Status | Final output | Folder |
|---|---|---|---|---|
| Red Dragon Tataki | Yoko Ono (dish) | v3 (painting ending) done | 9:16 13.98s + 4:5 | `projects/yoko-ono-red-dragon-tataki/` |
| Sushi Push Pop: "Anywhere" | Yoko Ono (Sushi Push Pop) | Pre-production; budget in `budget.md` | 9:16 ~15s + 6s cutdown | `projects/sushi-push-pop/` |

## Layout of every project folder
```
projects/<name>/
  brief.md      what the client wants, product facts, references, decisions made
  treatment.md  creative concept + beat sheet / shot list
  budget.md     price checks + package tables
  assets.md     LOG OF EVERY GENERATED OR RECEIVED FILE (see below)
  prompts/      final prompts, one file per shot (shot_01_snow.md ...)
  scripts/      ffmpeg / python build scripts
```

## The asset log rule
Video files (`*.mp4`) are not committed to git, and every cloud session starts from a fresh container.
So anything that matters gets one line in that project's `assets.md`: date, tool + model, job/media ID,
URL, cost, prompt file, and status (`selected` / `rejected` / `raw from client`).
Before asking the user to re-send or re-find anything, check `assets.md` first.

## Shared rules
See `CLAUDE.md` (spending approval is required for every paid generation).
