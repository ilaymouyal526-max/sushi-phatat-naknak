"""Builds the shot list for the owner as a PDF (Hebrew, RTL), one thumbnail per shot from the current draft.

Run from commercial/dice-explainer:  python3 tools/shotlist.py renders/draft-v6.mp4
Writes tools/shotlist.html and ../yoko-dice-shotlist.pdf (via tools/shotlist_pdf.js, Playwright + Chromium).
Everything is local and free.
"""
import base64, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIDEO = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "renders/draft-v6.mp4")

# (start, end, grab, part, on-screen text, what happens)
SHOTS = [
    (0.0, 3.1, 1.6, "פתיחה", "בועה: \"אפשר חשבון?\"",
     "הזוג יושב בתא אחרי הארוחה. הבחור מנופף כדי לבקש חשבון, והיא מחייכת אליו. קליפ בסגנון פיקסאר."),
    (3.1, 6.9, 4.6, "פתיחה", "בועה: \"לא, לא, לא… קודם מטילים את הקוביות!\"",
     "ליד הבר עם פס הלד הבחור מושיט כרטיס אשראי. הטבח מנענע אצבע ומצביע על שולחן הקוביות, ושני אנשי הצוות צוחקים לידו."),
    (6.9, 8.1, 7.4, "פתיחה", "\"?!\"",
     "הזוג מסתכל אחד על השנייה בהפתעה משועשעת."),
    (8.1, 9.4, 8.6, "פתיחה", "—",
     "תקריב על הלבד הירוק עם הלוגו. יד אוספת את שתי הקוביות לאגרוף. (הצעה: לעשות את השוט הזה ב-Kling ב-4.75 קרדיטים)"),
    (9.4, 11.9, 10.0, "הוק", "\"הטלה אחת…\" / \"…והחשבון יכול להיעלם\"",
     "יד זורקת, ושתי הקוביות עפות אל המצלמה."),
    (11.9, 15.6, 13.4, "המותג", "\"המשחק הגדול\" / \"הטילו את הקוביות\" / \"חדש\"",
     "הלוגו בזהב והחותמת 運. הקוביות נוחתות מתחת לכותרת."),
    (15.6, 19.4, 17.8, "מתי", "\"האפי האוור\" / \"16:00–18:00\" / \"בואו בין ארבע לשש\"",
     "לוח שעון זהב. מחוג השעות עובר מ-4 ל-6, והשמש שוקעת בחלון."),
    (19.4, 23.1, 20.6, "חוק 1", "\"רגע האמת\" / \"משחקים רק בסוף הארוחה, כשמגיע החשבון\"",
     "יד המלצר מחליקה את תיקיית החשבון עם הקוביות לשולחן."),
    (23.1, 26.9, 24.6, "חוק 2", "\"הזדמנות אחת\" / \"×1\" / \"ניסיון אחד ויחיד לכל השולחן\"",
     "שתי הקוביות מסתובבות מתחת ל-×1."),
    (26.9, 30.6, 29.5, "חוק 3", "\"שחקן אחד\" / \"רק אחד מטיל, בשביל כולם\"",
     "ארבעה חברים מצביעים על הבחור שמחזיק את הקוביות, והמצלמה מתקרבת אליו."),
    (30.6, 34.4, 33.4, "חוק 4", "\"ההטלה המושלמת\" / \"הקיר שממול\" / \"✕ לא נחשב\" / \"מטילים שוב!\"",
     "יד זורקת על שולחן הלבד. קובייה אחת לא מגיעה לקיר, ולכן ההטלה לא נחשבת ומטילים שוב."),
    (34.4, 40.6, 37.5, "חוק 4", "\"ההטלה המושלמת\" / \"שתי הקוביות חייבות לפגוע בקיר\" / ✓",
     "זריקה נוספת: שתי הקוביות פוגעות בקיר וחוזרות, ונוחת סימן ✓ בזהב."),
    (40.6, 45.6, 43.5, "פרס", "\"דאבל 1 · 2 · 3\" / \"−50%*\" / \"על כל החשבון של השולחן\"",
     "הקוביות מתחלפות 1-1, 2-2, 3-3. החשבונית מונחת למטה."),
    (45.6, 50.6, 48.4, "פרס", "\"ג'קפוט!\" / \"דאבל 4 · 5 · 6\" / \"100%*\" / \"כל הארוחה עלינו\"",
     "כרטיס זהב. הקוביות נוחתות על 6-6, ועלי זהב ופריחה עפים."),
    (50.6, 53.1, 52.6, "בלי דאבל", "\"לא יצא דאבל?\" / \"נשארתם עם ארוחה מעולה\"",
     "הקוביות מתגלגלות ונעצרות על 3 ו-5."),
    (53.1, 56.9, 55.6, "השירות", "\"השירות\" / \"הטיפ לא כלול בהטבה\"",
     "מטבע זהב נופל לצלחת הטיפ."),
    (56.9, 61.9, 58.3, "צילום", "\"חייכו, אתם מצולמים!\" / \"רגעי הזכייה עולים לרשתות שלנו\"",
     "בתוך טלפון עם REC הזוג חוגג דאבל 6, עם שני הבזקי מצלמה."),
    (61.9, 68.1, 64.6, "סיום", "\"הטילו את הקוביות\" / \"האפי האוור · 16:00–18:00\" / \"הזמינו שולחן\" / \"אחוזה 124, רעננה\" / התקנון",
     "זריקה אחרונה, והקוביות נוחתות על 6-6 מתחת ללוגו."),
]


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def thumb(t, tmp):
    out = pathlib.Path(tmp) / f"t{t:.2f}.jpg"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(VIDEO), "-frames:v", "1",
                    "-vf", "scale=300:-2", "-q:v", "4", str(out)], check=True)
    return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()


