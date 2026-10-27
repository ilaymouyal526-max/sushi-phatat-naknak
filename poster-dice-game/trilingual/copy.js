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
    fr: "Félicitations ! Vous bénéficiez immédiatement de <b>50% de remise</b> sur l'ensemble de l'addition de votre table.",
    en: "Congratulations! You immediately get a <b>50% discount</b> on your table's entire bill.",
    he: "מזל טוב! אתם מקבלים מיד <b>50% הנחה</b> על כל החשבון של השולחן.",
  },
  free: {
    label: { fr: "Double 4 · 5 · 6", he: "דאבל 4 · 5 · 6" },
    ribbon: { fr: "Jackpot !", en: "Jackpot!", he: "ג'קפוט!" },
    big: "100%",
    word: { fr: "Offert", en: "On the house", he: "עלינו" },
    fr: "C'est le jackpot ! <b>La totalité de votre repas vous est offerte</b> par la maison !",
    en: "Jackpot! <b>Your entire meal is offered</b> by the house!",
    he: "ג'קפוט! <b>כל הארוחה שלכם</b> על חשבון הבית!",
  },
  rulesTitle: { fr: "Règles du jeu", en: "Rules of the game", he: "חוקי המשחק" },
  // Rules and notes word for word from the restaurant's rules sheet (French and English), in its order
  rules: [
    {
      fr: { t: "Le moment de vérité", d: "Le grand jeu se déroule exclusivement <b>à la fin de votre repas</b>, au moment du règlement de l'addition." },
      en: { t: "The moment of truth", d: "The grand game takes place exclusively <b>at the end of your meal</b>, when settling the bill." },
      he: { t: "רגע האמת", d: "המשחק הגדול מתקיים <b>אך ורק בסוף הארוחה</b>, בזמן תשלום החשבון." },
    },
    {
      fr: { t: "Une chance unique", d: "Le lanceur désigné n'a droit qu'à <b>un seul et unique essai</b> pour toute la table." },
      en: { t: "A unique chance", d: "The designated roller is entitled to <b>only one single attempt</b> for the entire table." },
      he: { t: "הזדמנות אחת", d: "למטיל שנבחר מגיע <b>ניסיון אחד ויחיד</b> עבור כל השולחן." },
    },
    {
      fr: { t: "Un seul joueur", d: "<b>Une seule personne</b> est autorisée à lancer les dés pour l'ensemble des convives de la table." },
      en: { t: "A single player", d: "<b>Only one person</b> is authorized to roll the dice for all guests at the table." },
      he: { t: "שחקן אחד", d: "<b>רק אדם אחד</b> רשאי להטיל את הקוביות עבור כל הסועדים בשולחן." },
    },
    {
      fr: { t: "Le lancer parfait", d: "Pour que le résultat soit validé, les deux dés doivent <b>obligatoirement rebondir sur la paroi d'en face</b>." },
      en: { t: "The perfect roll", d: "For the result to be validated, both dice must <b>obligatorily bounce off the opposite wall</b>." },
      he: { t: "ההטלה המושלמת", d: "כדי שהתוצאה תיחשב, שתי הקוביות <b>חייבות לפגוע בקיר שממול ולקפוץ ממנו</b>." },
    },
  ],
  wall: { fr: "Paroi d'en face", en: "Opposite wall", he: "הקיר שממול" },
  notes: [
    {
      fr: { t: "Le service", d: "Seul le pourboire (<i>tips</i>) n'est pas inclus dans l'offre et reste dû à votre serveur pour saluer son travail et son accueil." },
      en: { t: "The service", d: "Only the tip (<i>tips</i>) is not included in the offer and remains due to your waiter to greet their work and welcome." },
      he: { t: "השירות", d: "רק הטיפ אינו כלול בהטבה, והוא נשאר לצוות המלצרים כהוקרה על העבודה ועל קבלת הפנים." },
    },
    {
      fr: { t: "Souriez, vous êtes filmés !", d: "En participant et en cas de gain, le gagnant autorise chaleureusement l'équipe de <i>Yoko Ono</i> à filmer ce moment de joie et à partager la vidéo sur nos réseaux sociaux sans restrictions." },
      en: { t: "Smile, you're on camera!", d: "By participating and in case of a win, the winner warmly authorizes the <i>Yoko Ono</i> team to film this joyful moment and share the video on our social networks without restrictions." },
      he: { t: "חייכו, אתם מצולמים!", d: "בהשתתפותכם ובמקרה של זכייה, הזוכים מאשרים בשמחה לצוות יוקו אונו לצלם את רגע השמחה ולשתף את הסרטון ברשתות החברתיות שלנו ללא הגבלה." },
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
