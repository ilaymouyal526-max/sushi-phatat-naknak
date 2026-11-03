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

  function svg() {
    let s = '<svg viewBox="-8 -8 136 146" width="100%" height="100%" style="display:block;overflow:visible">' +
      '<rect x="0" y="12" width="120" height="120" rx="24" fill="#6d0716"/>' +
      '<rect x="0" y="0" width="120" height="120" rx="24" fill="#c8102e" fill-opacity=".93"/>' +
      '<rect x="4" y="4" width="112" height="112" rx="21" fill="none" stroke="#ff8f95" stroke-opacity=".45" stroke-width="3"/>' +
      '<path d="M14 44 Q14 14 44 14 L74 14" stroke="#ffffff" stroke-opacity=".38" stroke-width="5" fill="none" stroke-linecap="round"/>';
    for (let n = 1; n <= 6; n++) {
      s += `<g class="face f${n}" opacity="0">`;
      // the opposite face shows faintly through the translucent body
      for (const [x, y] of PIPS[7 - n]) s += `<circle cx="${x * 1.2 + 7}" cy="${y * 1.2 + 11}" r="8" fill="#ffffff" fill-opacity=".13"/>`;
      for (const [x, y] of PIPS[n]) s += `<circle cx="${x * 1.2}" cy="${y * 1.2}" r="${n === 1 ? 14 : 10.5}" fill="#ffffff"/>`;
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
