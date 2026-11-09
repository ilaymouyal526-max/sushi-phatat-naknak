בנה לי את המוצר "Sushi push pop" של יוקו אונו בהיגספילד, בתור תמונת רפרנס של המוצר שאשתמש בה אחר כך בכל הפרסומות. הרקע צריך להתאים לתמונות המנות במסך התצוגה של המסעדה.

## לפני שמתחילים
- תטען את הסקיל sushi-ad-director ותעבוד לפיו. תקרא את CLAUDE.md וכל כלל בו תקף.
- הרפרנסים: 7 התמונות והסרטון שצירפתי. הם מקור האמת לצורה, לפרופורציות ולצבעים.
  - את התמונות תעלה להיגספילד (העלאה בלבד, בלי ליצור כלום).
  - מודל התמונה לא מקבל סרטון. לכן תחלץ מהסרטון מקומית, עם ffmpeg, 3-4 פריימים חדים שמראים את המוצר מכמה זוויות, ותעלה אותם בתור תמונות.
- רפרנס לרקע: את התמונה של הגיוזה מהמסך תצרף לפי מזהה הג'וב `726d4428-bede-48ee-8654-75d0f479fedc` (סוג image_job). היא משמשת לרקע, למשטח ולתאורה בלבד.
- אל תוציא קרדיטים בלי אישור שלי. קודם תראה לי את המחיר (get_cost) ואת הפרומפט המלא, ורק אחרי "כן" ממני תריץ. כל ג'וב צריך אישור נפרד.

