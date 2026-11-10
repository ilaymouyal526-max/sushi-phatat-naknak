// DiceKit (v6): the film's dice and the thrower's hand, driven from GSAP timelines.
//
// A die is a <div class="die" data-faces="6" data-v="a">. mount() fills it with, for every face it can land on:
//   - the rest image   assets/img/die-<face><v>.png        (1024 px, sharp)
//   - a tumble strip   assets/img/die-strip-<face><v>.webp (24 frames in a 6 x 4 grid: a roll that slows onto that face)
// The element's box is the cube's visible width; the rendered frame around it is FRAME times larger, so the die can
// spin without clipping. build.py bakes every throw frame by frame (position, scale, which strip frame), so the
// timeline only holds tl.set() calls: seeking to any time gives exactly that frame.
(function () {
  const FRAME = 1.842, COLS = 6, ROWS = 4;
  const resolve = (t) => (typeof t === "string" ? document.querySelector(t) : t);
  const EPS = 1e-4; // sets land a hair before their frame, so a seek to exactly n/24 s always sees them

  function mount(targets) {
    for (const t of targets) {
      const el = resolve(t), v = el.dataset.v || "a", faces = (el.dataset.faces || "1").split(",");
      const off = -((FRAME - 1) * 50).toFixed(2), box = `position:absolute;left:${off}%;top:${off}%;width:${FRAME * 100}%;height:${FRAME * 100}%`;
      let s = "";
      faces.forEach((f, i) => {
        s += `<img class="dk-rest" data-f="${f}" src="assets/img/die-${f}${v}.png" alt="" style="${box};opacity:${i === 0 ? 1 : 0}">`;
        s += `<div class="dk-win" data-f="${f}" style="${box};overflow:hidden;opacity:0"><img class="dk-strip" src="assets/img/die-strip-${f}${v}.webp" alt="" style="position:absolute;left:0;top:0;width:${COLS * 100}%;height:${ROWS * 100}%"></div>`;
      });
      el.innerHTML = s;
    }
  }

  // From time t on, show `face` at rest.
  function show(tl, target, face, t) {
    const el = resolve(target);
    tl.set(el.querySelectorAll(".dk-rest"), { opacity: (i, n) => (n.dataset.f == face ? 1 : 0) }, Math.max(0, t - EPS));
    tl.set(el.querySelectorAll(".dk-win"), { opacity: 0 }, Math.max(0, t - EPS));
  }

  // From time t on, show frame k (0-23) of the tumble that lands on `face`.
  function frame(tl, target, face, k, t) {
    const el = resolve(target), at = Math.max(0, t - EPS);
    tl.set(el.querySelectorAll(".dk-rest"), { opacity: 0 }, at);
    tl.set(el.querySelectorAll(".dk-win"), { opacity: (i, n) => (n.dataset.f == face ? 1 : 0) }, at);
    const win = [...el.querySelectorAll(".dk-win")].find((n) => n.dataset.f == face);
    tl.set(win.firstElementChild, { xPercent: -(k % COLS) * (100 / COLS), yPercent: -Math.floor(k / COLS) * (100 / ROWS) }, at);
  }

  // One strip frame per film frame from t0: ks[i] is the strip frame (0-23), or -1 for the rest image.
  function spin(tl, target, t0, face, ks, fps = 24) {
    let last = null;
    ks.forEach((k, i) => { if (k === last) return; last = k; k < 0 ? show(tl, target, face, t0 + i / fps) : frame(tl, target, face, k, t0 + i / fps); });
  }

  // Baked motion: rows[i] holds the values of `keys` at film frame i from t0 (e.g. keys ["x","y","scale","opacity"]).
  function bake(tl, target, t0, keys, rows, fps = 24) {
    const el = resolve(target);
    rows.forEach((r, i) => { const o = {}; keys.forEach((k, j) => (o[k] = r[j])); tl.set(el, o, Math.max(0, t0 + i / fps - EPS)); });
  }

  // Hand poses (open, release, fist, flat): stacked renders from build.py's hand(); show `name` from time t on.
  function pose(tl, target, name, t) {
    for (const img of resolve(target).querySelectorAll("img")) tl.set(img, { opacity: img.dataset.pose === name ? 1 : 0 }, Math.max(0, t - EPS));
  }

  window.DiceKit = { mount, show, frame, spin, bake, pose };
})();
