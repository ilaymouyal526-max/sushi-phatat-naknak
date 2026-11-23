#!/usr/bin/env python3
"""v4 "the ceremony" (23.11): the boss found v3 too aggressive (sword strike, blast, thrown, fallen).
Same style, calm story. Side A, read right to left:
A1 forest (keep) -> A2 entrance (keep) -> A3 lays down his sword (NEW) -> A3b bows (NEW)
-> A3c opens the lid gently, ギィ (NEW) -> A4 soft light from the chest (NEW)
-> A5 reveal (EDIT: chest intact, lid open) -> A6 reads the scroll (EDIT: chest intact).
Labels are replaced afterwards by scripts/brand_labels.py (real logo), so the edits ignore them.
Writes prompts/prompts_v4.json. Run: python3 scripts/build_prompts_v4.py
"""
import json, os, re

from build_prompts import STYLE, COLOUR, NO_TEXT, CHARACTER, SHRINE, CHEST, LEGEND, MODEL
from build_prompts_v3 import LEGEND_V3, FRAMING, NO_RED_BG, NO_PRODUCT

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "prompts", "prompts_v4.json")

REF = {
    "samurai": "a7ea96c5-87d2-40b6-b2f5-23ef4b9ad311",
    "shrine": "b03006ea-566c-4498-8006-6818a992f5eb",
    "chest": "589f77fa-f2cd-4a53-8fae-224db8740cda",    # A3 v3: the closed chest on its stone altar
    "reveal": "5a6c5675-df4f-4a53-bb85-29c7702fcb2e",   # A5 v2 (to edit)
    "scroll": "74cbbe08-5dcd-4fed-b0b9-9b1d42d6aae9",   # A6 v3 (to edit)
}
LEGEND_CHEST = ("Reference {n} shows the ancient chest on its low stone altar: use it ONLY for the shape of the "
                "chest and altar; ignore the red energy, the sword strike and the pose, which must not appear.")
CALM = ("MOOD: calm, silent and respectful, like a tea ceremony. No violence, no attack, no weapon drawn, no "
        "explosion, no energy wave, no speed lines, no flying debris, no ink splatter bursts.")
NO_RED_AT_ALL = ("NO RED: there is no red anywhere in this panel (no energy, no gate, no cushion); only black "
                 "ink, grey wash and bare cream paper.")
LIGHT = ("THE LIGHT: soft white light drawn as bare cream paper and fine radiating ink hatching against grey "
         "wash; never coloured, never gold.")

NEW = [
    ("A3", "lays down his sword", ["samurai", "shrine", "chest"], None,
     "PANEL A3 - THE SWORD. Inside the shrine, before the low stone altar with the CLOSED ancient chest. Close "
     "shot: the samurai, kneeling, lays his sheathed sword horizontally on the stone floor in front of him with "
     "both hands, slowly, as a sign of respect. Eyes lowered. The closed chest is behind, slightly out of focus."),
    ("A3b", "bows", ["samurai", "shrine", "chest"], None,
     "PANEL A3b - THE BOW. Medium-wide shot from the side: he kneels in seiza on the stone floor before the "
     "altar and bows deeply, back straight, head low, both hands flat on the floor in front of his knees; his "
     "sheathed sword lies on the floor before him. The closed chest rests on the altar ahead of him. Shafts of "
     "light and drifting dust. Complete stillness."),
    ("A3c", "opens the lid gently", ["samurai", "shrine", "chest"], "upper-left",
     "PANEL A3c - THE LID. Close-up of his two hands on the heavy lid of the closed chest, lifting it slowly and "
     "carefully a few centimetres. A thin line of soft white light spills out of the gap and lights his fingers "
     "and the old iron fittings. Nothing inside can be seen yet. Keep the upper-left area as quiet grey wash, "
     "free of detail, for lettering added later."),
    ("A4", "the light", ["samurai", "shrine", "chest"], None,
     "PANEL A4 - THE LIGHT. The lid is open. Soft white light rises out of the open chest and lights his face "
     "from below; he leans in slightly and looks inside with calm, quiet wonder, eyes open, serene. We do not "
     "see what is inside the chest (the open lid and the rim hide it). The hall around him is dim."),
]

