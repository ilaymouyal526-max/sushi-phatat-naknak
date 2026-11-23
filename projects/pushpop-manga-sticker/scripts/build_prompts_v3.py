#!/usr/bin/env python3
"""v3 story extension (23.11, user request). Side A becomes 8 panels:
A1 forest -> A2 entrance (v2) -> A3 the cut (REDO) -> A3b thrown (NEW) -> A3c fallen (NEW)
-> A4 one knee (v1) -> A5 reveal (v2) -> A6 reads the scroll (NEW).

- A3 redo: the chest is closed at the moment of impact; no product, sushi or food anywhere
  (the product is first seen in A5).
- A3b / A3c: he is thrown by the blast and lies on his side.
- A6: he reads the scroll, the hand-off to the how-to steps on side B.

Fixed blocks come from build_prompts.py and appear verbatim. Writes prompts/prompts_v3.json and
prompts/QA_v3.md, and asserts the checks before writing.
Run:  python3 scripts/build_prompts_v3.py
"""
import ast, json, os, re

from build_prompts import (STYLE, COLOUR, NO_TEXT, CHARACTER, PRODUCT, SHRINE, CHEST, LEGEND, MODEL,
                           REF as REF_V1)

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "prompts")
OUT = os.path.join(P, "prompts_v3.json")
QA = os.path.join(P, "QA_v3.md")


