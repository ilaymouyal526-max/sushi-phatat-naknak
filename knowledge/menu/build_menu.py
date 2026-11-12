#!/usr/bin/env python3
"""Single source for the menu-to-photo matching. Run it to regenerate menu.json and MENU.md.
match: exact = the same dish as served today; close = same dish, different plating/coating/name, or a near stand-in; none = no photo."""
import json
S = []
def sec(name, en, note=""): S.append({"section": name, "en": en, "note": note, "items": []})
def it(he, price, hero=None, alts="", match="none", note="", en=""):
    S[-1]["items"].append({"he": he, "en": en, "price": price, "hero": hero, "alts": alts.split() if alts else [], "match": match if hero else "none", "note": note})

sec("לפתיחה או לחלוקה", "Starters")
it("אדממה", "22", "Y333", "Y108", "exact", "", "Edamame")
it("קימצ'י", "21", en="Kimchi", note="Only the 3D-tray kimchi mesh exists")
it("מרק מיסו", "25", en="Miso soup")
it("מרק טום יאם", "49", en="Tom yum soup")
it("נמס עוף (2)", "39", "Y009", "Y007", "exact", "", "Chicken nems")
it("נמס צמחוני (2)", "36", "Y009", "", "close", "The photo is the chicken nems; they look the same", "Veggie nems")
it("גיוזה עוף / בקר (4)", "55 / 59", "Y049", "Y017 Y062 Y073 Y078 Y032 Y334 Y335 Y336", "exact", "Y334-336: in a bamboo steamer", "Gyoza")
it("באן באו אסאדו (2)", "49", "Y307", "", "exact", "", "Asado bao")
it("באן באו עוף (2)", "46", "Y014", "Y029 Y046 Y060", "exact", "", "Crispy chicken bao")
it("באן באו דג לבן טמפורה (2)", "46", "Y014", "", "close", "Stand-in: the chicken bao looks almost the same", "White fish bao")
it("שרימפס בטמפורה, זהבנון (4)", "49", "Y065", "Y020 Y037 Y053 Y074", "close", "Shot as 'shrimp crispy coco'. Looks right, but check it is the same coating", "Tempura 'shrimp'")
it("סלט פפאיה ואגוזי קשיו", "42", en="Papaya and cashew salad")

sec("רולים מיוחדים", "Special rolls", "8 pieces; no changes; soy wrap +7")
it("קוויאר סלמון רול", "72", "Y393", "Y394", "exact", "Seared salmon wrap with smoked tobiko", "Caviar Salmon Roll")
it("ספיישל יונו", "75", "Y313", "", "close", "Rolls topped with salmon tartare and tobiko", "Special Yono")
it("מיסו סלמון", "75", "Y416", "", "close", "Seared salmon wrap with sauce; shot as 'Tataki salmon roll'", "Miso Salmon")
it("קרייזי רול", "75", "Y324", "Y325 Y326", "close", "Shot as a rainbow wrap (salmon, tuna, white fish, avocado); today it's salmon and mango", "Crazy Roll")
it("ספיישל קריספי וג'י", "59", "Y422", "Y254 Y255 Y256", "close", "Y422: avocado and mango wrap with crispy shallot; shot as 'Veggie roll'", "Special Crispy Veggie")
it("ספיישל סלמון מבושל", "65", "Y114", "Y115", "close", "Avocado wrap with a crispy top; not named in the shoot", "Special Cooked Salmon")
it("ספיישל סורימי רול", "59", en="Special Surimi Roll", note="No photo of a mango-wrapped surimi roll")
it("רד דרגון טונה טטאקי", "79", "Y412", "Y415 Y337 Y338", "close", "Avocado wrap with seared tuna on top. Higgsfield has the Red Dragon ad too", "Red Dragon Tuna Tataki")
it("פיור וויט טמפורה", "65", "Y425", "Y414 Y426", "exact", "Avocado wrap with the truffle-aioli dollop", "Pure White Tempura")
it("וולקנו סלמון / טונה (4)", "69 / 79", "Y424", "Y423 Y111 Y112", "close", "The photo is the salmon version, salmon-wrapped; today's is avocado-wrapped", "Volcano")

