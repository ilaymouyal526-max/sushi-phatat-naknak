#!/usr/bin/env python3
"""Build prompts/prompts.json for the Push Pop manga sticker (9 panels).

The character, style, colour, product, shrine and chest descriptions are FIXED BLOCKS.
Every prompt is assembled from them, so they repeat word for word.
Run:  python3 scripts/build_prompts.py   (then scripts/check_prompts.py)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "prompts", "prompts.json")

# ---- references (Higgsfield ids) ----
REF = {
    "samurai": "a7ea96c5-87d2-40b6-b2f5-23ef4b9ad311",   # job, GPT Image 2.6, 23.11 - the corrected ronin-chef
    "entrance": "2b2fa7d5-f56b-4455-8c2e-0513f307d93a",  # media, Drive Y176 with the sign letters blanked
    "sushi": "a3556baa-052d-480e-87fc-fc4718ebfc50",     # job, 18.11 step 2 - the roll inside the tube
}

MODEL = {"model": "gpt_image_2_6", "quality": "low", "resolution": "1k"}  # same settings as a7ea96c5 (0.75 cr)

# ---- fixed blocks (verbatim in every prompt that uses them) ----
STYLE = ("ART STYLE: Japanese seinen samurai-manga ink illustration. Expressive sumi brush linework with "
         "dry-brush edges and strongly varying line weight, realistic adult anatomy, fine-pen cross-hatching "
         "in the shadows, sparse grey ink wash, generous bare cream washi paper, a few ink splatters, calm "
         "intense mood. No screentone, no chibi, no sparkles, no cute elements.")

COLOUR = ("COLOUR: black ink only on cream washi paper, with exactly these exceptions and nothing else: deep "
          "vermilion red ONLY for the Yoko gate frame, the red energy wave and the red display cushion; a thin "
          "gold rim ONLY on the round label of the push pop; the natural colours of the sushi (white rice, black "
          "sesame, orange salmon, green avocado) and the dark glossy brown of teriyaki sauce. Everything else, "
          "including lanterns, snow, wood, stone and clothing, is black ink, grey wash or bare paper.")

NO_TEXT = ("NO TEXT: no text, no letters, no numbers, no kanji or kana, no seals with characters, no logo, no "
           "writing on signs, no speech bubbles, no sound-effect lettering, no panel borders.")

CHARACTER = ("THE SAMURAI (match reference 1 exactly): a Japanese ronin-chef in his 30s, long black hair in a "
             "rough topknot, white cloth headband, light stubble, lean and strong, indigo-black kimono with a "
             "tasuki cord tying back the sleeves, narrow focused eyes, serious calm face. Same face and costume "
             "in every panel.")

PRODUCT = ("THE SUSHI PUSH POP (exact real proportions): a matte black paperboard tube 4.5 cm wide and about "
           "19 cm tall (about 1 to 4.2), clearly taller than the hand that holds it. A slim frosted-clear "
           "teriyaki vial runs along the RIGHT side for the full height of the tube, black ribbed caps at both "
           "ends, filled with dark glossy teriyaki sauce. A clear plastic lid sits flush with the top rim; a "
           "small clear tab sticks out from the lid and ends in a ring that grips the vial's top cap. A black "
           "plastic base cap with a round lobe on the right cradles the vial's bottom cap. On the front, a round "
           "dark label with a thin gold rim, blank inside.")

SHRINE = ("INSIDE THE YOKO SHRINE: a dim ancient Japanese shrine hall, thick dark wooden pillars and beams, old "
          "paper parasols hanging open from the high ceiling, hanging paper lanterns, worn stone floor, drifting "
          "dust in shafts of light.")

CHEST = ("THE ANCIENT CHEST: a knee-high antique lacquered wooden chest with iron corner fittings and a heavy "
         "lid, standing alone on a low stone altar.")

LEGEND = {
    "samurai": "Reference {n} is the exact samurai and the exact ink style to keep; ignore its background and counter.",
    "samurai_style": "Reference {n} is for the ink style and the product only; the samurai does not appear in this panel.",
    "entrance": ("Reference {n} is the real Yoko Ono entrance: copy its structure (red torii-style frame, metal "
                 "roof with a row of bulbs, long sign board with a round medallion in the middle, glass doors, two "
                 "stone lanterns on short railings) and redraw it in ink; the sign board stays blank."),
    "sushi": "Reference {n} is for the sushi roll and the tube only (rice, sesame, salmon, avocado); ignore the pose.",
}

PANELS = [
    # ---------------- SIDE A: the story, read right to left ----------------
    dict(id="A1", side="A", name="the forest", sfx=None, aspect="21:9",
         refs=["samurai"], blocks=["CHARACTER", "STYLE", "COLOUR"],
         scene=("PANEL A1 - THE FOREST. Wide cinematic shot from behind and slightly above: the samurai walks "
                "away from the camera, alone, through deep snow between towering straight cedar trees, leaving a "
                "line of footprints. His frozen breath shows as a pale puff of vapour beside his head. Falling "
                "snow is drawn as bare-paper flecks against grey wash. Silent, cold, vast. He is small, in the "
                "centre-right third; the cedars frame both sides. No red and no gold in this panel.")),
    dict(id="A2", side="A", name="the entrance", sfx="ザッ", aspect="21:9",
         refs=["samurai", "entrance"], blocks=["CHARACTER", "STYLE", "COLOUR"],
         scene=("PANEL A2 - THE ENTRANCE. Wide shot: between snow-laden cedar trees, half hidden in the snow, "
                "stands the entrance from reference 2, redrawn in sumi ink. The torii-style wooden frame is the "
                "ONLY red in this panel. Above it a corrugated metal roof with a row of small bulbs along its edge. "
                "Across the frame a long BLANK sign board with only the round oval medallion in its middle. The "
                "dark glass doors stand open onto pitch darkness. Two stone lanterns on short railings on either "
                "side, with round ornaments on the railings, all in black ink. Thick snow on the roof and on the "
                "lanterns. The samurai, small, seen from behind in the lower right, takes one step toward the "
                "doors, snow crunching under his straw sandal. Keep the upper-left sky as quiet grey wash for "
                "lettering added later.")),
    dict(id="A3", side="A", name="the cut", sfx="ドン!!", aspect="4:5",
         refs=["samurai"], blocks=["CHARACTER", "SHRINE", "CHEST", "STYLE", "COLOUR"],
         scene=("PANEL A3 - THE CUT. Inside the shrine, dynamic low angle. The samurai has drawn his sword and "
                "strikes the ancient chest in one full diagonal slash. At the point of impact a violent wave of "
                "red energy explodes out of the chest in jagged brush strokes and radiating speed lines; this red "
                "burst is the ONLY colour in the panel. Splinters and ink splatter fly. The red burst fills the "
                "upper half; keep the upper-left quarter free of detail (red burst and bare paper only) for "
                "lettering added later.")),
    dict(id="A4", side="A", name="the landing", sfx="ズザッ", aspect="4:5",
         refs=["samurai"], blocks=["CHARACTER", "SHRINE", "STYLE", "COLOUR"],
         scene=("PANEL A4 - THE LANDING. The blast has thrown him backward; he lands perfectly on one knee, "
                "sliding on the stone floor, his sword back in its scabbard at his hip and his right hand resting "
                "on the hilt, head up, calm, eyes fixed on the chest out of frame to the right. A few fading wisps "
                "of the red energy trail behind him (red only for these wisps). Dust and grit spray from his "
                "sliding knee across the lower left; keep the lower-left third as dust spray and bare floor, free "
                "of detail, for lettering added later.")),
    dict(id="A5", side="A", name="the reveal", sfx="ゴゴゴ", aspect="16:9",
         refs=["samurai_style", "sushi"], blocks=["CHEST", "PRODUCT", "STYLE", "COLOUR"],
         scene=("PANEL A5 - THE REVEAL. Close shot looking into the shattered chest: its heavy lid is broken "
                "into splintered planks. Inside, on a plush red display cushion like a jeweller's ring cushion "
                "(the cushion is the only red), the Sushi Push Pop stands upright, lid closed, teriyaki vial in "
                "place, sharp and perfect, lit from above as if sacred. Beside it lies a rolled paper scroll tied "
                "with a cord, blank, its end pointing out of the panel to the left. Dust motes in a shaft of light. "
                "Keep a vertical strip along the right edge as deep shadow, free of detail, for lettering added "
                "later. No person in this panel.")),
    # ---------------- SIDE B: how to use it, inside the shrine ----------------
    dict(id="B1", side="B", name="step 1: take out the teriyaki", sfx=None, aspect="3:4",
         refs=["samurai", "sushi"], blocks=["CHARACTER", "PRODUCT", "SHRINE", "STYLE", "COLOUR"],
         scene=("PANEL B1 - STEP 1, TAKE OUT THE TERIYAKI. Medium close-up at a low dark wooden altar table "
                "inside the shrine (the shrine only lightly suggested behind him). He stands the push pop upright "
                "on the table, steadies the tube with his left hand, and with his right thumb and fingers slides "
                "the teriyaki vial out of the lid ring and the base lobe, away to the right. The lid is still "
                "closed. Eyes lowered, total focus, like drawing a blade. The vial and his fingers are the "
                "sharpest point. Keep the top-right corner as empty washi paper for a number seal.")),
    dict(id="B2", side="B", name="step 2: open the lid", sfx=None, aspect="3:4",
         refs=["samurai", "sushi"], blocks=["CHARACTER", "PRODUCT", "SHRINE", "STYLE", "COLOUR"],
         scene=("PANEL B2 - STEP 2, OPEN THE LID. The vial is already out and lies on the altar table. He holds "
                "the tube upright at chest height in his left hand and with his right hand lifts the round clear "
                "lid (with its small tab and ring) straight up off the top, revealing the top of the roll inside: "
                "white rice with black sesame, orange salmon and green avocado in the centre, exactly like "
                "reference 2. Three-quarter view from slightly above, quiet satisfied focus. Keep the top-right "
                "corner as empty washi paper for a number seal.")),
    dict(id="B3", side="B", name="step 3: add teriyaki", sfx=None, aspect="3:4",
         refs=["samurai", "sushi"], blocks=["CHARACTER", "PRODUCT", "SHRINE", "STYLE", "COLOUR"],
         scene=("PANEL B3 - STEP 3, ADD TERIYAKI. The lid is off. He holds the open tube upright in his left "
                "hand and with his right hand tips the uncapped teriyaki vial over it, pouring a thin glossy "
                "stream of dark brown teriyaki onto the top of the roll, which glistens. Close, slightly from "
                "above. Keep the top-right corner as empty washi paper for a number seal.")),
    dict(id="B4", side="B", name="step 4: push up and enjoy", sfx=None, aspect="3:4",
         refs=["samurai", "sushi"], blocks=["CHARACTER", "PRODUCT", "SHRINE", "STYLE", "COLOUR"],
         scene=("PANEL B4 - STEP 4, PUSH UP AND ENJOY. He holds the tube upright in his left hand and pushes the "
                "black base up from below with his right thumb; the roll has risen about 3 cm out of the top of "
                "the tube, glossy with teriyaki. He takes a bite from the top, eyes closed for a moment in quiet "
                "satisfaction. Keep the top-right corner as empty washi paper for a number seal.")),
]

BLOCKS = dict(STYLE=STYLE, COLOUR=COLOUR, NO_TEXT=NO_TEXT, CHARACTER=CHARACTER, PRODUCT=PRODUCT,
              SHRINE=SHRINE, CHEST=CHEST)


def build():
    items = []
    for p in PANELS:
        legend = [LEGEND[r].format(n=i + 1) for i, r in enumerate(p["refs"])]
        parts = legend + [p["scene"]] + [BLOCKS[b] for b in p["blocks"]] + [NO_TEXT]
        prompt = "\n".join(parts)
        medias = [{"role": "image_references", "value": REF[r.split("_")[0]]} for r in p["refs"]]
        items.append({
            "id": p["id"], "side": p["side"], "name": p["name"], "sfx": p["sfx"],
            "refs": p["refs"], "blocks": p["blocks"] + ["NO_TEXT"],
            "params": dict(MODEL, aspect_ratio=p["aspect"], medias=medias, prompt=prompt),
        })
    doc = {"project": "pushpop-manga-sticker", "updated": "2026-11-23",
           "refs": REF, "blocks": BLOCKS, "panels": items,
           # what generate_image_batch takes, ready to pass by sandbox ref or copy
           "requests": [{"index": i, "params": it["params"]} for i, it in enumerate(items)]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("wrote", os.path.normpath(OUT), len(items), "panels")


if __name__ == "__main__":
    build()
