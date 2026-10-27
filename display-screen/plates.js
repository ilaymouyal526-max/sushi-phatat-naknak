// Flat top-down dish illustrations used as placeholders until the restaurant's real photos arrive.
// Plates.svg(kind) returns an <svg> string on a transparent 600x600 canvas.
(function () {
  const rnd = (seed => () => (seed = (seed * 16807) % 2147483647) / 2147483647)(42);
  const shadow = (cx, cy, rx, ry) => `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#000" opacity=".28" filter="url(#soft)"/>`;
  const sesame = (n, x0, y0, w, h, fill = "#f5ead2") => Array.from({ length: n }, () =>
    `<ellipse cx="${(x0 + rnd() * w).toFixed(1)}" cy="${(y0 + rnd() * h).toFixed(1)}" rx="3.2" ry="1.8" fill="${fill}" transform="rotate(${(rnd() * 180).toFixed(0)} ${(x0 + w / 2).toFixed(0)} ${(y0 + h / 2).toFixed(0)})"/>`).join("");
  const scallion = (x, y, r = 7) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#5fae3e"/><circle cx="${x}" cy="${y}" r="${r * .55}" fill="#c9e8a6"/>`;

  const ART = {
    tataki() {
      let s = shadow(300, 330, 270, 105) + `<g transform="rotate(-8 300 300)"><rect x="40" y="205" width="520" height="190" rx="18" fill="#2b2a2c"/><rect x="40" y="205" width="520" height="190" rx="18" fill="none" stroke="#3d3b3e" stroke-width="3"/>`;
      for (let i = 0; i < 8; i++) {
        const x = 62 + i * 60;
        s += `<rect x="${x}" y="232" width="56" height="136" rx="16" fill="#f4efe4"/>${sesame(6, x + 4, 236, 48, 128, "#2b2a2c")}
          <rect x="${x - 2}" y="246" width="60" height="98" rx="14" fill="#b9283a"/>
          <rect x="${x + 6}" y="256" width="44" height="78" rx="10" fill="#d8455a"/>
          <path d="M${x + 2} 262l52 18M${x + 2} 290l52 18M${x + 2} 318l52 18" stroke="#5b1a1c" stroke-width="5" opacity=".55"/>`;
      }
      s += `<path d="M58 300 ${Array.from({ length: 16 }, (_, i) => `L${80 + i * 30} ${i % 2 ? 270 : 330}`).join(" ")}" fill="none" stroke="#3a160d" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>`;
      for (let i = 0; i < 9; i++) s += scallion(70 + i * 55 + rnd() * 20, 250 + rnd() * 100, 6);
      return s + sesame(30, 60, 240, 480, 120) + `</g>`;
    },
    pushpop() {
      let s = shadow(310, 470, 210, 46);
      s += `<g transform="rotate(-24 300 300)">
        <rect x="236" y="70" width="128" height="430" rx="22" fill="#e9eef0" opacity=".35"/>
        <rect x="244" y="440" width="112" height="60" rx="8" fill="#9aa3a8"/><rect x="284" y="500" width="32" height="54" rx="6" fill="#9aa3a8"/><rect x="262" y="548" width="76" height="20" rx="10" fill="#7d878c"/>
        <rect x="244" y="360" width="112" height="80" fill="#f4efe4"/>${sesame(10, 248, 364, 104, 72, "#d8cfbd")}
        <rect x="244" y="300" width="112" height="60" fill="#f08a5d"/><path d="M244 312l112 18M244 334l112 18" stroke="#fde3d3" stroke-width="7"/>
        <rect x="244" y="250" width="112" height="50" fill="#7fb54a"/><rect x="244" y="262" width="112" height="10" fill="#a8d06f"/>
        <rect x="244" y="236" width="112" height="14" fill="#1c2420"/>
        <rect x="244" y="150" width="112" height="86" fill="#f4efe4"/>${sesame(10, 248, 154, 104, 78, "#d8cfbd")}
        <rect x="244" y="96" width="112" height="54" rx="4" fill="#f26a2e"/>${Array.from({ length: 30 }, () => `<circle cx="${(250 + rnd() * 100).toFixed(1)}" cy="${(100 + rnd() * 46).toFixed(1)}" r="4" fill="#ff8f4a"/>`).join("")}
        <rect x="236" y="70" width="128" height="430" rx="22" fill="none" stroke="#dfe7ea" stroke-width="6" opacity=".9"/>
        <rect x="252" y="90" width="10" height="390" rx="5" fill="#fff" opacity=".45"/>
      </g>`;
      return s + `<circle cx="130" cy="470" r="62" fill="#2b2a2c"/><circle cx="130" cy="470" r="48" fill="#3a160d"/><circle cx="116" cy="458" r="10" fill="#6a3a24" opacity=".7"/>`;
    },
    nigiri() {
      let s = shadow(300, 340, 270, 120) + `<g transform="rotate(-6 300 300)"><rect x="40" y="170" width="520" height="270" rx="20" fill="#d6ad78"/>
        ${Array.from({ length: 7 }, (_, i) => `<path d="M50 ${195 + i * 36} C 200 ${185 + i * 36}, 380 ${205 + i * 36}, 550 ${192 + i * 36}" stroke="#bf925b" stroke-width="3" fill="none" opacity=".7"/>`).join("")}`;
      for (let i = 0; i < 4; i++) {
        const x = 70 + i * 104;
        s += `<rect x="${x + 6}" y="216" width="84" height="176" rx="38" fill="#f4efe4"/>
          <rect x="${x}" y="206" width="96" height="180" rx="40" fill="#f2884f"/>
          <path d="M${x + 4} 236l88 26M${x + 2} 276l92 28M${x + 2} 318l92 28M${x + 6} 356l80 24" stroke="#fde1cf" stroke-width="9" stroke-linecap="round"/>`;
      }
      s += `<path d="M498 230c30-8 48 22 30 44-16 20-46 6-44-16 1-14 4-24 14-28Z" fill="#8cc152"/>`;
      for (let i = 0; i < 4; i++) s += `<ellipse cx="${506 + i * 6}" cy="${330 + i * 14}" rx="34" ry="14" fill="#f6b8b0" stroke="#e9988f" stroke-width="2" transform="rotate(${-20 + i * 12} 515 345)"/>`;
      return s + `</g>`;
    },
    maki() {
      let s = shadow(300, 320, 250, 250) + `<circle cx="300" cy="300" r="255" fill="#232224"/><circle cx="300" cy="300" r="238" fill="none" stroke="#38363a" stroke-width="4"/>`;
      const fills = [["#f2884f", "#7fb54a"], ["#d8455a", "#a8d06f"], ["#f2884f", "#e9e1c9"]];
      const spots = [[300, 300], ...Array.from({ length: 6 }, (_, i) => [300 + 128 * Math.cos(i * Math.PI / 3), 300 + 128 * Math.sin(i * Math.PI / 3)])];
      spots.forEach(([x, y], i) => {
        const [a, b] = fills[i % 3];
        s += `<circle cx="${x}" cy="${y}" r="60" fill="#14181a"/><circle cx="${x}" cy="${y}" r="52" fill="#f4efe4"/>${sesame(6, x - 40, y - 40, 80, 80, "#d8cfbd")}
          <circle cx="${x}" cy="${y}" r="22" fill="${a}"/><path d="M${x - 8} ${y + 4}a14 14 0 0 0 26 -6" fill="${b}"/>`;
      });
      return s;
    },
    poke() {
      let s = shadow(300, 320, 255, 255) + `<circle cx="300" cy="300" r="258" fill="#22334f"/><circle cx="300" cy="300" r="236" fill="#2f4a70"/><circle cx="300" cy="300" r="222" fill="#f4efe4"/>${sesame(30, 120, 120, 360, 360, "#d8cfbd")}`;
      for (let i = 0; i < 9; i++) {
        const x = 200 + (i % 3) * 46 + rnd() * 10, y = 170 + Math.floor(i / 3) * 46 + rnd() * 10;
        s += `<rect x="${x}" y="${y}" width="42" height="42" rx="7" fill="#f2884f" transform="rotate(${(rnd() * 30 - 15).toFixed(0)} ${x + 21} ${y + 21})"/><path d="M${x + 6} ${y + 12}l30 8M${x + 6} ${y + 28}l30 8" stroke="#fde1cf" stroke-width="5"/>`;
      }
      for (let i = 0; i < 6; i++) s += `<ellipse cx="380" cy="300" rx="80" ry="22" fill="${i % 2 ? "#a8d06f" : "#7fb54a"}" transform="rotate(${-30 + i * 14} 300 300) translate(0 ${i * 4})"/>`;
      for (let i = 0; i < 8; i++) s += `<rect x="${170 + (i % 4) * 34}" y="${330 + Math.floor(i / 4) * 34}" width="30" height="30" rx="5" fill="#f7c33f"/>`;
      for (let i = 0; i < 10; i++) s += `<ellipse cx="${300 + rnd() * 90}" cy="${380 + rnd() * 70}" rx="13" ry="9" fill="#9bc96b" stroke="#6f9e45" stroke-width="2"/>`;
      for (let i = 0; i < 7; i++) s += `<path d="M${330 + i * 9} 160q30 20 60 6" stroke="#7b3f8c" stroke-width="5" fill="none" stroke-linecap="round"/>`;
      return s;
    },
    gyoza() {
      let s = shadow(300, 330, 270, 200) + `<ellipse cx="300" cy="300" rx="275" ry="210" fill="#f6f2ea"/><ellipse cx="300" cy="300" rx="250" ry="188" fill="none" stroke="#e3dccf" stroke-width="4"/>`;
      for (let i = 0; i < 5; i++) {
        const a = -40 + i * 20;
        s += `<g transform="rotate(${a} 300 520)"><path d="M300 150c62 0 92 46 92 100H208c0-54 30-100 92-100Z" fill="#efcf95"/><path d="M208 250h184c0 14-6 24-14 24H222c-8 0-14-10-14-24Z" fill="#b8762f"/>
          ${[230, 255, 280, 305, 330, 355].map(x => `<path d="M${x + 10} 160q-6 30 2 60" stroke="#d8b06b" stroke-width="4" fill="none"/>`).join("")}</g>`;
      }
      s += `<circle cx="470" cy="420" r="58" fill="#232224"/><circle cx="470" cy="420" r="44" fill="#4a2414"/>${Array.from({ length: 8 }, () => `<circle cx="${(450 + rnd() * 40).toFixed(1)}" cy="${(400 + rnd() * 40).toFixed(1)}" r="3" fill="#d23c1f"/>`).join("")}`;
      for (let i = 0; i < 5; i++) s += scallion(160 + i * 26, 420 + rnd() * 20, 7);
      return s;
    },
  };

  window.Plates = {
    svg(kind) {
      return `<svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg"><defs><filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter></defs>${ART[kind]()}</svg>`;
    },
  };
})();
