// Yoko Ono · Asian Kitchen logo, redrawn as a vector from the logo printed on the dice table.
// Drawn in currentColor, so the colour comes from CSS. Insert with Logo.svg() (inline, so the
// page's Montserrat is used for "ASIAN KITCHEN").
(function () {
  const W = 8; // stroke width of the line art
  const blossom = (x, y, r = 13) => {
    const petals = Array.from({ length: 5 }, (_, i) => {
      const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
      return `<circle cx="${(x + Math.cos(a) * r * 0.62).toFixed(1)}" cy="${(y + Math.sin(a) * r * 0.62).toFixed(1)}" r="${(r * 0.46).toFixed(1)}"/>`;
    }).join("");
    return `<g class="blossom">${petals}<circle cx="${x}" cy="${y}" r="${(r * 0.22).toFixed(1)}" fill="var(--logo-bg, #000)"/></g>`;
  };
  // Frame: straight sides, half-ellipse top and bottom, broken where the name crosses it
  const frame = (cx, half, topY, sideTop, sideBot, botRy, gapTop, gapBot) => {
    const l = cx - half, r = cx + half, topRy = sideTop - topY;
    return `<path d="M${l} ${gapTop} V${sideTop} A${half} ${topRy} 0 0 1 ${r} ${sideTop} V${gapTop}"/>` +
      `<path d="M${l} ${gapBot} V${sideBot} A${half} ${botRy} 0 0 0 ${r} ${sideBot} V${gapBot}"/>`;
  };
  const art = `
    <g fill="none" stroke="currentColor" stroke-width="${W}" stroke-linecap="round" stroke-linejoin="round">
      ${frame(502, 256, 22, 157, 407, 181, 238, 346)}
      ${frame(502, 226, 54, 157, 407, 150, 238, 346)}
      <!-- branches -->
      <path d="M282 142 C330 128 390 120 452 124" stroke-width="5"/>
      <path d="M330 133 C345 140 352 148 356 156" stroke-width="4"/>
      <path d="M722 146 C672 128 612 118 548 122" stroke-width="5"/>
      <path d="M672 133 C655 140 645 150 638 160" stroke-width="4"/>
      <!-- mountains -->
      <path d="M306 234 C360 214 400 196 440 182 C455 190 470 200 486 206 C500 196 515 190 532 186 C580 204 630 218 694 232"/>
      <path d="M440 182 C430 196 418 206 404 214 M440 182 C448 196 452 206 450 218 M532 186 C522 198 512 206 500 212 M532 186 C542 200 552 208 566 214" stroke-width="5"/>
      <!-- YOKO ONO -->
      <path d="M22 262 C40 288 80 296 108 292 C140 288 175 276 198 258 M108 292 V330 H96"/>
      <ellipse cx="222" cy="292" rx="56" ry="37"/>
      <path d="M288 258 V330 M292 296 C318 270 352 258 396 262 M300 294 L400 332"/>
      <ellipse cx="466" cy="292" rx="60" ry="37"/>
      <ellipse cx="656" cy="292" rx="60" ry="37"/>
      <path d="M730 330 V258 L852 330 V258"/>
      <ellipse cx="930" cy="292" rx="60" ry="37"/>
      <!-- bowl and chopsticks -->
      <path d="M496 470 L548 400 M512 472 L590 414" stroke-width="6"/>
      <ellipse cx="514" cy="462" rx="76" ry="9" stroke-width="5"/>
      <!-- waves -->
      <path d="M284 448 C330 470 372 500 404 534 Q502 552 600 534 C632 500 674 470 720 448" stroke-width="6"/>
      <path d="M284 476 C322 494 352 516 378 546 Q502 572 626 546 C652 516 682 494 720 476" stroke-width="6"/>
      <path d="M292 508 C318 522 340 538 356 556 M712 508 C686 522 664 538 648 556" stroke-width="6"/>
    </g>
    <g fill="currentColor">
      <path d="M440 466 C446 492 476 506 514 506 C552 506 582 492 588 466 Z"/>
      ${[[472, 62], [404, 98], [457, 106], [522, 112], [580, 101], [355, 158], [636, 163]].map(([x, y]) => blossom(x, y)).join("")}
      <path d="M392 228 C420 208 436 192 440 182 C446 196 458 206 474 212 C460 214 450 220 440 230 C428 222 412 222 392 228 Z M500 214 C516 200 526 192 532 186 C540 198 552 206 568 212 C552 214 540 220 532 228 C522 220 512 216 500 214 Z" opacity=".9"/>
    </g>
    <text x="508" y="379" text-anchor="middle" fill="currentColor" font-family="Montserrat, sans-serif" font-weight="500" font-size="38" letter-spacing="2">ASIAN KITCHEN</text>`;

  window.Logo = {
    viewBox: "0 0 1012 608",
    svg: (cls = "logo-svg") => `<svg class="${cls}" viewBox="0 0 1012 608" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Yoko Ono · Asian Kitchen">${art}</svg>`,
  };
})();
