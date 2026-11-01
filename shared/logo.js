// Yoko Ono · Asian Kitchen logo as inline SVG, in currentColor so the colour comes from CSS.
// The artwork is traced from the restaurant's own logo (logo-path.js, made by trace-logo.py);
// "ASIAN KITCHEN" is too thin to trace, so it is set in the page's Montserrat.
// Load logo-path.js first, then insert with Logo.svg().
(function () {
  const { viewBox, d } = window.LOGO_PATH;
  window.Logo = {
    viewBox,
    svg: (cls = "logo-svg") => `<svg class="${cls}" viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Yoko Ono · Asian Kitchen">
      <path d="${d}" fill="currentColor" fill-rule="evenodd"/>
      <text x="382" y="522" text-anchor="middle" fill="currentColor" font-family="Montserrat, sans-serif" font-weight="500" font-size="29" letter-spacing="4.2">ASIAN KITCHEN</text>
    </svg>`,
  };
})();
