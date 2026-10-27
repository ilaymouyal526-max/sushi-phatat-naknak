// All poster text in one place: French (the restaurant's original rules), English and Hebrew.
// Any element with data-t="path.to.text" gets that text; Hebrew paths are set right-to-left.
window.COPY = {
  new: { fr: "Nouveau", en: "New", he: "חדש" },
  kicker: { fr: "Le grand jeu", en: "The grand game", he: "המשחק הגדול" },
  title: { fr: "Lancez les dés", en: "Roll the dice", he: "הטילו את הקוביות" },
  tagline: {
    fr: "Faites un double… et votre addition fond de moitié, ou disparaît.",
    en: "Roll a double… and your bill gets cut in half, or vanishes.",
    he: "הטילו דאבל… והחשבון יורד בחצי, או נעלם לגמרי.",
  },
  half: {
    label: { fr: "Double 1 · 2 · 3", he: "דאבל 1 · 2 · 3" },
    big: "−50%",
    fr: "sur toute l'addition de votre table",
    en: "off your table's entire bill",
    he: "הנחה על כל החשבון של השולחן",
  },
  free: {
    label: { fr: "Double 4 · 5 · 6", he: "דאבל 4 · 5 · 6" },
    ribbon: { fr: "Jackpot !", en: "Jackpot!", he: "ג'קפוט!" },
    big: "100%",
    word: { fr: "Offert", en: "On the house", he: "עלינו" },
    fr: "La totalité de votre repas est offerte",
    en: "Your entire meal is on the house",
    he: "כל הארוחה שלכם על חשבון הבית",
  },
  rulesTitle: { fr: "Règles du jeu", en: "Rules of the game", he: "חוקי המשחק" },
  rules: [
    {
      fr: { t: "Le moment de vérité", d: "Le jeu se déroule exclusivement <b>à la fin de votre repas</b>, au moment du règlement de l'addition." },
      en: { t: "The moment of truth", d: "Only <b>at the end of your meal</b>, when settling the bill." },
      he: { t: "רגע האמת", d: "המשחק מתקיים <b>אך ורק בסוף הארוחה</b>, בזמן תשלום החשבון." },
    },
    {
      fr: { t: "Un seul joueur", d: "Une seule personne lance les dés <b>pour toute la table</b>." },
      en: { t: "A single player", d: "One person rolls the dice <b>for the whole table</b>." },
      he: { t: "שחקן אחד", d: "רק אדם אחד מטיל את הקוביות <b>עבור כל השולחן</b>." },
    },
    {
      fr: { t: "Une chance unique", d: "Le lanceur désigné n'a droit qu'à <b>un seul et unique essai</b>." },
      en: { t: "One single chance", d: "The designated roller gets <b>only one attempt</b>." },
      he: { t: "הזדמנות אחת", d: "למטיל שנבחר יש <b>ניסיון אחד ויחיד</b> בלבד." },
    },
    {
      fr: { t: "Le lancer parfait", d: "Pour être validé, les deux dés doivent <b>rebondir sur la paroi d'en face</b>." },
      en: { t: "The perfect roll", d: "To count, both dice must <b>bounce off the opposite wall</b>." },
      he: { t: "ההטלה המושלמת", d: "כדי שההטלה תיחשב, שתי הקוביות חייבות <b>לפגוע בקיר שממול ולקפוץ ממנו</b>." },
    },
  ],
  wall: { fr: "Paroi d'en face", en: "Opposite wall", he: "הקיר שממול" },
  notes: [
    {
      fr: { t: "Le service", d: "Seul le pourboire n'est pas inclus dans l'offre : il reste dû à votre serveur, pour saluer son travail et son accueil." },
      en: { t: "Service", d: "Only the tip is not included: it remains due to your waiter." },
      he: { t: "השירות", d: "רק הטיפ אינו כלול בהטבה, והוא נשאר לצוות המלצרים כהוקרה על השירות." },
    },
    {
      fr: { t: "Souriez, vous êtes filmés !", d: "En cas de gain, le gagnant autorise l'équipe Yoko Ono à filmer ce moment de joie et à partager la vidéo sur ses réseaux sociaux, sans restriction." },
      en: { t: "Smile, you're on camera!", d: "Winners authorize the Yoko Ono team to film the moment and share it on social media, without restriction." },
      he: { t: "חייכו, אתם מצולמים!", d: "במקרה של זכייה, הזוכים מאשרים לצוות יוקו אונו לצלם את הרגע ולשתף את הסרטון ברשתות החברתיות, ללא הגבלה." },
    },
  ],
};

window.fillCopy = function (root = document) {
  for (const node of root.querySelectorAll("[data-t]")) {
    const path = node.dataset.t;
    const value = path.split(".").reduce((o, k) => o?.[k], window.COPY);
    if (value == null) throw new Error("Missing copy: " + path);
    node.innerHTML = value;
    if (/(^|\.)he(\.|$)/.test(path)) { node.dir = "rtl"; node.lang = "he"; }
  }
};