FONT = lambda f: (ROOT / "assets/fonts" / f).as_uri()
CSS = f"""
@font-face {{ font-family: "Frank Ruhl"; font-weight: 300 900; src: url('{FONT("frankruhl-normal-hebrew.woff2")}') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F; }}
@font-face {{ font-family: "Frank Ruhl"; font-weight: 300 900; src: url('{FONT("frankruhl-normal-latin.woff2")}') format('woff2'); }}
@font-face {{ font-family: "Heebo"; font-weight: 100 900; src: url('{FONT("heebo-normal-hebrew.woff2")}') format('woff2'); unicode-range: U+0590-05FF, U+200C-2010, U+FB1D-FB4F; }}
@font-face {{ font-family: "Heebo"; font-weight: 100 900; src: url('{FONT("heebo-normal-latin.woff2")}') format('woff2'); }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #0b0907; color: #f4ecdf; font-family: Heebo, sans-serif; direction: rtl; }}
.page {{ width: 210mm; height: 297mm; padding: 11mm 12mm; page-break-after: always; position: relative; overflow: hidden;
  background: radial-gradient(ellipse 90% 60% at 50% 40%, #24160e 0%, #0b0907 75%); }}
.page::before {{ content: ""; position: absolute; inset: 5mm; border: 1.2px solid #c9a36b; pointer-events: none; }}
.page::after {{ content: ""; position: absolute; inset: 6.4mm; border: .6px solid rgba(201,163,107,.5); pointer-events: none; }}
h1 {{ font-family: "Frank Ruhl", serif; font-weight: 800; font-size: 30pt; text-align: center; margin-top: 40mm; color: #e2c590; }}
.lead {{ text-align: center; font-size: 14pt; margin-top: 8mm; line-height: 1.7; color: #f4ecdf; }}
.how {{ margin: 16mm auto 0; width: 150mm; border: 1px solid #c9a36b; border-radius: 6mm; padding: 7mm 9mm; font-size: 13pt; line-height: 1.8; }}
.how b {{ color: #e2c590; }}
.shot {{ display: flex; gap: 7mm; height: 87mm; padding: 4mm 2mm; border-bottom: 1px solid rgba(201,163,107,.35); }}
.shot:last-child {{ border-bottom: 0; }}
.shot img {{ height: 79mm; width: auto; border-radius: 3mm; border: 1px solid #c9a36b; flex: none; }}
.info {{ flex: 1; display: flex; flex-direction: column; gap: 2.2mm; min-width: 0; }}
.top {{ display: flex; align-items: baseline; gap: 4mm; }}
.n {{ font-family: "Frank Ruhl", serif; font-weight: 800; font-size: 24pt; color: #e2c590; }}
.part {{ font-weight: 700; font-size: 13pt; }}
.time {{ font-size: 11pt; color: #c9a36b; direction: ltr; unicode-bidi: isolate; margin-inline-start: auto; }}
.lbl {{ font-size: 9.5pt; color: #c9a36b; font-weight: 700; margin-top: 1mm; }}
.txt {{ font-size: 11pt; line-height: 1.5; }}
.boxes {{ display: flex; gap: 6mm; margin-top: auto; font-size: 12pt; font-weight: 700; }}
.boxes span::before {{ content: ""; display: inline-block; width: 4.2mm; height: 4.2mm; border: 1.4px solid #e2c590; border-radius: 1mm; margin-inline-end: 1.8mm; vertical-align: -0.6mm; }}
.note {{ border-bottom: 1px dashed rgba(244,236,223,.45); height: 7mm; font-size: 9.5pt; color: #c9a36b; }}
.end h2 {{ font-family: "Frank Ruhl", serif; font-weight: 800; font-size: 24pt; color: #e2c590; margin: 14mm 0 8mm; text-align: center; }}
.end ol {{ width: 165mm; margin: 0 auto; font-size: 13pt; line-height: 1.75; padding-inline-start: 7mm; }}
.end li {{ margin-bottom: 4mm; }}
.end li b {{ color: #e2c590; }}
.foot {{ position: absolute; bottom: 9mm; left: 0; right: 0; text-align: center; font-size: 9pt; color: #c9a36b; }}
"""


