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

  // Vegas casino dice, rendered in real 3D by tools/render_props.js: 6 resting faces and 12 tumbling poses.
  function svg() {
    let s = "";
    for (let n = 1; n <= 6; n++) s += `<img class="face f${n}" src="assets/img/die-${n}.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;opacity:0">`;
    for (let k = 0; k < 12; k++) s += `<img class="face roll" src="assets/img/die-roll-${k}.png" alt="" style="position:absolute;inset:0;width:100%;height:100%;opacity:0">`;
    return s;
  }

  const resolve = (t) => (typeof t === "string" ? document.querySelector(t) : t);

  function mount(targets) {
    for (const t of targets) {
      const el = resolve(t);
      el.innerHTML = svg();
      el.querySelector(".f" + (el.dataset.face || 1)).style.opacity = "1";
    }
  }

  // Show `face` from time t on.
  function setFace(tl, target, face, t) {
    const faces = resolve(target).querySelectorAll(".face");
    tl.set(faces, { opacity: (i) => (i === face - 1 ? 1 : 0) }, t);
  }

  // Show tumbling pose k (0-11) from time t on.
  function setRoll(tl, target, k, t) {
    const faces = resolve(target).querySelectorAll(".face");
    tl.set(faces, { opacity: (i) => (i === 6 + (k % 12) ? 1 : 0) }, t);
  }

  // Swap faces every `step` seconds between t0 and t1, landing on `final` at t1.
  function tumble(tl, target, t0, t1, final, step = 1 / 12, seed = 0) {
    let k = seed;
    for (let t = t0; t < t1 - 1e-6; t += step) setRoll(tl, target, (k++ * 5) % 12, t);
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
