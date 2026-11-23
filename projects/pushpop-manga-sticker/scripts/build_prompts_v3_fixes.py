#!/usr/bin/env python3
"""v3 fixes from review/QA_review.md: B2 and B4 show the wrong product state. Edits of the v2 panels
(logo on label), changing only the product state. Writes prompts/prompts_v3_fixes.json."""
import json, os
from build_prompts import MODEL

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = ("Edit reference 1. Keep EVERYTHING else exactly the same: the same drawing, composition, pose, face, "
        "background, lighting and the same Japanese seinen samurai-manga sumi-ink style, and the same gold logo "
        "on the round label of the tube. ")
B2 = (KEEP + "Change ONLY this: the slim teriyaki vial is NOT attached to the tube any more. Remove it from the "
      "right side of the tube; the clear ring on the lid tab and the round lobe of the black base are empty. "
      "The full vial (frosted clear, black ribbed caps, dark teriyaki inside) lies on its side on the dark "
      "wooden table next to the tube. No other text, letters or logo anywhere in the image.")
B4 = (KEEP + "Change ONLY these things: 1) the teriyaki vial is NOT attached to the tube: remove it from the "
      "right side of the tube completely (it has already been used); the base lobe is empty. 2) Remove the "
      "small second logo above the round label, so the only logo is the one inside the round label. 3) The "
      "sushi roll is pushed clearly higher: about 3 cm of the roll sticks up out of the top of the tube, and "
      "he bites the top of it; his right thumb pushes the black base up from below. 4) The red arrow and the "
      "red bench in the background become black ink; no red anywhere in this panel. No other text, letters "
      "or logo anywhere in the image.")
reqs = [
    {"index": 0, "id": "B2", "params": dict(MODEL, aspect_ratio="3:4", prompt=B2, medias=[
        {"role": "image_references", "value": "6217a8c0-5eeb-4557-a07c-904cf2fca90e"}])},
    {"index": 1, "id": "B4", "params": dict(MODEL, aspect_ratio="3:4", prompt=B4, medias=[
        {"role": "image_references", "value": "ffb7efe5-9a8c-4f59-b454-83e665a10d68"}])},
]
assert not any("soy" in r["params"]["prompt"].lower() for r in reqs)
json.dump({"note": "v3 fixes B2/B4 from QA review, 2 x 0.75", "requests": reqs},
          open(os.path.join(HERE, "..", "prompts", "prompts_v3_fixes.json"), "w"), ensure_ascii=False, indent=2)
print("ok")