def build():
    with tempfile.TemporaryDirectory() as tmp:
        cards = []
        for i, (a, b, g, part, text, what) in enumerate(SHOTS, 1):
            cards.append(f"""<div class="shot"><img src="{thumb(g, tmp)}" alt="">
  <div class="info"><div class="top"><span class="n">{i}</span><span class="part">{part}</span><span class="time">{mmss(a)}–{mmss(b)}</span></div>
  <div class="lbl">מה כתוב על המסך</div><div class="txt">{text}</div>
  <div class="lbl">מה קורה</div><div class="txt">{what}</div>
  <div class="boxes"><span>להשאיר</span><span>להעיף</span><span>לשנות</span></div>
  <div class="note">הערה:</div></div></div>""")
    pages = [cards[k:k + 3] for k in range(0, len(cards), 3)]
    total = len(pages) + 2
    body = [f"""<section class="page"><h1>יוקו אונו · הטילו את הקוביות</h1>
<p class="lead">רשימת השוטים של הסרטון<br>68 שניות · אנכי 9:16 · לרילס, לסטוריז ולמסך במסעדה</p>
<div class="how"><b>איך עוברים על זה:</b> ליד כל שוט מסמנים <b>להשאיר</b>, <b>להעיף</b> או <b>לשנות</b>, וכותבים הערה אם צריך.<br>
יש {len(SHOTS)} שוטים: 4 בפתיחה עם הדמויות, ו-14 כרטיסים שמסבירים את המשחק.<br>
בכל כרטיס מופיע למטה "*בכפוף לתקנון".</div>
<div class="foot">עמוד 1 מתוך {total}</div></section>"""]
    for p, chunk in enumerate(pages, 2):
        body.append(f'<section class="page">{"".join(chunk)}<div class="foot">עמוד {p} מתוך {total}</div></section>')
    body.append(f"""<section class="page end"><h2>מה עוד מחכה להחלטה</h2><ol>
<li><b>היד בפתיחה (שוט 4):</b> לעשות אותה בקליפ Kling כמו הדמויות. העלות 4.75 קרדיטים.</li>
<li><b>היד בכרטיסים (שוטים 5, 8, 11, 12, 18):</b> להשאיר את היד התלת-ממדית, או לוותר עליה כך שהקוביות עפות לבד.</li>
<li><b>חשבון האינסטגרם</b> לכרטיס הסיום.</li>
<li><b>קריינות ומוזיקה:</b> מוסיפים בסוף, לפי הזמנים בתסריט.</li>
<li><b>הסכמה:</b> הטבח ושני אנשי הצוות מופיעים כדמויות בסרטון.</li>
</ol><div class="foot">עמוד {total} מתוך {total}</div></section>""")
    html = f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(body)}</body></html>'
    out = ROOT / "tools/shotlist.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    html = build()
    pdf = ROOT.parent / "yoko-dice-shotlist.pdf"
    subprocess.run(["node", str(ROOT / "tools/shotlist_pdf.js"), str(html), str(pdf)], check=True)
    print("wrote", pdf)