def _v2_constant(name):
    """Read a string constant from build_prompts_v2.py without running it (importing it rewrites prompts_v2.json)."""
    tree = ast.parse(open(os.path.join(HERE, "build_prompts_v2.py"), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == name:
            return ast.literal_eval(node.value)
    raise KeyError(name)


LOGO_DESC = _v2_constant("LOGO_DESC")

# ---- references (Higgsfield ids) ----
REF = {
    "samurai": REF_V1["samurai"],                    # a7ea96c5, the corrected ronin-chef + ink style
    "shrine": "b03006ea-566c-4498-8006-6818a992f5eb",  # A4 v1 panel: same hall, parasols, lanterns
    "reveal": "5a6c5675-df4f-4a53-bb85-29c7702fcb2e",  # A5 v2 panel: chest, cushion, scroll, logo label
    "logo": _v2_constant("LOGO"),                      # 7d756499, gold logo on black
}
assert REF["samurai"] == "a7ea96c5-87d2-40b6-b2f5-23ef4b9ad311"
assert REF["logo"] == "7d756499-c1ca-4655-a534-653fe05df47b"

LEGEND_V3 = {
    "samurai": LEGEND["samurai"],  # verbatim from build_prompts.py
    "shrine": ("Reference {n} is the same shrine hall (dark wooden pillars and beams, open paper parasols hanging "
               "from the ceiling, paper lanterns, worn stone floor, shafts of light): use it ONLY for the location "
               "and the lighting; ignore the pose and the figure in it, and ignore its red torii gate and red "
               "altar objects, which must not appear."),
    "reveal": ("Reference {n} is the reveal panel: keep the broken chest, the red display cushion, the rolled "
               "paper scroll with its cord and the push pop with the gold logo on its round label exactly as "
               "they look there; ignore its framing and its black right edge."),
    "logo": ("Reference {n} is the gold Yoko Ono logo: draw it small and crisp, in gold, inside the round label "
             "of the push pop and nowhere else."),
}

FRAMING = ("FRAMING: square image. Keep the samurai, his face, hands and sword, and all the important action "
           "inside the central 70% of the frame; the outer 15% on every side holds only background, energy, "
           "dust or bare paper, because the panel will be cropped to about 5:4 or 4:5.")

NO_RED_BG = ("NO RED IN THE BACKGROUND: there is no gate in this panel. No red torii gates, no red pillars, no "
             "red lanterns, no red altar objects; the whole shrine background is black ink, grey wash and bare "
             "paper.")

# Nothing of the product may be seen before the reveal (A5).
NO_PRODUCT = ("MUST NOT APPEAR: no push pop, no tube, no vial, no bottle, no sushi, no rice, no food of any "
              "kind, no tray, no plate, no bowl, no cushion, no scroll and no object of any kind on, in, beside "
              "or around the chest. The cushion, the push pop label and the sushi and teriyaki colours named in "
              "the colour rule do not appear in this panel.")

# A6 only: the logo on the label is allowed; worded like build_prompts_v2.py.
NO_TEXT_A6 = ("NO TEXT: apart from the Yoko Ono logo inside the round label of the push pop, no text, no "
              "letters, no numbers, no kanji or kana, no seals with characters, no writing visible on the "
              "scroll, no speech bubbles, no sound-effect lettering, no panel borders. No other text, letters "
              "or logo anywhere in the image.")

LABEL_A6 = ("THE LABEL IN THIS PANEL: the round dark label of the push pop is NOT blank here. Inside its thin "
            f"gold rim draw {LOGO_DESC}, copied exactly from reference 4, in gold, centred and upright, small "
            "and crisp, following the curve of the tube. Gold is used only for the label rim and this logo.")

PANELS = [
    dict(id="A3", name="the cut (redo)", sfx="ドン!!", refs=["samurai", "shrine"],
         blocks=["CHARACTER", "SHRINE", "CHEST", "STYLE", "COLOUR"],
         extra=["NO_PRODUCT", "NO_RED_BG", "FRAMING"], no_text="NO_TEXT",
         scene=("PANEL A3 - THE CUT. Inside the shrine, dynamic low angle. The ancient chest is CLOSED and "
                "intact at the moment of impact: its heavy lid is shut, and there is nothing on it, in front of "
                "it or around it. The samurai has drawn his sword and strikes the closed lid in one full diagonal "
                "slash. A thin bright crack splits the lid along the line of the cut, and a violent wave of red "
                "energy bursts out of that slash crack in jagged brush strokes and radiating speed lines; this "
                "red burst is the ONLY colour in the panel. Splinters and ink splatter fly. The red burst fills "
                "the upper half; keep the upper-left quarter, from the corner in toward the centre, free of "
                "detail (red burst and bare paper only) for lettering added later. What is inside the chest "
                "stays hidden.")),
    dict(id="A3b", name="thrown by the blast", sfx=None, refs=["samurai", "shrine"],
         blocks=["CHARACTER", "SHRINE", "STYLE", "COLOUR"],
         extra=["NO_PRODUCT", "NO_RED_BG", "FRAMING"], no_text="NO_TEXT",
         scene=("PANEL A3b - THROWN. Inside the shrine, a split second after the cut. The red energy wave "
                "hurls the samurai backward through the air toward the left of the frame: his body is nearly "
                "horizontal, back first, legs trailing, loose hair whipping around his white headband, the ends "
                "of the headband and his sleeves snapping in the blast, face strained, eyes narrowed, his sword "
                "still gripped in his right hand. Behind him, on the right, a churning wave of red energy with "
                "speed lines and flying wooden splinters drives him away; the chest itself is hidden in the "
                "burst or out of frame. Pillars, hanging parasols and lanterns of the hall behind him, drawn "
                "with ink motion streaks. Red only for the energy wave. No lettering in this panel.")),
    dict(id="A3c", name="fallen on his side", sfx="ズザッ", refs=["samurai", "shrine"],
         blocks=["CHARACTER", "SHRINE", "STYLE", "COLOUR"],
         extra=["NO_PRODUCT", "NO_RED_BG", "FRAMING"], no_text="NO_TEXT",
         scene=("PANEL A3c - FALLEN. He has crashed onto the worn stone floor of the shrine and lies on his "
                "side, slightly right of centre, one arm under him and the other loose, dazed, eyes half closed, "
                "a strand of hair across his face. His sword lies on the floor just beyond his open hand. Dust "
                "and grit are still settling around him in a low ink cloud, and a few thin red wisps of the "
                "energy fade in the air above him (red only for these wisps). The hall behind him is quiet. Keep "
                "the lower-left area as settling dust and bare stone floor, free of detail, for lettering added "
                "later.")),
    dict(id="A6", name="reads the scroll", sfx=None, refs=["samurai", "shrine", "reveal", "logo"],
         blocks=["CHARACTER", "PRODUCT", "SHRINE", "CHEST", "STYLE", "COLOUR"],
         extra=["LABEL_A6", "NO_RED_BG", "FRAMING"], no_text="NO_TEXT_A6",
         scene=("PANEL A6 - THE SCROLL. Inside the shrine, quiet after the storm, medium shot. The samurai "
                "kneels on the stone floor beside the broken chest from reference 3, its lid shattered into "
                "splintered planks, his sword back in its scabbard at his hip. On the red display cushion beside "
                "him (the cushion is the only red) the Sushi Push Pop stands upright, lid closed, teriyaki vial "
                "in place, the gold Yoko Ono logo on its round label. He has untied the cord and unrolls the "
                "paper scroll with both hands at chest height, reading it intently, eyes lowered to the paper, "
                "calm and focused. The written side faces him: we see only the plain back of the paper, or the "
                "scroll is angled away from us, so no writing is visible. The unrolled end of the scroll hangs "
                "down and leads the eye to the left edge of the panel, like a hand-off to the instructions on "
                "the other side. A soft shaft of light falls on the scroll and the push pop. No sushi is visible "
                "outside the closed tube.")),
]

BLOCKS = dict(STYLE=STYLE, COLOUR=COLOUR, NO_TEXT=NO_TEXT, CHARACTER=CHARACTER, PRODUCT=PRODUCT,
              SHRINE=SHRINE, CHEST=CHEST, NO_TEXT_A6=NO_TEXT_A6, NO_PRODUCT=NO_PRODUCT,
              NO_RED_BG=NO_RED_BG, FRAMING=FRAMING, LABEL_A6=LABEL_A6)
FIXED = ["STYLE", "COLOUR", "NO_TEXT", "CHARACTER", "PRODUCT", "SHRINE", "CHEST"]
ASPECT = "1:1"
COST_EACH = 0.75


def build():
    reqs, rows = [], []
    for i, p in enumerate(PANELS):
        legend = [LEGEND_V3[r].format(n=n + 1) for n, r in enumerate(p["refs"])]
        parts = legend + [p["scene"]] + [BLOCKS[b] for b in p["extra"] + p["blocks"] + [p["no_text"]]]
        prompt = "\n".join(parts)
        reqs.append({"index": i, "id": p["id"],
                     "params": dict(MODEL, aspect_ratio=ASPECT, prompt=prompt,
                                    medias=[{"role": "image_references", "value": REF[r]} for r in p["refs"]])})
    return reqs


def check(reqs):
    """Asserts; returns QA rows. Fails loudly before anything is written."""
    by_id = {r["id"]: r for r in reqs}
    assert [r["id"] for r in reqs] == ["A3", "A3b", "A3c", "A6"]
    rows = []
    for p in PANELS:
        r = by_id[p["id"]]
        prm, t = r["params"], r["params"]["prompt"]
        scene = [l for l in t.split("\n") if l.startswith(f"PANEL {p['id']} ")][0]
        done = []
        # model and aspect
        assert {k: prm[k] for k in MODEL} == MODEL == {"model": "gpt_image_2_6", "quality": "low", "resolution": "1k"}
        assert prm["aspect_ratio"] == "1:1"
        assert "central 70%" in t and FRAMING in t
        done.append("model/1:1/central 70%")
        # fixed blocks verbatim (the original text from build_prompts.py)
        for b in p["blocks"]:
            assert BLOCKS[b] in t, f"{p['id']}: block {b} not verbatim"
        assert all(BLOCKS[b] == globals()[b] for b in FIXED)
        done.append("blocks verbatim: " + ", ".join(p["blocks"]))
        # text rule
        if p["id"] == "A6":
            assert NO_TEXT_A6 in t and "No other text, letters or logo anywhere" in t
            assert NO_TEXT not in t
            done.append("NO_TEXT_A6 (logo on label only)")
        else:
            assert NO_TEXT in t, f"{p['id']}: NO_TEXT missing"
            done.append("NO_TEXT verbatim")
        # teriyaki, never soy
        assert not re.search(r"\bsoy\b", t, re.I), f"{p['id']}: says soy"
        # samurai is reference 1 everywhere, shrine ref everywhere
        ids = [m["value"] for m in prm["medias"]]
        assert ids[0] == REF["samurai"] and REF["shrine"] in ids
        assert set(ids) <= set(REF.values()) and len(ids) == len(set(ids)) == len(p["refs"])
        assert all(re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", x) for x in ids)
        for n in range(1, len(ids) + 1):
            assert f"Reference {n} " in t, f"{p['id']}: legend for reference {n} missing"
        assert (REF["reveal"] in ids) == (REF["logo"] in ids) == (p["id"] == "A6")
        assert LEGEND["samurai"].format(n=1) in t
        done.append("refs valid + legend")
        # no red background (v1 shrine ref has a red torii)
        assert NO_RED_BG in t and "torii" in t
        done.append("no red gates in background")
        # product only in A6 (A5 is the first time it is seen)
        if p["id"] == "A6":
            assert PRODUCT in t and LABEL_A6 in t and LOGO_DESC in t and "reference 4" in LABEL_A6
            assert "no writing is visible" in scene and "both hands" in scene
            done.append("product + logo label, scroll back faces viewer")
        else:
            assert PRODUCT not in t and NO_PRODUCT in t
            for w in ["no push pop", "no sushi", "no food", "no tray", "no cushion"]:
                assert w in t, f"{p['id']}: must forbid '{w}'"
            assert "push pop" not in scene.lower() and "sushi" not in scene.lower()
            done.append("no PRODUCT block; forbids push pop/sushi/food/tray/cushion")
        if p["id"] == "A3":
            assert "CLOSED" in scene and "slash crack" in scene
        # sound-effect space
        if p["sfx"]:
            assert "lettering added later" in scene
            where = {"A3": "upper-left quarter", "A3c": "lower-left area"}[p["id"]]
            assert where in scene
            done.append(f"SFX {p['sfx']} space: {where}")
        else:
            assert "lettering added later" not in scene
        rows.append((p["id"], p["name"], p["sfx"] or "-", prm["aspect_ratio"],
                     ", ".join(f"{k} ({REF[k][:8]})" for k in p["refs"]), len(t), "; ".join(done)))
    return rows


def write(reqs, rows):
    total = COST_EACH * len(reqs)
    doc = {"note": (f"v3 story extension: A3 redo + A3b, A3c, A6 new, 1:1, GPT Image 2.6 low 1k. "
                    f"{len(reqs)} x {COST_EACH:.2f} = {total:.2f} credits. Needs user approval before generating."),
           "requests": reqs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    md = ["# Prompt QA v3 (auto-generated by scripts/build_prompts_v3.py)", "",
          "New side A order (8 panels, right to left): A1 forest (keep) > A2 entrance (keep v2) > **A3 the cut (redo)** > "
          "**A3b thrown (new)** > **A3c fallen (new)** > A4 one knee (keep v1) > A5 reveal (keep v2) > **A6 reads the scroll (new)**.", "",
          "| Request | What | Sound (added in code) | Aspect | References | Prompt chars | Checked |",
          "|---|---|---|---|---|---|---|",
          *[f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} |" for a, b, c, d, e, f, g in rows], "",
          f"Model: GPT Image 2.6, low, 1k (MODEL from build_prompts.py). Expected cost: {len(reqs)} x {COST_EACH:.2f} = "
          f"{total:.2f} credits (confirm with estimate_image_cost before generating).", "",
          "## Checks run (asserts in build_prompts_v3.py; the file is only written if all pass)",
          "- Fixed blocks (STYLE, COLOUR, NO_TEXT, CHARACTER, PRODUCT, SHRINE, CHEST, LEGEND, MODEL) imported from build_prompts.py and present verbatim.",
          "- NO_TEXT verbatim in A3, A3b, A3c; A6 uses NO_TEXT_A6, which allows only the logo on the label and ends with \"No other text, letters or logo anywhere in the image.\"",
          "- No 'soy' anywhere (teriyaki only).",
          "- No product before the reveal: A3, A3b and A3c do not contain the PRODUCT block, their scene text never mentions the push pop or sushi, and they carry the MUST NOT APPEAR line (no push pop, no sushi, no food, no tray, no cushion, nothing on/in/around the chest). A3 says the chest is CLOSED and the red bursts out of the slash crack.",
          "- SFX space: A3 keeps the upper-left quarter free (ドン!!); A3c keeps the lower-left area free (ズザッ); A3b and A6 have no sound and no reserved area.",
          "- References: samurai a7ea96c5 is reference 1 in every prompt; shrine b03006ea in all four (location and lighting only); reveal 5a6c5675 and logo 7d756499 only in A6; every reference has a legend line; ids are well-formed UUIDs with no duplicates.",
          "- No red background: every prompt forbids red torii gates and other red in the background (the shrine reference has a red torii).",
          "- Framing: aspect 1:1 and the 'central 70%' instruction in every prompt (layout crops to about 5:4 or 4:5).",
          "- A6: PRODUCT block + logo label (LOGO_DESC read from build_prompts_v2.py), scroll held with both hands and turned so no writing is visible.", "",
          "## Known tensions (worded around, worth an eye check on the results)",
          "- The verbatim COLOUR block still names the \"Yoko gate frame\" and the sushi colours; A3/A3b/A3c add NO_RED_BG and MUST NOT APPEAR to override them.",
          "- The verbatim PRODUCT block says the label is \"blank inside\"; A6 adds LABEL_A6, which says the label is NOT blank in this panel.",
          "- The verbatim CHEST block says \"heavy lid\"; A6's scene says the lid is shattered (as in reference 3).", ""]
    with open(QA, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    return total


if __name__ == "__main__":
    reqs = build()
    rows = check(reqs)
    total = write(reqs, rows)
    for r in rows:
        print(f"{r[0]:4} {r[3]} {r[5]} chars  ok")
    print(f"wrote {os.path.normpath(OUT)} and {os.path.normpath(QA)}: {len(reqs)} requests, {total:.2f} credits")