EDIT_KEEP = ("Edit reference 1. Keep EVERYTHING else exactly the same: the same drawing, composition, pose, "
             "face, lighting, the push pop, the red cushion, the scroll and the same Japanese seinen "
             "samurai-manga sumi-ink style. ")
EDITS = [
    ("A5", "reveal, chest intact", "reveal", "16:9",
     EDIT_KEEP + "Change ONLY the chest: it is intact, not broken. Its heavy wooden lid is opened and rests "
     "back on its hinges, whole and undamaged. Remove every splinter, broken plank and shattered edge; the "
     "chest walls are solid antique lacquered wood with iron corner fittings. No other text, letters or logo "
     "anywhere in the image."),
    ("A6", "reads the scroll, chest intact", "scroll", "1:1",
     EDIT_KEEP + "Change ONLY the chest beside him: it is intact, not broken, its heavy wooden lid opened and "
     "resting back on its hinges, whole and undamaged. Remove every splinter, broken plank and shattered edge. "
     "No other text, letters or logo anywhere in the image."),
]


def legend(refs):
    out = []
    for i, r in enumerate(refs, start=1):
        t = {"samurai": LEGEND["samurai"], "shrine": LEGEND_V3["shrine"], "chest": LEGEND_CHEST}[r]
        out.append(t.format(n=i))
    return out


def build():
    reqs = []
    for i, (pid, name, refs, sfx_area, scene) in enumerate(NEW):
        parts = legend(refs) + [scene, CALM, NO_PRODUCT, NO_RED_AT_ALL, NO_RED_BG, LIGHT, FRAMING,
                                CHARACTER, SHRINE, CHEST, STYLE, COLOUR, NO_TEXT]
        reqs.append({"index": i, "id": pid, "name": name, "params": dict(
            MODEL, aspect_ratio="1:1", prompt="\n".join(parts),
            medias=[{"role": "image_references", "value": REF[r]} for r in refs])})
    for j, (pid, name, src, ar, prompt) in enumerate(EDITS, start=len(NEW)):
        reqs.append({"index": j, "id": pid, "name": name, "params": dict(
            MODEL, aspect_ratio=ar, prompt=prompt, medias=[{"role": "image_references", "value": REF[src]}])})
    return reqs


def check(reqs):
    for r in reqs:
        t, pid = r["params"]["prompt"], r["id"]
        assert not re.search(r"\bsoy\b", t, re.I), pid
        scene = [l for l in t.split("\n") if l.startswith("PANEL") or l.startswith("Edit")]
        assert scene and not re.search(r"\b(strike|slash|explod|thrown|blast|attack)\w*", scene[0], re.I), pid
        assert r["params"]["model"] == "gpt_image_2_6" and r["params"]["quality"] == "low"
        if pid in {"A3", "A3b", "A3c", "A4"}:
            for blk in (STYLE, COLOUR, NO_TEXT, CHARACTER, SHRINE, CHEST, NO_PRODUCT, CALM, NO_RED_AT_ALL):
                assert blk in t, (pid, blk[:30])
        else:
            assert "No other text" in t and "intact" in t
    assert "lettering added later" in reqs[2]["params"]["prompt"]   # space for ギィ
    return True


if __name__ == "__main__":
    reqs = build(); check(reqs)
    json.dump({"note": "v4 'the ceremony': 4 new + 2 edits, 6 x 0.75 = 4.50 credits", "requests": reqs},
              open(OUT, "w"), ensure_ascii=False, indent=2)
    for r in reqs:
        print(r["id"], r["name"], r["params"]["aspect_ratio"], [m["value"][:8] for m in r["params"]["medias"]],
              len(r["params"]["prompt"]))