## שלב 1: בדיקת המפרט מול התמונות (בלי קרדיטים)
תעבור על כל סעיף ותגיד לי מה תואם ומה לא. אל תתקדם עם סתירה פתוחה. שים לב במיוחד ל:
- **הגובה של מבחנת הסויה:** במפרט היא באותו גובה כמו הגליל. ברנדרים הקודמים בהיגספילד היא קצרה יותר.
- **הפרופורציות של הגליל:** במפרט הגובה הוא בערך פי 3.4 מהרוחב (22 על 6.5 ס"מ). ברנדרים הקודמים הגליל נמוך ורחב יותר.
- **הצבע של המדבקה:** כחול-אפור כהה, או שחור?
- **עיצוב המדבקה:** האם על המוצר האמיתי יש המדבקה העגולה, או מדבקה עוטפת? (בסשן "Sushipush popsticker" עיצבנו מדבקה עוטפת עם SUSHI PUSH POP במברשת.)
- **הבסיס:** איך הבוכנה נראית באמת מלמטה.

מפרט המוצר:
1. **שרוול/גליל ראשי:** גליל קרטון שחור מט, בגובה של בערך 22 ס"מ ובקוטר של בערך 6.5 ס"מ, עם טקסטורת נייר עדינה.
2. **למעלה:** מכסה פלסטיק שקוף שיושב בגובה שפת הגליל. ממנו יוצאת הצידה לשונית שקופה עם טבעת שמחזיקה את המבחנה.
3. **למטה:** בסיס פלסטיק שחור עם בליטה עגולה לצד, שמחזיקה את תחתית המבחנה. בתוך הבסיס יש בוכנה שחורה בצורת משפך, עם עיגול אפור באמצע.
4. **מבחנת סויה:** צינור פלסטיק שקוף-חלבי ודק (בקוטר של בערך 1.2 ס"מ), צמוד לצד הימני של הגליל. יש לו פקקי הברגה שחורים ומחורצים בשני הקצוות. הוא מלא ברוטב סויה כהה בגוון בורדו-חום, עם כיס אוויר קטן למעלה.
5. **מדבקה עגולה בחזית:** הלוגו של יוקו אונו בקו זהב-ברונזה, ומתחתיו "YOKO ONO / ASIAN KITCHEN".
6. **בתחתית החזית:** "Sushi push pop" בהטבעת זהב-נחושת.

## שלב 2: הפקה
- **מודל:** GPT Image 2.5 (`gpt_image_2_5`), יחס 4:5. זה המודל שיצר את תמונות המנות במסך, אז הסגנון יהיה זהה.
- **קודם טיוטות:** איכות low ו-1K, תמונה אחת לכל זווית, 0.25 קרדיט לכל אחת. הטיוטות רק בודקות צורה ופרופורציות מול התמונות.
- **אחרי שאאשר טיוטה:** גרסה סופית באיכות high ו-2K, 2.75 קרדיט לכל אחת, שוב עם אישור.
- **רפרנסים לכל ג'וב:** רפרנס 1 הוא הגיוזה (רקע בלבד). רפרנסים 2 ואילך הם התמונות של המוצר.
- **לוגו וטקסט:** את המוצר מייצרים עם מדבקה ריקה ובלי טקסט. את הלוגו האמיתי ואת "Sushi push pop" מלבישים אחר כך מקומית, בלי קרדיטים:
  - **מקור הלוגו:** `shared/logo-source.png` או `shared/logo-path.js` בענף `ccr-501b2ecd-itqixr`.
  - **מקור הכיתוב "Sushi push pop":** חיתוך מהתמונה האמיתית הכי חדה.
  - **התאמה לגליל:** עיוות גלילי לפי הקוטר, והצללה לפי הבהירות של המדבקה הריקה בתמונה (multiply), כדי שהאור יתאים.
  - **מסכה מרוככת,** בלי טשטוש של הרקע.
  - **שורת המשווק הקטנה בעברית:** משמיטים.
- **זווית (ג):** זו הזווית המסוכנת, כי AI ממציא מנגנונים. תריץ אותה רק אם יש תמונה אמיתית של התחתית. אם אין, תציע לי במקום זה לנקות מקומית את התמונה האמיתית.

### בלוק המוצר (זהה בכל הזוויות)
```
References 2 and up are photos of the real product and are the authority for its shape, proportions, materials and colors; match them exactly.
PRODUCT: a matte black paperboard tube standing upright, its height about 3.4 times its width, fine paper texture. On top, a clear plastic lid sitting flush with the tube rim; a small clear tab sticks out from the lid to the right and ends in a ring that grips the top cap of a slim soy-sauce vial. At the bottom, a black plastic base cap with a round lobe on the right that cradles the bottom cap of the vial. The vial is a slim frosted-clear plastic tube about one fifth of the tube's width, running along the right side for the full height of the tube, with black ribbed screw caps on both ends, filled with dark burgundy-brown soy sauce with a small air gap at the top. On the front, a round label in deep slate blue with a thin gold rim, completely blank inside. The lower front of the tube is plain matte black. No text, no letters, no logo anywhere on the product.
```

### בלוק הרקע (בסגנון מסך התצוגה)
```
Reference 1 is for the surface, background and lighting only; do not include any food or dish from it.
SET: the product stands on a polished black marble slab with thin, elegant gold veins. Completely black room, pitch-black background, nothing else in frame. A single soft warm overhead spotlight from above and slightly in front pools light on the product and the marble, with rich falloff into darkness. A thin warm rim light outlines the black tube so it separates clearly from the black background. Real soft contact shadow and a faint reflection on the polished marble. Luxurious, moody, Michelin-style product photography, photorealistic, true-to-life materials.
```

### הזוויות (בלוק המוצר + בלוק הרקע + השורה של הזווית)
- **(א) הירו חזיתי:**
  ```
  CAMERA: straight-on at label height, narrow 29-degree field of view, the blank round label square to camera, the vial fully visible on the right. Product centered with empty dark space above and below it, about 15% of the frame each.
  ```
- **(ב) 3/4 מלמעלה:**
  ```
  CAMERA: three-quarter view from the front-left, about 35 degrees above, so the clear flush lid, the tab ring and the top cap of the vial are clearly visible; the label turns slightly away but stays visible. Product centered with empty dark space around it.
  ```
- **(ג) מבט על הבוכנה:**
  ```
  CAMERA: low angle looking into the underside of the base: the tube tipped onto its side on the marble with the base facing camera, showing the black funnel-shaped plunger with a grey circle in its center inside the base cap and the round lobe holding the vial's bottom cap. Match the real underside photo exactly.
  ```

## שלב 3: אחרי שאאשר את התמונות
- **הוספה ל-Elements בהיגספילד:** תמונה (א) עם הלוגו המולבש בתור `@pushpop`. בנוסף, קלוז-אפ שטוח של המדבקה בתור `@label`.
- **הצעה לסרטון קצר (רק הצעה, בלי להריץ):**
  - טיוטה ב-480p.
  - תמונה (א) בתור הפריים הראשון.
  - תנועת מצלמה: אורביט איטי או פוש-אין, ושמשהו זז כבר מהפריים הראשון (למשל עשן קל או ניצוץ אור שעובר על הזהב). בלי שוטים סטטיים.
  - מחיר ואישור לפני כל ריצה.

## סטטוס
תשמור את הסטטוס בקובץ `push-pop/STATUS.md` בריפו: מה הועלה, מזהי המדיה והג'ובים, מה אושר, כמה קרדיטים יצאו ומה הצעד הבא. תעשה commit ו-push.