sec("רולים קלאסיים", "Classic rolls", "8 pieces; push-pop version +12; soy wrap +7. The 2024 photos are all sesame-coated inside-out rolls on blue plates")
it("סלמון אבוקדו (פנקו)", "45", "Y308", "", "close", "Today it's panko-coated; the photo is sesame", "Salmon Avocado")
it("סלמון צ'יז אבוקדו (פנקו)", "49", en="Salmon Cheese Avocado")
it("ספייסי סלמון (שומשום)", "45", "Y309", "", "exact", "", "Spicy Salmon")
it("טונה אדומה אבוקדו (פנקו)", "59", "Y311", "", "close", "Today it's panko-coated; the photo is sesame", "Red Tuna Avocado")
it("ספייסי טונה (פנקו)", "59", "Y310", "", "close", "Today it's panko-coated; the photo is sesame", "Spicy Tuna")
it("סלמון מבושל (שומשום)", "48", en="Cooked Salmon")
it("טטאקי טונה (פנקו)", "59", en="Tuna Tataki")
it("טטאקי סלמון (פנקו סגול)", "52", en="Salmon Tataki")
it("טונה מיונז (שומשום)", "42", "Y312", "", "exact", "", "Tuna Mayo")
it("ירקות (פנקו סגול)", "35", "Y250", "Y249 Y251 Y252 Y253", "close", "The photo is an avocado and cucumber roll without purple panko", "Veggie")
it("ספייסי סורימי (שומשום)", "48", en="Spicy Surimi")

sec("טטאקי", "Tataki")
it("סלמון טטאקי (6)", "69", "Y417", "Y418 Y419 Y420", "exact", "Y419-420: with an ikura spoon", "Salmon Tataki")
it("טונה אדומה טטאקי (6)", "79", "Y421", "Y038 Y044 Y058 Y066 Y068", "close", "Shot in an orange broth; today it's served on avocado and asparagus", "Red Tuna Tataki")

sec("סשימי", "Sashimi")
it("סשימי סלמון (6)", "49", "Y146", "Y145", "close", "Salmon rosettes on a sashimi plate", "Salmon Sashimi")
it("סשימי טונה אדומה (6)", "69", "Y406", "Y003 Y026 Y057 Y407 Y408 Y409", "exact", "", "Red Tuna Sashimi")
it("סשימי רויאל (10)", "98", "Y397", "Y395 Y396 Y398 Y399 Y400 Y401 Y402 Y143 Y144", "exact", "Salmon, tuna and white fish on ice", "Sashimi Royal")

sec("ספיישל מטוגנים", "Fried specials")
it("קריספי רייס טונה אדומה (4)", "59", "Y330", "Y329 Y331 Y332", "exact", "", "Crispy Rice Red Tuna")
it("קריספי רייס סלמון (4)", "52", "Y328", "Y327", "exact", "", "Crispy Rice Salmon")
it("קריספי רייס סלמון טטאקי (4)", "55", "Y327", "", "close", "Stand-in: the salmon crispy rice", "Crispy Rice Salmon Tataki")
it("פנקו רול", "64", "Y358", "Y359", "exact", "", "Panko Roll")
it("פנקו רול ירקות", "55", "Y359", "", "close", "Stand-in: the salmon panko roll", "Veggie Panko Roll")
it("קריספי פיז'טה סלמון (2)", "59", "Y097", "Y096 Y098", "close", "Crispy rice slab with salmon and ikura; not named in the shoot", "Crispy Pizzetta Salmon")
it("קריספי פיז'טה טונה אדומה כמהין", "69", en="Crispy Pizzetta Tuna Truffle")
it("קריספי פיז'טה טונה מיונז", "59", en="Crispy Pizzetta Tuna Mayo")

