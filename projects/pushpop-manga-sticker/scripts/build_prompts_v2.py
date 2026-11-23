#!/usr/bin/env python3
"""v2 edits (23.11, user override): the real YOKO ONO sign on the entrance (A2) and the Yoko Ono logo
drawn by AI on the push pop label (A5, B1-B4). Each edit keeps the generated v1 panel as reference 1
and changes only the sign / label. Writes prompts/prompts_v2.json."""
import json, os
from build_prompts import STYLE, MODEL

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = {"A2": "fec4e871-aec2-4515-9aca-e8ee609e087e", "A5": "26b632e0-adcb-44a3-bf1b-88782bbadfbe",
      "B1": "2260f325-2ffc-45aa-a7e4-a4806aa05bde", "B2": "13af2582-97e3-4855-bef5-bb28c04af75f",
      "B3": "6a3a2c5b-d9fb-4842-8e1f-6dbf518bf827", "B4": "780c90fd-b1c1-4cc1-9ba8-0915b624e4d6"}
ASPECT = {"A2": "21:9", "A5": "16:9", "B1": "3:4", "B2": "3:4", "B3": "3:4", "B4": "3:4"}
ENTRANCE_REAL = "ae5a9411-dc77-409c-842d-43a16623c9a6"   # Drive Y176, uncensored
LOGO = "7d756499-c1ca-4655-a534-653fe05df47b"            # design-system gold logo on black

LOGO_DESC = ("the Yoko Ono logo: a tall arched oval line frame with cherry-blossom branches at the top, a "
             "mountain range, the words YOKO ONO with ASIAN KITCHEN under them, and a bowl with chopsticks "
             "over curved waves at the bottom, all in thin gold lines")

KEEP = ("Edit reference 1. Keep EVERYTHING exactly the same: the same drawing, composition, pose, hands, "
        "face, background, lighting, colours and the same Japanese seinen samurai-manga sumi-ink style. ")

LABEL = (KEEP + "Change ONLY the round dark label on the front of the push pop tube: inside its thin gold rim, "
         f"draw {LOGO_DESC}, copied exactly from reference 2, in gold, centred and upright, small and crisp, "
         "following the curve of the tube. No other text, letters or logo anywhere in the image.")

SIGN = (KEEP + "Change ONLY the long blank sign board on the red entrance frame: put the real sign from "
        "reference 2 on it, exactly as in that photo: the letters YOKO ONO spelled exactly Y-O-K-O O-N-O "
        "in the same rounded thin line lettering, with the oval medallion in the middle exactly as in "
        "reference 2 (an arched oval gold frame with cherry blossoms, mountains, a bowl with chopsticks and "
        "waves; reference 3 shows these details clearly). Sign letters and medallion in warm gold on the "
        "dark board, slightly glowing, with a little snow on top of the board. No other text, letters or "
        "logo anywhere in the image.")


def req(i, pid, prompt, medias):
    return {"index": i, "id": pid,
            "params": dict(MODEL, aspect_ratio=ASPECT[pid], prompt=prompt,
                           medias=[{"role": "image_references", "value": m} for m in medias])}


reqs = [req(0, "A2", SIGN, [V1["A2"], ENTRANCE_REAL, LOGO])]
for i, pid in enumerate(["A5", "B1", "B2", "B3", "B4"], start=1):
    reqs.append(req(i, pid, LABEL, [V1[pid], LOGO]))
assert all("No other text" in r["params"]["prompt"] for r in reqs)
assert not any("soy" in r["params"]["prompt"].lower() for r in reqs)
json.dump({"note": "v2 logo edits, approved 23.11: 6 x 0.75 = 4.50 credits", "requests": reqs},
          open(os.path.join(HERE, "..", "prompts", "prompts_v2.json"), "w"), ensure_ascii=False, indent=2)
print(len(reqs), "requests")
