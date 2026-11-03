// Pixar-lite 3D opening: a couple asks for the bill, the cashier sends them to the dice.
// Built from smooth primitives in Three.js (assets/vendor/three.min.js). Every frame is a pure function of time t,
// drawn from HyperFrames' hf-seek event, so renders are deterministic.
(function () {
  const T = window.THREE;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ease = {
    inOut: (k) => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2),
    out: (k) => 1 - Math.pow(1 - k, 3),
    back: (k) => { const c = 1.6, c3 = c + 1; return 1 + c3 * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
  };
  const seg = (t, t0, t1, fn = ease.inOut) => fn(clamp((t - t0) / (t1 - t0)));

  function paintTexture(w, h, draw) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    draw(c.getContext("2d"), w, h);
    const tex = new T.CanvasTexture(c);
    tex.colorSpace = T.SRGBColorSpace;
    return tex;
  }

  // Warm, bright, soft backgrounds painted once and blurred like a long lens.
  const terraceTex = () => paintTexture(1024, 1536, (g, w, h) => {
    const sky = g.createLinearGradient(0, 0, 0, h);
    sky.addColorStop(0, "#f2785a"); sky.addColorStop(0.4, "#ff9b6a"); sky.addColorStop(0.62, "#ffc98a"); sky.addColorStop(0.75, "#ffe0a8"); sky.addColorStop(1, "#e88a5c");
    g.fillStyle = sky; g.fillRect(0, 0, w, h);
    g.filter = "blur(26px)";
    const sun = g.createRadialGradient(w * 0.68, h * 0.62, 10, w * 0.68, h * 0.62, 320);
    sun.addColorStop(0, "#fff4d0"); sun.addColorStop(0.35, "#ffd98f"); sun.addColorStop(1, "rgba(255,190,120,0)");
    g.fillStyle = sun; g.fillRect(0, 0, w, h);
    g.fillStyle = "rgba(178,84,74,.75)";
    g.beginPath(); g.moveTo(0, h * 0.7); g.lineTo(w * 0.22, h * 0.6); g.lineTo(w * 0.4, h * 0.66); g.lineTo(w * 0.6, h * 0.56); g.lineTo(w * 0.8, h * 0.64); g.lineTo(w, h * 0.6); g.lineTo(w, h); g.lineTo(0, h); g.fill();
    g.filter = "blur(10px)"; g.fillStyle = "rgba(150,96,52,.85)";
    for (let x = 30; x < w; x += 150) g.fillRect(x, h * 0.2, 16, h * 0.62);
    g.fillRect(0, h * 0.2, w, 22);
    for (const [x, y, r, a] of [[120, 300, 40, .55], [330, 250, 26, .5], [560, 340, 46, .4], [860, 280, 34, .55], [940, 470, 50, .35], [220, 520, 30, .4]]) {
      g.fillStyle = `rgba(255,240,200,${a})`; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
    }
  });
  const cafeTex = () => paintTexture(1024, 1536, (g, w, h) => {
    const wall = g.createLinearGradient(0, 0, w, h);
    wall.addColorStop(0, "#ffb07e"); wall.addColorStop(0.5, "#f08a66"); wall.addColorStop(1, "#d8724e");
    g.fillStyle = wall; g.fillRect(0, 0, w, h);
    g.filter = "blur(22px)";
    for (const x of [180, 512, 844]) {
      const glow = g.createRadialGradient(x, 330, 10, x, 330, 220);
      glow.addColorStop(0, "rgba(255,246,214,.95)"); glow.addColorStop(1, "rgba(255,220,170,0)");
      g.fillStyle = glow; g.fillRect(0, 0, w, h);
      g.fillStyle = "#c9a36b"; g.beginPath(); g.ellipse(x, 300, 90, 40, 0, 0, Math.PI * 2); g.fill();
    }
    g.fillStyle = "rgba(120,70,40,.35)"; g.fillRect(0, h * 0.62, w, h * 0.4);
    g.fillStyle = "rgba(255,255,255,.18)";
    for (let i = 0; i < 6; i++) g.fillRect(80 + i * 160, h * 0.4, 90, 260);
  });

  function mat(color, opts = {}) {
    return new T.MeshPhysicalMaterial(Object.assign({ color, roughness: 0.55, metalness: 0 }, opts));
  }
  const SKIN = (c) => mat(c, { roughness: 0.48, sheen: 0.8, sheenRoughness: 0.5, sheenColor: new T.Color("#ffb59a"), clearcoat: 0.08 });
  const CLOTH = (c) => mat(c, { roughness: 0.85, sheen: 0.5, sheenColor: new T.Color("#ffffff") });
  const GLOSS = (c) => mat(c, { roughness: 0.25, clearcoat: 0.6 });

  function capsule(r, len, m) {
    const mesh = new T.Mesh(new T.CapsuleGeometry(r, len, 12, 28), m);
    mesh.castShadow = true; mesh.receiveShadow = true;
    return mesh;
  }
  function sphere(r, m, seg = 48) {
    const mesh = new T.Mesh(new T.SphereGeometry(r, seg, Math.round(seg * 0.75)), m);
    mesh.castShadow = true; mesh.receiveShadow = true;
    return mesh;
  }

  // A seated, waist-up character. Facing +z (the camera).
  function character(o) {
    const root = new T.Group();
    const skin = SKIN(o.skin), cloth = CLOTH(o.cloth), hair = GLOSS(o.hair);
    const torso = capsule(0.6, 0.55, cloth); torso.scale.set(1.18, 1, 0.82); torso.position.y = 1.12; root.add(torso);
    if (o.kind === "cashier") {
      const apron = new T.Mesh(new T.CylinderGeometry(0.73, 0.78, 0.9, 40, 1, true, -Math.PI * 0.32, Math.PI * 0.64), CLOTH("#1d1714"));
      apron.position.set(0, 0.92, 0.0); apron.material.side = T.DoubleSide; root.add(apron);
      const badge = new T.Mesh(new T.TorusGeometry(0.09, 0.012, 8, 32, Math.PI), GLOSS("#d8b26a"));
      badge.position.set(0, 1.0, 0.78); root.add(badge);
    }
    if (o.kind === "woman") {
      const neck = new T.Mesh(new T.TorusGeometry(0.2, 0.012, 8, 40, Math.PI), GLOSS("#e2c590"));
      neck.rotation.set(Math.PI * 0.52, 0, Math.PI); neck.position.set(0, 1.56, 0.32); root.add(neck);
    }
    const neck = capsule(0.15, 0.2, skin); neck.position.y = 1.68; root.add(neck);

    const head = new T.Group(); head.position.y = 1.78; root.add(head);
    const skull = sphere(0.52, skin, 64); skull.scale.set(1, 1.06, 0.96); skull.position.y = 0.44; head.add(skull);
    for (const s of [-1, 1]) { const ear = sphere(0.1, skin); ear.position.set(s * 0.5, 0.44, 0); ear.scale.set(0.6, 1, 0.8); head.add(ear); }

    const face = new T.Group(); face.position.y = 0.44; head.add(face);
    const eyes = new T.Group(); face.add(eyes);
    const white = mat("#fffaf2", { roughness: 0.15, clearcoat: 1 });
    const irisM = mat(o.iris || "#5a341c", { roughness: 0.2, clearcoat: 1 });
    const black = mat("#0e0805", { roughness: 0.1, clearcoat: 1 });
    const shine = new T.MeshBasicMaterial({ color: "#ffffff" });
    for (const s of [-1, 1]) {
      const e = new T.Group(); e.position.set(s * 0.19, 0.06, 0.4); eyes.add(e);
      const w = sphere(0.14, white); w.scale.set(1, 1.15, 0.55); e.add(w);
      const ir = sphere(0.088, irisM); ir.scale.set(1, 1.06, 0.4); ir.position.z = 0.065; e.add(ir);
      const pu = sphere(0.046, black); pu.scale.set(1, 1, 0.4); pu.position.z = 0.09; e.add(pu);
      const c1 = sphere(0.024, shine, 12); c1.position.set(-0.03, 0.04, 0.115); e.add(c1);
      const c2 = sphere(0.011, shine, 10); c2.position.set(0.032, -0.025, 0.112); e.add(c2);
    }
    const brows = new T.Group(); face.add(brows);
    for (const s of [-1, 1]) {
      const b = new T.Mesh(new T.TorusGeometry(0.11, 0.022, 10, 24, Math.PI * 0.75), hair);
      b.position.set(s * 0.19, 0.24, 0.44); b.rotation.z = Math.PI * 0.125; brows.add(b);
    }
    const nose = sphere(0.065, SKIN(o.skinShade)); nose.position.set(0, -0.07, 0.49); face.add(nose);
    for (const s of [-1, 1]) {
      const ch = sphere(0.1, new T.MeshBasicMaterial({ color: "#ff8a78", transparent: true, opacity: 0.28 }), 16);
      ch.scale.set(1, 0.6, 0.3); ch.position.set(s * 0.28, -0.1, 0.4); face.add(ch);
    }
    const mouthRed = mat("#8a2e26", { roughness: 0.4 });
    const smile = new T.Mesh(new T.TorusGeometry(0.085, 0.02, 10, 24, Math.PI), mouthRed);
    smile.rotation.z = Math.PI; smile.position.set(0, -0.2, 0.455); face.add(smile);
    const open = sphere(0.085, mat("#5a1e1a", { roughness: 0.6 }), 24); open.scale.set(1.15, 0.75, 0.35); open.position.set(0, -0.22, 0.45); face.add(open);
    const oh = sphere(0.06, mat("#5a1e1a", { roughness: 0.6 }), 24); oh.scale.set(0.8, 1.05, 0.35); oh.position.set(0, -0.23, 0.455); face.add(oh);

    // Sculpted hair, Pixar style: smooth shells, no strands
    const cap = new T.Mesh(new T.SphereGeometry(0.55, 48, 32, 0, Math.PI * 2, 0, Math.PI * (o.kind === "woman" ? 0.56 : 0.47)), hair);
    cap.position.y = 0.47; cap.rotation.x = -0.16; cap.castShadow = true; head.add(cap);
    if (o.kind === "man") { const q = sphere(0.24, hair); q.scale.set(1.3, 0.7, 0.9); q.position.set(0.1, 0.9, 0.24); head.add(q); }
    if (o.kind === "woman") {
      const back = capsule(0.48, 0.55, hair); back.position.set(0, 0.12, -0.2); back.scale.set(1.08, 1, 0.7); head.add(back);
      for (const s of [-1, 1]) { const lock = capsule(0.13, 0.55, hair); lock.position.set(s * 0.46, 0.1, 0.12); head.add(lock); }
      const fringe = sphere(0.3, hair); fringe.scale.set(1.5, 0.55, 0.8); fringe.position.set(-0.1, 0.82, 0.3); fringe.rotation.z = 0.25; head.add(fringe);
    }
    if (o.kind === "cashier") { const bun = sphere(0.21, hair); bun.position.set(0, 1.04, -0.12); head.add(bun); }

    const arms = {};
    for (const s of [-1, 1]) {
      const pivot = new T.Group(); pivot.position.set(s * 0.74, 1.5, 0.05); root.add(pivot);
      const sleeveM = o.kind === "man" ? CLOTH("#1b1716") : (o.kind === "cashier" ? CLOTH("#f3ece0") : cloth);
      const upper = capsule(0.15, 0.6, sleeveM); upper.position.y = -0.42; pivot.add(upper);
      if (o.kind === "man") { const cuff = new T.Mesh(new T.TorusGeometry(0.15, 0.03, 10, 28), GLOSS("#d8b26a")); cuff.rotation.x = Math.PI / 2; cuff.position.y = -0.76; pivot.add(cuff); }
      const hand = sphere(0.15, skin); hand.scale.set(1, 1.1, 0.85); hand.position.y = -0.92; pivot.add(hand);
      if (o.kind === "cashier" && s === 1) { const finger = capsule(0.045, 0.16, skin); finger.position.y = -1.13; pivot.add(finger); }
      arms[s] = pivot;
    }
    root.userData = { head, eyes, brows, smile, open, oh, arms };
    return root;
  }

  function mouth(c, state) {
    const u = c.userData;
    u.smile.visible = state === "smile"; u.open.visible = state === "open"; u.oh.visible = state === "oh";
  }
  const talk = (t, t0, t1) => (t >= t0 && t < t1 ? (Math.floor((t - t0) / 0.11) % 3 === 2 ? "oh" : (Math.floor((t - t0) / 0.11) % 2 ? "smile" : "open")) : null);
  // Resting arms: forearms forward onto the table, elbows slightly out.
  function rest(c, sides) { for (const s of sides) { c.userData.arms[s].rotation.x = -1.15; c.userData.arms[s].rotation.z += s * 0.05; } }
  const blink = (t, at) => (t > at && t < at + 0.13 ? 0.12 : 1);

  function build(canvas) {
    const renderer = new T.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
    renderer.setPixelRatio(1); renderer.setSize(1080, 1920, false);
    renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.12;
    renderer.outputColorSpace = T.SRGBColorSpace;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;

    const scene = new T.Scene();
    const camera = new T.PerspectiveCamera(40, 1080 / 1920, 0.1, 60);
    scene.add(new T.HemisphereLight("#fff3e2", "#c08a64", 1.1));
    const key = new T.DirectionalLight("#ffe2c0", 2.4); key.position.set(-3, 5, 5); key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024); key.shadow.radius = 6; key.shadow.camera.left = -5; key.shadow.camera.right = 5; key.shadow.camera.top = 5; key.shadow.camera.bottom = -2;
    scene.add(key);
    const rim = new T.DirectionalLight("#ffb27a", 2.2); rim.position.set(2.5, 3.5, -5); scene.add(rim);
    const fill = new T.PointLight("#ffd1b8", 6, 20); fill.position.set(3, 2.2, 5); scene.add(fill);

    // Terrace set (P1, P3)
    const terrace = new T.Group(); scene.add(terrace);
    const bg1 = new T.Mesh(new T.PlaneGeometry(12, 18), new T.MeshBasicMaterial({ map: terraceTex(), toneMapped: false })); bg1.position.set(0, 2.6, -5); terrace.add(bg1);
    const table = new T.Mesh(new T.BoxGeometry(6, 0.14, 2.2), mat("#c58653", { roughness: 0.45, clearcoat: 0.3 })); table.position.set(0, 0.95, 1.25); table.receiveShadow = true; terrace.add(table);
    const tableFront = new T.Mesh(new T.BoxGeometry(6, 1.2, 0.1), mat("#9a6036", { roughness: 0.6 })); tableFront.position.set(0, 0.35, 2.33); terrace.add(tableFront);
    for (const x of [-1.05, 1.05]) {
      const plate = new T.Mesh(new T.CylinderGeometry(0.38, 0.3, 0.05, 48), mat("#fffaf2", { roughness: 0.2, clearcoat: 1 })); plate.position.set(x, 1.05, 1.5); plate.castShadow = true; plate.receiveShadow = true; terrace.add(plate);
      const rimG = new T.Mesh(new T.TorusGeometry(0.33, 0.012, 8, 48), GLOSS("#d8b26a")); rimG.rotation.x = Math.PI / 2; rimG.position.set(x, 1.08, 1.5); terrace.add(rimG);
    }
    const man = character({ kind: "man", skin: "#e9b58e", skinShade: "#d89c74", hair: "#3a2416", cloth: "#2b2730" });
    const woman = character({ kind: "woman", skin: "#f6cfaa", skinShade: "#e8b48c", hair: "#8a3f22", cloth: "#c2414e", iris: "#3a5a2a" });
    man.position.set(-0.86, 0, 0); woman.position.set(0.86, 0, 0.05); terrace.add(man, woman);

    // Café counter set (P2)
    const cafe = new T.Group(); scene.add(cafe);
    const bg2 = new T.Mesh(new T.PlaneGeometry(12, 18), new T.MeshBasicMaterial({ map: cafeTex(), toneMapped: false })); bg2.position.set(0, 2.6, -5); cafe.add(bg2);
    const counter = new T.Mesh(new T.BoxGeometry(6, 1.15, 1.1), mat("#b0703f", { roughness: 0.45, clearcoat: 0.35 })); counter.position.set(0, 0.5, 1.15); counter.receiveShadow = true; cafe.add(counter);
    const edge = new T.Mesh(new T.BoxGeometry(6.02, 0.06, 1.14), GLOSS("#d8b26a")); edge.position.set(0, 1.09, 1.15); cafe.add(edge);
    const term = new T.Mesh(new T.BoxGeometry(0.45, 0.32, 0.3), mat("#2a2420", { roughness: 0.3 })); term.position.set(0.95, 1.28, 1.25); term.rotation.x = -0.4; term.castShadow = true; cafe.add(term);
    const screen = new T.Mesh(new T.PlaneGeometry(0.34, 0.16), new T.MeshBasicMaterial({ color: "#5fd39a" })); screen.position.set(0.95, 1.34, 1.42); screen.rotation.x = -0.4; cafe.add(screen);
    const diceTable = new T.Group(); diceTable.position.set(1.95, 0.55, -1.9); diceTable.rotation.y = -0.45; cafe.add(diceTable);
    const dtRim = new T.Mesh(new T.BoxGeometry(1.7, 0.3, 1.1), mat("#8a5532", { roughness: 0.5 })); dtRim.castShadow = true; diceTable.add(dtRim);
    const felt = new T.Mesh(new T.BoxGeometry(1.5, 0.31, 0.9), new T.MeshStandardMaterial({ color: "#2fb066", emissive: "#1d8a4c", emissiveIntensity: 0.35, roughness: 0.95 })); felt.position.y = 0.01; diceTable.add(felt);
    const cashier = character({ kind: "cashier", skin: "#d59a6e", skinShade: "#bf8458", hair: "#22160f", cloth: "#f3ece0" });
    cafe.add(cashier);
    const guest = new T.Group(); cafe.add(guest);
    const gSleeve = capsule(0.17, 1.4, CLOTH("#1b1716")); gSleeve.rotation.z = Math.PI / 2 - 0.25; guest.add(gSleeve);
    const gCuff = new T.Mesh(new T.TorusGeometry(0.17, 0.03, 10, 28), GLOSS("#d8b26a")); gCuff.rotation.y = Math.PI / 2; gCuff.rotation.z = -0.25; gCuff.position.set(0.82, 0.21, 0); guest.add(gCuff);
    const gHand = sphere(0.17, SKIN("#e9b58e")); gHand.position.set(1.0, 0.27, 0); guest.add(gHand);
    const card = new T.Mesh(new T.BoxGeometry(0.42, 0.27, 0.02), GLOSS("#15110e")); card.position.set(1.18, 0.42, 0.05); card.rotation.z = 0.2; guest.add(card);
    const chip = new T.Mesh(new T.BoxGeometry(0.07, 0.05, 0.022), GLOSS("#d8b26a")); chip.position.set(1.06, 0.45, 0.07); chip.rotation.z = 0.2; guest.add(chip);

    function renderAt(t) {
      const p1 = t < 3.125, p2 = t >= 3.125 && t < 6.875;
      terrace.visible = !p2; cafe.visible = p2;
      for (const c of [man, woman, cashier]) { mouth(c, "smile"); c.userData.eyes.scale.y = 1; c.userData.brows.position.y = 0; c.userData.head.rotation.set(0, 0, 0); c.userData.arms[-1].rotation.set(0, 0, 0); c.userData.arms[1].rotation.set(0, 0, 0); }
      if (p1) {
        camera.position.set(lerp(-0.12, 0.12, t / 3.125), 2.0, lerp(9.0, 8.5, t / 3.125)); camera.lookAt(0, 2.0, 0);
        man.userData.arms[1].rotation.z = 2.6 * seg(t, 0.35, 0.8, ease.back);
        man.userData.head.rotation.z = -0.1 * seg(t, 0.3, 0.7);
        mouth(man, talk(t, 0.6, 1.26) || "smile");
        woman.userData.head.rotation.y = -0.35 * seg(t, 1.4, 1.9);
        woman.userData.eyes.scale.y = blink(t, 0.9); man.userData.eyes.scale.y = blink(t, 2.2);
        rest(man, [-1]); rest(woman, [-1, 1]); if (t < 0.35) rest(man, [1]);
      } else if (p2) {
        const u = t - 3.125;
        camera.position.set(lerp(0.15, -0.1, u / 3.75), 2.1, lerp(8.8, 8.2, u / 3.75)); camera.lookAt(-0.1, 2.05, 0);
        const g = seg(u, 0, 0.6, ease.out); guest.position.set(lerp(-3.2, -1.9, g), 1.45, 1.9);
        const arm = cashier.userData.arms[1];
        let z = 2.75 * seg(u, 0.45, 0.85, ease.back);
        if (u > 0.85 && u < 1.6) z += Math.sin((u - 0.85) * Math.PI * 2 / 0.32) * 0.18;
        z = lerp(z, 1.75, seg(u, 2.0, 2.45));
        arm.rotation.z = z;
        const h = cashier.userData.head;
        h.rotation.z = (u > 0.85 && u < 1.6 ? Math.sin((u - 0.85) * Math.PI * 2 / 0.32) * 0.1 : 0) - 0.12 * seg(u, 2.0, 2.45);
        h.rotation.y = 0.35 * seg(u, 2.0, 2.45);
        cashier.userData.brows.position.y = 0.05 * seg(u, 0.6, 0.8);
        mouth(cashier, talk(u, 0.75, 2.2) || "smile");
        cashier.userData.eyes.scale.y = blink(u, 2.6);
        rest(cashier, [-1]);
      } else {
        const u = t - 6.875;
        camera.position.set(0, 2.3, lerp(7.4, 6.9, clamp(u / 1.25))); camera.lookAt(0, 2.45, 0);
        man.userData.head.rotation.y = 0.45 * seg(u, 0.05, 0.35, ease.back);
        woman.userData.head.rotation.y = -0.45 * seg(u, 0.12, 0.42, ease.back);
        for (const c of [man, woman]) { c.userData.brows.position.y = 0.06 * seg(u, 0.15, 0.35); if (u > 0.2) mouth(c, "oh"); rest(c, [-1, 1]); }
      }
      renderer.render(scene, camera);
    }
    return { renderAt };
  }

  window.Avatars3D = { build };
})();
