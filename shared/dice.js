// SVG dice for the Yoko Ono designs: isometric 3D dice and flat dice.
// Asian dice have a red one and a red four, so those pips use `red`.
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const lo = 25, c = 50, hi = 75;
  const PIPS = {
    1: [[c, c]],
    2: [[lo, lo], [hi, hi]],
    3: [[lo, lo], [c, c], [hi, hi]],
    4: [[lo, lo], [hi, lo], [lo, hi], [hi, hi]],
    5: [[lo, lo], [hi, lo], [c, c], [lo, hi], [hi, hi]],
    6: [[lo, lo], [lo, c], [lo, hi], [hi, lo], [hi, c], [hi, hi]],
  };

  const IVORY = {
    top: "#fbf6ec", left: "#e8ddc8", right: "#d3c4a8", edge: "#c2b190",
    pip: "#1b1714", red: "#c0352b", stroke: null, strokeWidth: 0,
  };

  function el(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  }

  const pipFill = (n, t) => (n === 1 || n === 4) ? t.red : t.pip;

  function face(parent, n, matrix, fill, t) {
    const g = el("g", { transform: `matrix(${matrix.join(" ")})` }, parent);
    el("rect", { x: 2.5, y: 2.5, width: 95, height: 95, rx: 17, fill }, g);
    for (const [x, y] of PIPS[n])
      el("circle", { cx: x, cy: y, r: n === 1 ? 15 : 9.5, fill: pipFill(n, t) }, g);
  }

  // (cx, cy) is the centre of the hexagonal silhouette, s the edge length.
  function isoDie(parent, { cx, cy, s, rot = 0, top, left, right, theme = {}, filter }) {
    const t = { ...IVORY, ...theme };
    const g = el("g", { transform: `rotate(${rot} ${cx} ${cy})`, filter }, parent);
    const k = 0.866 * s, h = 0.5 * s, u = 1 / 100;
    const pts = [[cx, cy - s], [cx + k, cy - h], [cx + k, cy + h], [cx, cy + s], [cx - k, cy + h], [cx - k, cy - h]];
    const outline = pts.map(p => p.join(",")).join(" ");
    if (t.stroke) el("polygon", { points: outline, fill: t.stroke, stroke: t.stroke, "stroke-width": s * 0.1 + t.strokeWidth * 2, "stroke-linejoin": "round" }, g);
    el("polygon", { points: outline, fill: t.edge, stroke: t.edge, "stroke-width": s * 0.1, "stroke-linejoin": "round" }, g);
    face(g, top, [k * u, h * u, -k * u, h * u, cx, cy - s], t.top, t);
    face(g, left, [k * u, h * u, 0, s * u, cx - k, cy - h], t.left, t);
    face(g, right, [k * u, -h * u, 0, s * u, cx, cy], t.right, t);
    return g;
  }

  // A flat die face as its own <svg>, for icons and inline rows.
  function flatDie(n, { body = "#f4ecdf", pip = "#1b1714", red = "#c0352b", stroke = null, strokeWidth = 6 } = {}) {
    const svg = el("svg", { viewBox: "0 0 100 100" });
    const inset = stroke ? strokeWidth / 2 + 2 : 3;
    el("rect", { x: inset, y: inset, width: 100 - 2 * inset, height: 100 - 2 * inset, rx: 18, fill: body, stroke, "stroke-width": stroke ? strokeWidth : null }, svg);
    for (const [x, y] of PIPS[n])
      el("circle", { cx: x, cy: y, r: n === 1 ? 14 : 10, fill: (n === 1 || n === 4) ? red : pip }, svg);
    return svg;
  }

  // Fills every element with data-dice="1,2,3" with pairs of flat dice.
  function fillDoubles(root, opts) {
    for (const row of root.querySelectorAll("[data-dice]")) {
      for (const n of row.dataset.dice.split(",").map(Number)) {
        const pair = document.createElement("span");
        pair.className = "pair";
        pair.append(flatDie(n, opts), flatDie(n, opts));
        row.appendChild(pair);
      }
    }
  }

  window.Dice = { NS, el, isoDie, flatDie, fillDoubles };
})();
