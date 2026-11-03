// The restaurant's real dice: translucent red casino dice with white pips (see ../reference/dice_on_table.jpg).
// DiceKit.mount() draws all six faces into each .die element; tumble() schedules face swaps on a GSAP timeline.
(function () {
  const PIPS = {
    1: [[50, 50]],
    2: [[27, 27], [73, 73]],
    3: [[27, 27], [50, 50], [73, 73]],
    4: [[27, 27], [73, 27], [27, 73], [73, 73]],
    5: [[27, 27], [73, 27], [50, 50], [27, 73], [73, 73]],
    6: [[27, 25], [27, 50], [27, 75], [73, 25], [73, 50], [73, 75]],
  };
  const ORDER = [1, 5, 3, 6, 2, 4];

  // Vegas casino dice: sharp corners, translucent red acrylic, flush white pips, a tiny gold serial on the one face.
  function svg() {
    let s = '<svg viewBox="-8 -8 136 146" width="100%" height="100%" style="display:block;overflow:visible">' +
      '<defs><radialGradient id="vd-body" cx=".42" cy=".38" r=".75"><stop offset="0" stop-color="#ff3b52"/><stop offset=".55" stop-color="#d0122c"/><stop offset="1" stop-color="#7d0716"/></radialGradient>' +
      '<linearGradient id="vd-side" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8e0a1b"/><stop offset="1" stop-color="#3f030b"/></linearGradient></defs>' +
      '<rect x="1" y="13" width="120" height="120" rx="5" fill="url(#vd-side)"/>' +
      '<rect x="0" y="0" width="120" height="120" rx="5" fill="url(#vd-body)" fill-opacity=".95"/>' +
      '<rect x="3" y="3" width="114" height="114" rx="3" fill="none" stroke="#ff9aa4" stroke-opacity=".55" stroke-width="2"/>' +
      '<path d="M5 3 L115 3" stroke="#ffffff" stroke-opacity=".7" stroke-width="2.5" stroke-linecap="round"/>' +
      '<path d="M3 6 L3 112" stroke="#ffffff" stroke-opacity=".4" stroke-width="2" stroke-linecap="round"/>' +
      '<polygon points="0,0 46,0 0,46" fill="#ffffff" fill-opacity=".12"/>' +
      '<polygon points="70,0 92,0 0,92 0,70" fill="#ffffff" fill-opacity=".07"/>';
    for (let n = 1; n <= 6; n++) {
      s += `<g class="face f${n}" opacity="0">`;
      // the opposite face shows faintly through the translucent acrylic
      for (const [x, y] of PIPS[7 - n]) s += `<circle cx="${x * 1.2 + 7}" cy="${y * 1.2 + 11}" r="8" fill="#ffffff" fill-opacity=".14"/>`;
      for (const [x, y] of PIPS[n]) {
        const r = n === 1 ? 14 : 10.5;
        s += `<circle cx="${x * 1.2}" cy="${y * 1.2}" r="${r}" fill="#c9c2bd"/><circle cx="${x * 1.2 - 0.8}" cy="${y * 1.2 - 0.8}" r="${r - 1.4}" fill="#ffffff"/>`;
      }
      if (n === 1) s += '<text x="60" y="108" text-anchor="middle" font-family="Heebo, sans-serif" font-weight="700" font-size="8" letter-spacing="1" fill="#e2c590" fill-opacity=".85">YO-24</text>';
      s += "</g>";
    }
    return s + "</svg>";
  }

  const resolve = (t) => (typeof t === "string" ? document.querySelector(t) : t);

  function mount(targets) {
    for (const t of targets) {
      const el = resolve(t);
      el.innerHTML = svg();
      el.querySelector(".f" + (el.dataset.face || 1)).setAttribute("opacity", "1");
    }
  }

  // Show `face` from time t on.
  function setFace(tl, target, face, t) {
    const faces = resolve(target).querySelectorAll(".face");
    tl.set(faces, { opacity: (i) => (i === face - 1 ? 1 : 0) }, t);
  }

  // Swap faces every `step` seconds between t0 and t1, landing on `final` at t1.
  function tumble(tl, target, t0, t1, final, step = 1 / 12, seed = 0) {
    let k = seed;
    for (let t = t0; t < t1 - 1e-6; t += step) setFace(tl, target, ORDER[k++ % 6], t);
    setFace(tl, target, final, t1);
  }

  window.DiceKit = { mount, setFace, tumble };
})();

// Hand poses (fist, release, open) drawn by build.py's hand_svg(); show `name` from time t on.
(function () {
  const NAMES = ["fist", "release", "open"];
  window.DiceKit.pose = function (tl, target, name, t) {
    const el = document.querySelector(target);
    for (const n of NAMES) tl.set(el.querySelector(".pose-" + n), { opacity: n === name ? 1 : 0 }, t);
  };
})();