sec("מאקי", "Maki", "8 pieces")
it("מאקי סלמון מלפפון", "32", "Y339", "Y340", "exact", "", "Salmon Maki")
it("מאקי טונה אדומה מלפפון", "39", "Y342", "", "exact", "", "Red Tuna Maki")
it("מאקי טונה מיונז מלפפון", "32", "Y341", "", "exact", "", "Tuna Mayo Maki")
it("מאקי צמחוני", "26", "Y343", "", "exact", "", "Veggie Maki")

sec("פנסי טמאקי", "Fancy temaki", "1 or 3 pieces. Nothing photographed")
for he, p, en in [("טמאקי סלמון", "26 / 59", "Salmon Temaki"), ("טמאקי טונה אדומה", "29 / 69", "Red Tuna Temaki"), ("טמאקי סורימי", "29 / 66", "Surimi Temaki"), ("טמאקי קריספי שרימפס", "29 / 66", "Crispy Shrimp Temaki"), ("טמאקי דג לבן טמפורה", "29 / 66", "White Fish Temaki"), ("פנסי טמאקי (3)", "68", "Fancy Temaki x3")]:
    it(he, p, en=en)

sec("טרטר יפני וצ'יראשי", "Japanese tartare and chirashi")
it("סלמון טרטר", "78", "Y379", "Y378 Y380", "exact", "", "Salmon Tartare")
it("טרטר טונה אדומה", "98", en="Red Tuna Tartare")
it("טרטר טונה מיונז", "72", en="Tuna Mayo Tartare")
it("רויאל צ'יראשי", "95", "Y318", "Y314 Y315 Y316 Y317 Y319 Y320", "exact", "", "Royal Chirashi")

sec("ניגירי", "Nigiri", "2 or 3 pieces")
it("ניגירי סלמון", "29 / 39", "Y351", "Y001 Y347 Y348 Y349 Y350", "exact", "Y347-351: with a sauce pour", "Salmon Nigiri")
it("ניגירי טונה אדומה", "34 / 49", "Y041", "Y002 Y025 Y352", "exact", "", "Red Tuna Nigiri")
it("ניגירי טונה אדומה וכמהין", "42 / 59", en="Red Tuna Truffle Nigiri")
it("ניגירי סלמון צרוב", "31 / 41", en="Seared Salmon Nigiri")
it("ניגירי טונה אדומה צרובה", "36 / 51", en="Seared Red Tuna Nigiri")
it("ניגירי דניס צרוב", "34 / 46", en="Seared Sea Bream Nigiri")

sec("סלטים", "Salads")
it("סלט גולדן נמס", "58 / 64", en="Golden Nems Salad")
it("סלט אסייתי עוף / שרימפס קריספי", "69 / 79", "Y381", "Y382 Y241 Y248 Y259 Y260 Y261", "exact", "Y259-261: with crispy pieces, good for the shrimp version", "Asian Salad")
it("סלט סשימי בול", "79", "Y385", "Y384 Y386 Y387 Y388 Y389 Y390 Y391 Y102 Y103 Y104 Y403 Y404 Y405", "exact", "Y403-405: black sesame pour", "Sashimi Bowl Salad")
it("סלט עוף קראנץ' מלפפונים", "49", "Y243", "Y242 Y392", "close", "Chicken and cucumber salad; the photo also has tomato", "Crunchy Chicken Cucumber Salad")

sec("ווק פארטי", "Wok Party", "Spicy option +8")
it("נודלס הבית: עוף / טמפורה / צמחוני", "69 / 72 / 59", "Y010", "Y011 Y033 Y050 Y355 Y356", "exact", "", "House Wok Noodles")
it("נודלס חמוץ מתוק אננס וקשיו", "72 / 75 / 62", "Y011", "", "close", "Stand-in: the house noodles; no pineapple in the photo", "Sweet & Sour Noodles")
it("עוף קרמל בטמפורה", "72", "Y005", "Y006 Y028", "close", "Shot as 'chicken lemon': glazed crispy chicken with rice", "Caramel Tempura Chicken")
it("עוף בטמפורה ג'נרל טאו", "72", "Y016", "Y031 Y048 Y061 Y072", "exact", "", "General Tao Chicken")
it("עוף חמוץ מתוק אננס וקשיו", "75", "Y031", "", "close", "Stand-in: General Tao", "Sweet & Sour Chicken")
it("תוספת: אורז / אורז סושי / סלט תאילנדי", "19", en="Sides")

