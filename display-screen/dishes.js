// Dishes shown on the in-store screen. Replace this sample list with the real menu:
//   photo: path to the dish photo (e.g. "photos/red-dragon-tataki.jpg"); null shows the placeholder illustration
//   art:   which placeholder illustration to use while there is no photo
//   price: optional, shown as written (e.g. "18 €"); null hides it
window.DISHES = [
  {
    name: "Red Dragon Tataki", he: "רד דרגון טאטאקי",
    fr: "Uramaki au thon snacké, sauce, sésame et ciboule",
    en: "Uramaki with torch-seared tuna, sauce, sesame and scallion",
    heDesc: "אוראמאקי עם טונה צרובה, רוטב, שומשום ובצל ירוק",
    photo: null, art: "tataki", price: null,
  },
  {
    name: "Sushi Push Pop", he: "סושי פוש פופ",
    fr: "Le sushi qui se pousse et se croque",
    en: "Push it up, pop it, bite it",
    heDesc: "סושי בשפופרת: דוחפים, נוגסים, נהנים",
    photo: null, art: "pushpop", price: null,
  },
  {
    name: "Nigiri Saumon", he: "ניגירי סלמון",
    fr: "Saumon frais sur riz vinaigré",
    en: "Fresh salmon on seasoned rice",
    heDesc: "סלמון טרי על אורז מתובל",
    photo: null, art: "nigiri", price: null,
  },
  {
    name: "California Maki", he: "קליפורניה מאקי",
    fr: "Avocat, surimi, concombre et sésame",
    en: "Avocado, crab stick, cucumber and sesame",
    heDesc: "אבוקדו, סורימי, מלפפון ושומשום",
    photo: null, art: "maki", price: null,
  },
  {
    name: "Poke Bowl", he: "פוקה בול",
    fr: "Riz, saumon, avocat, edamame et mangue",
    en: "Rice, salmon, avocado, edamame and mango",
    heDesc: "אורז, סלמון, אבוקדו, אדממה ומנגו",
    photo: null, art: "poke", price: null,
  },
  {
    name: "Gyoza", he: "גיוזה",
    fr: "Raviolis japonais grillés, sauce ponzu",
    en: "Pan-fried Japanese dumplings with ponzu",
    heDesc: "כיסוני גיוזה צרובים ברוטב פונזו",
    photo: null, art: "gyoza", price: null,
  },
];

// Reads ?layout=hero&dish=0 or ?layout=grid&dishes=0,1,2,3 and returns what to draw.
window.slideFromUrl = function () {
  const q = new URLSearchParams(location.search);
  const layout = q.get("layout") || "hero";
  const ids = (q.get("dishes") || q.get("dish") || "0").split(",").map(Number);
  return { layout, dishes: ids.map(i => ({ ...window.DISHES[i], index: i + 1 })) };
};

// The dish photo, or its placeholder illustration
window.dishVisual = function (dish) {
  return dish.photo
    ? `<img src="${dish.photo}" alt="${dish.name}">`
    : `<div class="art">${window.Plates.svg(dish.art)}</div>`;
};