sec("קומבינציות", "Combinations", "Party trays: Y303-306, Y099; Drive folder 'יוקומגשים'; the 3D trays project")
for he, p, en in [("מיקס מבושלים (24)", "125", "Cooked Mix"), ("מיאמי (22)", "135", "Miami"), ("סופר קליפורניה (32)", "170", "Super California"), ("פול ניגירי סלמון (10)", "129", "Full Salmon Nigiri"), ("דלוקס (32)", "219", "Deluxe"), ("פלטת השף (28)", "259", "Chef's Platter")]:
    it(he, p, "Y303", "Y304 Y305 Y306", "close", "The party-tray photos are not one specific combination", en)

sec("משקאות", "Drinks")
it("קוקה קולה / זירו / ספרייט זירו / פנטה / פוזטי", "15", "Y116", "Y117 Y118 Y120 Y125", "exact", "Bottles on a grey backdrop", "Soft drinks")
it("מיצי פריגת", "15", "Y123", "Y124 Y126", "exact", "", "Prigat juices")
it("מים מינרליים קטן / גדול", "15 / 24", "Y122", "Y128 Y135", "exact", "", "Mineral water")
it("סאן פלגרינו גדול", "", "Y129", "Y121 Y134", "exact", "", "San Pellegrino")
it("סודה יפנית / סודה פרייה", "15", en="Sodas")
it("באבל תה פסיפלורה / דובדבן / צ'אי", "26 / 26 / 29", en="Bubble tea")
it("תה ושתייה חמה", "11–28", en="Tea and coffee")

json.dump(S, open("menu.json", "w"), ensure_ascii=False, indent=1)
L = {"exact": "✓ exact", "close": "≈ close", "none": "— none"}
n = [i for s in S for i in s["items"]]
c = {k: sum(1 for i in n if i["match"] == k) for k in L}
md = ["# Yoko Ono menu (current), matched to the photos", "",
      "- **Source:** `MENU_FINAL_HEBSP.pdf` (2026-10-19). The data lives in `build_menu.py`; run it to regenerate `menu.json` and this file.",
      "- **Photo codes:** Google Drive codes, fetched with `python3 knowledge/tools/drive_get.py OUT Y049`.",
      "- **Hero:** the photo to use first. **Other photos:** more angles of the same dish.",
      "- **Matching:** checked by eye on 2026-11-12, not by file name.",
      f"- **Totals:** {len(n)} menu lines. {c['exact']} exact, {c['close']} close, {c['none']} without a photo.",
      "- **Not on the menu:** desserts, cocktails and alcohol. The user will send those menus later.",
      "- **Photographed in 2024 but no longer on the menu:** pad kapao, tonkatsu, bœuf caramélisé, darne saumon, poisson du jour, yakitori saumon, curry poulet, curry and tofu noodles. Don't use these.",
      "- **The menu's own look:** \"סטריט סושי בר\" (Street Sushi Bar), white and orange-red with line illustrations.",
      "- **Kosher:** זהבנון stands in for shrimp, surimi for crab; cream and cheese are vegan.", ""]
for s in S:
    md += [f"## {s['section']} ({s['en']})"] + ([f"{s['note']}.", ""] if s["note"] else [""])
    md += ["| Dish | ₪ | Hero | Match | Other photos | Note |", "|---|---|---|---|---|---|"]
    for i in s["items"]:
        md.append(f"| {i['he']} | {i['price']} | {i['hero'] or '—'} | {L[i['match']]} | {', '.join(i['alts']) or ''} | {i['note']} |")
    md.append("")
open("MENU.md", "w").write("\n".join(md))
print(len(n), c)
