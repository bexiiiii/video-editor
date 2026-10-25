/* reels-studio · Style A "3D Keyword" (Zaytsev) component library → global `RSA`.
 *
 * Contract (references/contracts.md): every builder is `RSA.x(container, props, tl, at) → HTMLElement`.
 * It builds its DOM at the FINAL layout, then adds seek-safe `fromTo` tweens to the paused timeline `tl`
 * starting at local time `at` (seconds). Nothing reads a clock, nothing uses Math.random (RS.rand only),
 * and text never exits on its own — exits happen only through RSA.transition*.
 *
 * Requires: GSAP 3, assets/shared/runtime.js (RS), assets/style-a/tokens.css.
 * Numbers in the JSDoc come from references/teardowns/style-a/*.md (Dej = DejCkBdNC6h, DeV = DeVzimJCYVp,
 * Der0 = Der0UBDNBmZ, Dey = DeyJKx9t_aA).
 *
 * Coordinates: x/y props are stage pixels (1080×1920) of the element's CENTRE. Elements are centred with a
 * 0×0 flex anchor (`.rsa-at`) so GSAP owns `transform` on the child without CSS-transform conflicts.
 */
(function () {
  "use strict";
  if (!window.RS) throw new Error("RSA needs assets/shared/runtime.js (RS) loaded first");
  const RS = window.RS;
  const RSA = {};
  const SVGNS = "http://www.w3.org/2000/svg";

  /* ───────────────────────────── private helpers ───────────────────────────── */

  let uid = 0;
  const nextId = (p) => `rsa-${p}-${++uid}`;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const num = (v, d) => (typeof v === "number" && isFinite(v) ? v : d);
  /** Resolve "76%" (of 1920 / 1080) or a number to px. */
  const pos = (v, axisLen, d) => (typeof v === "string" && v.endsWith("%") ? (parseFloat(v) / 100) * axisLen : num(v, d));

  function el(tag, cls, parent, style) {
    const e = RS.el(tag, cls, parent);
    if (style) Object.assign(e.style, style);
    return e;
  }

  /** 0×0 anchor centred on (x, y); children are flex-centred on that point. */
  function anchor(container, x, y, z) {
    return el("div", "rsa-at", container, { left: `${x}px`, top: `${y}px`, zIndex: z == null ? "" : String(z) });
  }

  /** Split headline text into lines: array, "a / b" or "a\nb". */
  function toLines(text) {
    if (Array.isArray(text)) return text;
    return String(text).split(/\s*(?:\/|\n)\s*/).filter(Boolean);
  }

  /**
   * Directional (1-axis) motion blur through an SVG filter on `node`, tweening stdDeviation from→to.
   * Separate from CSS `filter: blur()` tweens: put it on a wrapper that no other tween filters.
   */
  function dirBlur(tl, node, at, dur, axis, from, to, ease, region) {
    let f = node.__rsaBlur;
    if (!f) {
      const id = nextId("mb");
      const svg = document.createElementNS(SVGNS, "svg");
      svg.setAttribute("width", "0"); svg.setAttribute("height", "0");
      svg.style.position = "absolute";
      const rg = region || [-60, 220];
      svg.innerHTML = `<filter id="${id}" x="${rg[0]}%" y="${rg[0]}%" width="${rg[1]}%" height="${rg[1]}%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="0 0"/></filter>`;
      node.parentNode.insertBefore(svg, node);
      node.style.filter = `url(#${id})`;
      f = node.__rsaBlur = svg.querySelector("feGaussianBlur");
    }
    const v = (a) => (axis === "x" ? `${a} 0` : `0 ${a}`);
    tl.fromTo(f, { attr: { stdDeviation: v(from) } },
      { attr: { stdDeviation: v(to) }, duration: dur, ease: ease || "power2.out", immediateRender: false }, at);
    return f;
  }

  /**
   * Anchored typewriter: chars pre-laid-out, grouped per word (so lines wrap naturally), each char
   * fades + un-blurs (Dej §4B: ~24 cps, 3-frame soft leading glyph, no reflow, no cursor).
   * @returns {HTMLElement[]} char spans
   */
  function typeInto(node, text, tl, at, cps, o) {
    o = o || {};
    node.innerHTML = String(text).split(/(\s+)/).map((tok) => {
      if (/^\s+$/.test(tok)) return " ";
      return `<span class="rsa-tw">${[...tok].map((c) => `<span class="c">${esc(c)}</span>`).join("")}</span>`;
    }).join("");
    const cs = [...node.querySelectorAll(".c")];
    if (cs.length) {
      tl.fromTo(cs, { opacity: 0, filter: `blur(${o.blur ?? 6}px)` },
        { opacity: 1, filter: "blur(0px)", duration: o.dur ?? 0.12, ease: "none", stagger: 1 / (cps || 24) }, at);
    }
    return cs;
  }

  /** Headline-style blur-rise for an arbitrary element (Dej §4A). */
  function blurRise(tl, node, at, o) {
    o = o || {};
    tl.fromTo(node, { opacity: 0, y: o.y ?? 24, filter: `blur(${o.blur ?? 14}px)` },
      { opacity: 1, y: 0, filter: "blur(0px)", duration: o.dur ?? 0.36, ease: o.ease || "expo.out" }, at);
  }

  /* Placeholder "inflated" 3D objects (real runs use generated transparent PNGs from assets/img). */
  const GITHUB = '<path fill="currentColor" d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2c-3.2.7-3.87-1.37-3.87-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.76 2.69 1.25 3.35.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5Z"/>';
  RSA.icons = { github: (s) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24">${GITHUB}</svg>` };

  /**
   * Build a placeholder 3D object node.
   * @param {object} p {src?, emoji?, blob?: 'tile'|'tile-dark'|'disc'|'coin'|'orb'|'bookmark', glyph?, color?, size}
   */
  function object3D(p) {
    const size = num(p.size, 260);
    const o = el("div", "rsa-obj", null, { width: `${size}px`, height: `${size}px` });
    if (p.src) {
      o.classList.add("rsa-obj--img");
      o.innerHTML = `<img src="${esc(p.src)}" alt="">`;
    } else if (p.blob === "tile" || p.blob === "tile-dark") {
      const t = el("div", "rsa-tile" + (p.blob === "tile-dark" ? " rsa-tile--dark" : ""), o, { width: `${size}px`, height: `${size}px` });
      const g = el("span", "rsa-emoji", t, { fontSize: `${size * 0.56}px` });
      g.textContent = p.emoji || p.glyph || "★";
    } else if (p.blob === "disc") {
      // glossy black badge with a white mark (GitHub-badge stand-in)
      o.innerHTML = `<div style="width:100%;height:100%;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;
        background:radial-gradient(70% 60% at 32% 25%,#4a4f55 0%,#1b1e22 45%,#050607 100%);
        box-shadow:inset 0 -14px 26px rgba(0,0,0,.6),inset 0 10px 18px rgba(255,255,255,.18),0 26px 40px rgba(0,0,0,.28)">
        ${RSA.icons.github(Math.round(size * 0.6))}</div>`;
    } else if (p.blob === "coin") {
      o.innerHTML = coinSVG(size, p.color || "#1E8BFF");
    } else if (p.blob === "bookmark") {
      o.innerHTML = bookmarkSVG(size, p.color);
    } else if (p.blob === "orb") {
      const c = p.color || "#1EB4F6";
      o.innerHTML = `<div style="width:100%;height:100%;border-radius:50%;background:radial-gradient(60% 55% at 35% 28%,#fff 0%,${c} 28%,${c} 55%,rgba(0,0,0,.55) 120%);box-shadow:0 20px 40px rgba(0,0,0,.25)"></div>`;
    } else {
      const g = el("span", "rsa-emoji", o, { fontSize: `${size * 0.9}px` });
      g.textContent = p.emoji || "🤖";
    }
    return o;
  }

  function coinSVG(size, c) {
    const id = nextId("coin");
    return `<svg width="${size}" height="${size * 0.42}" viewBox="0 0 200 84" style="overflow:visible">
      <defs><linearGradient id="${id}s" x1="0" x2="1"><stop offset="0" stop-color="#0B4FC4"/><stop offset=".35" stop-color="${c}"/><stop offset=".55" stop-color="#7CC4FF"/><stop offset="1" stop-color="#0A44B0"/></linearGradient>
      <radialGradient id="${id}t" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#E8F5FF"/><stop offset=".25" stop-color="#6DB8FF"/><stop offset=".7" stop-color="${c}"/><stop offset="1" stop-color="#0D5AD8"/></radialGradient></defs>
      <path d="M4 30 v22 a96 30 0 0 0 192 0 v-22z" fill="url(#${id}s)"/>
      <ellipse cx="100" cy="30" rx="96" ry="28" fill="url(#${id}t)"/>
      <ellipse cx="100" cy="30" rx="70" ry="18" fill="none" stroke="rgba(255,255,255,.45)" stroke-width="5"/>
      <ellipse cx="78" cy="20" rx="30" ry="6" fill="rgba(255,255,255,.55)"/></svg>`;
  }

  /** Glossy inflated 3D blue bookmark (CSS/SVG, no image). Aspect 0.82. */
  function bookmarkSVG(size, color) {
    const id = nextId("bm");
    const c = color || "#1E8BFF";
    const w = size * 0.82, h = size;
    return `<svg width="${w}" height="${h}" viewBox="0 0 164 200" style="overflow:visible">
      <defs>
        <linearGradient id="${id}b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7CCBFF"/><stop offset=".35" stop-color="${c}"/><stop offset="1" stop-color="#0A4FD0"/></linearGradient>
        <linearGradient id="${id}d" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B57D8"/><stop offset="1" stop-color="#06328F"/></linearGradient>
        <radialGradient id="${id}g" cx=".3" cy=".18" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".35" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
        <filter id="${id}f" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
        <filter id="${id}s" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
      </defs>
      <ellipse cx="86" cy="196" rx="62" ry="10" fill="rgba(0,30,90,.30)" filter="url(#${id}s)"/>
      <path d="M30 14 h104 a26 26 0 0 1 26 26 v146 a10 10 0 0 1-16 8 l-58-40 l-58 40 a10 10 0 0 1-16-8 v-146 a26 26 0 0 1 26-26z" fill="url(#${id}d)" stroke="url(#${id}d)" stroke-width="22" stroke-linejoin="round" transform="translate(4 7)"/>
      <path d="M30 10 h104 a26 26 0 0 1 26 26 v146 a10 10 0 0 1-16 8 l-58-40 l-58 40 a10 10 0 0 1-16-8 v-146 a26 26 0 0 1 26-26z" fill="url(#${id}b)" stroke="url(#${id}b)" stroke-width="22" stroke-linejoin="round"/>
      <path d="M30 10 h104 a26 26 0 0 1 26 26 v146 a10 10 0 0 1-16 8 l-58-40 l-58 40 a10 10 0 0 1-16-8 v-146 a26 26 0 0 1 26-26z" fill="url(#${id}g)"/>
      <path d="M26 30 q4-14 22-15 h64" stroke="#fff" stroke-opacity=".9" stroke-width="9" stroke-linecap="round" fill="none" filter="url(#${id}f)"/>
      <path d="M150 50 v120" stroke="#04318A" stroke-opacity=".35" stroke-width="10" stroke-linecap="round" fill="none" filter="url(#${id}f)"/>
      <ellipse cx="54" cy="150" rx="8" ry="22" fill="#fff" fill-opacity=".28" filter="url(#${id}f)"/></svg>`;
  }

  /* ───────────────────────────── layers & backgrounds ───────────────────────────── */

  const THEMES = {
    dark: { bg: "dark", grid: "dark", ink: "dark" },
    light: { bg: "light", grid: "light", ink: "light" },
    curtain: { bg: "curtain", ink: "accent" },
    space: { bg: "space", fx: "stars", ink: "accent" },
    navy: { bg: "navy", fx: "rays", grid: "ray", ink: "accent" },
    green: { bg: "green", fx: "rays", grid: "ray", ink: "accent" },
    maroon: { bg: "maroon", fx: "rays", grid: "maroon", ink: "accent" },
    teal: { bg: "teal", ink: "accent" },
    emerald: { bg: "emerald", ink: "accent" },
    orange: { bg: "orange", ink: "accent" },
    lavender: { bg: "lavender", ink: "light" },
    none: { bg: "none", ink: "dark" }, // transparent overlay over talking-head footage (layout head-side)
  };
  RSA.themes = Object.keys(THEMES);

  /**
   * Pleated velvet curtain (Dej hook) as real shading instead of a flat stripe gradient: a seeded,
   * vertically-stretched fractal-noise height map lit by feDiffuseLighting (+ a satin specular), so pleat
   * widths vary naturally (≈18–60 px). Then: warm top glow, vertical light fall-off to near-black by ~70 %,
   * a second gold-lit copy of the same folds masked to a spotlight at the right edge (gold catches the
   * pleats rather than a flat blob), and a soft side vignette. Static → rasterised once by Chrome.
   */
  function curtain(bg, seed) {
    const id = nextId("cur");
    const fold = (lit, extra) => `<feTurbulence type="fractalNoise" baseFrequency="0.016 0.00004" numOctaves="2" seed="${seed}" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.2 0 0 0 -0.1" result="h"/>
      <feDiffuseLighting in="h" surfaceScale="30" diffuseConstant="1.25" lighting-color="${lit}" result="d"><feDistantLight azimuth="200" elevation="38"/></feDiffuseLighting>${extra || ""}`;
    const svg = (inner) => `<svg class="rsa-cur-svg" width="1080" height="1920" viewBox="0 0 1080 1920">${inner}</svg>`;
    bg.insertAdjacentHTML("beforeend", svg(`<defs><filter id="${id}r" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">${fold("#ff1a0e",
      `<feSpecularLighting in="h" surfaceScale="30" specularConstant=".35" specularExponent="14" lighting-color="#ff8a6a" result="s"><feDistantLight azimuth="200" elevation="48"/></feSpecularLighting>
       <feComposite in="s" in2="d" operator="arithmetic" k2="1" k3=".55"/>`)}</filter></defs>
      <rect width="1080" height="1920" fill="#000" filter="url(#${id}r)"/>`));
    el("div", "rsa-cur-top", bg);
    el("div", "rsa-cur-fall", bg);
    bg.insertAdjacentHTML("beforeend", svg(`<defs><filter id="${id}g" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">${fold("#f2bf86")}</filter>
      <radialGradient id="${id}m" gradientUnits="userSpaceOnUse" cx="1080" cy="1430" r="560" gradientTransform="translate(1080 1430) scale(1 1.35) translate(-1080 -1430)">
        <stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
      <mask id="${id}k" maskUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1920"><rect width="1080" height="1920" fill="url(#${id}m)"/></mask></defs>
      <rect x="380" y="760" width="700" height="1160" fill="#000" filter="url(#${id}g)" mask="url(#${id}k)"/>`));
    el("div", "rsa-cur-vig", bg);
    el("div", "rsa-cur-glow", bg);
  }

  /**
   * Background plate for a theme (CSS-only).
   * @param {HTMLElement} container
   * @param {{theme?: string, drift?: number, grid?: boolean, seed?: number}} props
   *   theme: dark | light | curtain | space | navy | green | maroon | teal | emerald | orange | lavender | none
   *   ("accent:<name>" accepted; `none` = transparent plate for overlays on footage). seed = curtain fold seed (default 11).
   *   drift: seconds of slow light-ray/glow drift (the only BG motion in the refs); 0 = static.
   * @returns {HTMLElement} `.rsa-bg` (its `.grid` property = dot-grid element, if any)
   */
  RSA.background = function (container, props, tl, at) {
    props = props || {};
    const name = String(props.theme || "dark").replace(/^accent:/, "");
    const t = THEMES[name] || THEMES.dark;
    const bg = el("div", `rsa-bg rsa-bg--${t.bg}`, container);
    if (t.bg === "curtain") curtain(bg, props.seed || 11);
    let fx = null;
    if (t.fx) fx = el("div", `rsa-fx rsa-fx--${t.fx}`, bg);
    if (t.grid && props.grid !== false) bg.grid = el("div", `rsa-grid rsa-grid--${t.grid}`, bg);
    if (fx && props.drift && tl) {
      tl.fromTo(fx, { x: -30, y: -20 }, { x: 30, y: 20, duration: props.drift, ease: "none" }, at || 0);
    }
    bg.dataset.theme = name;
    return bg;
  };

  /**
   * One scene layer: background + content (+ inner wrapper for SVG motion blur) + overlay for shared elements.
   * Put the returned `.root` inside a HyperFrames clip (or make the clip itself). Never tween `.root`.
   * @param {HTMLElement} container
   * @param {{theme?: string, drift?: number}} props
   * @returns {HTMLElement} root, with `.bg .content .inner .over .theme` properties
   */
  RSA.layer = function (container, props, tl, at) {
    props = props || {};
    const name = String(props.theme || "dark").replace(/^accent:/, "");
    const t = THEMES[name] || THEMES.dark;
    const root = el("div", `rsa-layer rsa-theme-${t.ink}`, container);
    root.bg = RSA.background(root, props, tl, at);
    root.content = el("div", "rsa-content", root);
    root.inner = el("div", "rsa-inner", root.content);
    root.over = el("div", "rsa-over", root);
    root.theme = name;
    return root;
  };

  /* ───────────────────────────── text ───────────────────────────── */

  /**
   * Keyword headline — words pre-laid-out on ≤2 centred lines, each word blur-rises in place.
   * Motion (Dej §4A, Der0 §4.1): opacity 0→1, blur 14→0, y +24→0, 0.36 s, expo.out; words either on their
   * transcript times (+0.12 s after onset is the director's job) or staggered 0.12 s.
   * @param {object} props
   * @param {string|string[]} props.text   "нужны / плагины?" ("/" or "\n" = line break) or array of lines. ≤22 chars/line.
   * @param {Array<{w:string,t:number}>} [props.words] per-word reveal times (local), in reading order.
   * @param {number} [props.stagger=0.12]
   * @param {string[]} [props.pills]  words that get a keyword-pill wipe (Der0 «роботов»)
   * @param {'top'|'bottom'} [props.position='top']  bottom = headline-bottom variant (DeV), centre y≈70%
   * @param {number} [props.y] block centre y (px) override; [props.size] px; [props.weight]; [props.halo] dark text halo (Dey)
   * @returns {HTMLElement} `.rsa-headline` (`.words` = word spans)
   */
  RSA.headline = function (container, props, tl, at) {
    const lines = toLines(props.text);
    const longest = Math.max(...lines.map((l) => l.length));
    const h = el("div", "rsa-headline");
    if (props.position === "bottom") h.classList.add("rsa-headline--bottom");
    if (!props.size && longest > 16) h.classList.add("rsa-headline--long");
    if (props.size) h.style.fontSize = `${props.size}px`;
    if (props.weight) h.style.fontWeight = String(props.weight);
    if (props.halo) h.classList.add("rsa-headline--halo");
    if (props.y != null) h.style.top = `${pos(props.y, 1920) - 1000}px`;
    if (props.color) h.style.color = props.color;
    container.appendChild(h);
    const stagger = props.stagger ?? 0.12;
    const timed = props.words || [];
    let k = 0;
    const spans = [];
    const pills = (props.pills || []).map((s) => s.toLowerCase());
    lines.forEach((line) => {
      const ln = el("div", "rsa-line", h);
      const ws = line.split(/\s+/).filter(Boolean).map((w) => {
        const t = timed[k] ? timed[k].t : at + k * stagger;
        k++;
        return { w, t };
      });
      const s = RS.words(ln, ws, tl, { blur: 14, y: 24, dur: 0.36, ease: "expo.out", highlight: pills, hlClass: "rsa-pill" });
      s.forEach((sp, i) => {
        if (sp.classList.contains("rsa-pill")) pillWipe(tl, sp, ws[i].t);
      });
      spans.push(...s);
    });
    h.words = spans;
    return h;
  };

  function pillWipe(tl, node, t) {
    // Der0 §4.4: clip reveal L→R, rotate −8°→0, 0.35 s power3.out
    tl.fromTo(node, { clipPath: "inset(0% 100% 0% 0% round 999px)", rotation: -8 },
      { clipPath: "inset(0% 0% 0% 0% round 999px)", rotation: 0, duration: 0.35, ease: "power3.out" }, t);
  }

  /**
   * Grey caption — typewriter (~24 cps, per-char blur), anchored at its final centred box (y≈76%).
   * @param {object} props {text: string|string[] (lines), y?: px|'%', cps?=24, color?, size?=42}
   * @returns {HTMLElement}
   */
  RSA.caption = function (container, props, tl, at) {
    const c = el("div", "rsa-caption", container);
    if (props.y != null) c.style.top = `${pos(props.y, 1920) - 500}px`;
    if (props.color) c.style.color = props.color;
    if (props.size) c.style.fontSize = `${props.size}px`;
    const lines = Array.isArray(props.text) ? props.text : [props.text];
    let t = at;
    const cps = props.cps || 24;
    lines.forEach((line) => {
      const ln = el("div", "rsa-typed", c);
      typeInto(ln, line, tl, t, cps);
      t += line.length / cps;
    });
    return c;
  };

  /**
   * Free label typed at a point (icon labels, card titles, recap lines).
   * @param {object} props {text, x, y, size?=44, color?, weight?, cps?=24, cls?}
   */
  RSA.label = function (container, props, tl, at) {
    const a = anchor(container, props.x, props.y);
    const l = el("div", "rsa-label " + (props.cls || ""), a);
    if (props.size) l.style.fontSize = `${props.size}px`;
    if (props.color) l.style.color = props.color;
    if (props.weight) l.style.fontWeight = String(props.weight);
    typeInto(l, props.text, tl, at, props.cps || 24);
    return l;
  };

  /* ───────────────────────────── objects ───────────────────────────── */

  /**
   * Hero 3D object (one per scene). Transparent PNG via `src`; placeholders via `emoji`/`blob`.
   * Entries (Dej §5, DeV §5): pop = scale .1→1 + blur 10→0, 0.3 s back.out(1.4) · rise = from +y 900, blur, 0.38 s
   * expo.out + vertical motion blur · slide = from ±640 px with horizontal motion blur, 0.4 s expo.out ·
   * drop = falls from above (power3.in, 0.32 s) then squash-settles · ghost = grey semi-transparent → full colour.
   * Idle: none by default (refs hold still); `idle:{amp=8, period=3, until}` gives a seek-safe sine bob (Der0 robot).
   * @param {object} props {src?, emoji?, blob?, size=300, x=540, y=1000, entry='pop', from='right'|'left'|'below'|'above', shadow=true, idle?}
   * @returns {HTMLElement} the object node (`.anchor` = positioned wrapper)
   */
  RSA.hero = function (container, props, tl, at) {
    const x = num(props.x, 540), y = num(props.y, 1000), size = num(props.size, 300);
    const a = anchor(container, x, y);
    if (props.shadow !== false) {
      const sh = el("div", "rsa-contact", a, { width: `${size * 0.8}px`, height: `${size * 0.14}px`, position: "absolute",
        left: `${-size * 0.4}px`, top: `${size * 0.47}px` });
      tl.fromTo(sh, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.4, ease: "power3.out" }, at + 0.05);
    }
    const mb = el("div", "rsa-mb", a);
    const o = object3D(Object.assign({ size }, props));
    mb.appendChild(o);
    const entry = props.entry || "pop";
    if (entry === "pop") {
      tl.fromTo(o, { opacity: 0, scale: 0.1, filter: "blur(10px)" },
        { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "back.out(1.4)" }, at);
    } else if (entry === "rise") {
      const d = props.from === "above" ? -1 : 1;
      // opacity 0 at rest so the object never peeks in before its entry time
      tl.fromTo(o, { y: 900 * d, scale: 0.85, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 0.38, ease: "expo.out" }, at);
      dirBlur(tl, mb, at, 0.3, "y", 36, 0, "power2.out");
    } else if (entry === "slide") {
      const d = props.from === "left" ? -1 : 1;
      tl.fromTo(o, { x: 640 * d, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: "expo.out" }, at);
      dirBlur(tl, mb, at, 0.32, "x", 60, 0, "power2.out");
    } else if (entry === "drop") {
      tl.fromTo(o, { y: -1300, opacity: 1 }, { y: 0, duration: 0.32, ease: "power3.in" }, at);
      tl.fromTo(o, { scaleY: 1, scaleX: 1 }, { keyframes: [{ scaleY: 0.86, scaleX: 1.06, duration: 0.07 }, { scaleY: 1, scaleX: 1, duration: 0.16, ease: "power2.out" }], immediateRender: false }, at + 0.32);
      dirBlur(tl, mb, at, 0.32, "y", 0, 22, "power3.in");
      dirBlur(tl, mb, at + 0.32, 0.08, "y", 22, 0, "none");
    } else if (entry === "ghost") {
      tl.fromTo(o, { opacity: 0.35, filter: "grayscale(1) blur(2px)" }, { opacity: 1, filter: "grayscale(0) blur(0px)", duration: 0.25, ease: "power2.out" }, at);
    }
    if (props.idle) idleBob(tl, mb, at + 0.45, props.idle);
    o.anchor = a;
    return o;
  };

  /** Seek-safe sine bob: finite yoyo repeat inside the scene window. */
  function idleBob(tl, node, start, idle) {
    const amp = idle.amp ?? 8, half = (idle.period ?? 3) / 2;
    const until = idle.until ?? start + 6;
    const reps = Math.max(0, Math.floor((until - start) / half) - 1);
    tl.fromTo(node, { y: -amp / 2, x: -(idle.ampX ?? amp / 2) / 2 },
      { y: amp / 2, x: (idle.ampX ?? amp / 2) / 2, duration: half, ease: "sine.inOut", yoyo: true, repeat: reps }, start);
  }

  /**
   * Drop-and-stack (Dej coins): items fall from the top edge one by one (~0.15 s apart) and stack upward.
   * @param {object} props {blob='coin', color?, count=5, size=230, x=540, y=1150 (bottom item), step=44, interval=0.15}
   * @returns {HTMLElement} wrapper anchor
   */
  RSA.stack = function (container, props, tl, at) {
    const n = props.count || 5, step = props.step || 44, iv = props.interval || 0.15;
    const x = num(props.x, 540), y = num(props.y, 1150), size = props.size || 230;
    const wrap = el("div", "", container, { position: "absolute", inset: "0" });
    const sh = el("div", "rsa-contact", wrap, { left: `${x - size * 0.5}px`, top: `${y + size * 0.12}px`, width: `${size}px`, height: `${size * 0.16}px` });
    tl.fromTo(sh, { opacity: 0 }, { opacity: 1, duration: 0.3 }, at + 0.25);
    for (let i = 0; i < n; i++) {
      RSA.hero(wrap, { blob: props.blob || "coin", color: props.color, emoji: props.emoji, src: props.src, size, x, y: y - i * step, entry: "drop", shadow: false }, tl, at + i * iv);
    }
    return wrap;
  };

  /**
   * Icon row — 3D app icons pop on their spoken word (Dej hook, Dey brand icons), labels type in below.
   * Pop: scale .1→1 + blur 10→0, 0.28 s back.out(1.3), siblings 0.10 s apart unless `t` given per item.
   * @param {object} props
   * @param {Array<{emoji?,src?,blob?,glyph?,label?,t?}>} props.items
   * @param {number} [props.y=1000] centre y · [props.size=200] · [props.gap=400] centre spacing · [props.zigzag=0] px drop of odd items
   * @param {string} [props.between] connector word between items ("или"), centred
   * @param {number} [props.labelGap=45]
   * @returns {HTMLElement} wrapper
   */
  RSA.iconRow = function (container, props, tl, at) {
    const items = props.items || [];
    const n = items.length, size = props.size || 200, gap = props.gap || 400, y = num(props.y, 1000);
    const x0 = num(props.x, 540) - ((n - 1) * gap) / 2;
    const wrap = el("div", "", container, { position: "absolute", inset: "0" });
    items.forEach((it, i) => {
      const x = x0 + i * gap, yy = y + (i % 2 ? props.zigzag || 0 : 0);
      const t = it.t ?? at + i * 0.1;
      const a = anchor(wrap, x, yy);
      const o = object3D(Object.assign({ blob: it.src ? undefined : (it.blob || "tile"), size }, it));
      a.appendChild(o);
      tl.fromTo(o, { opacity: 0, scale: 0.1, rotation: -10, filter: "blur(10px)" },
        { opacity: 1, scale: 1, rotation: 0, filter: "blur(0px)", duration: 0.3, ease: "back.out(1.4)" }, t);
      if (it.label) RSA.label(wrap, { text: it.label, x, y: yy + size / 2 + (props.labelGap ?? 45) + 22 }, tl, t + 0.45);
    });
    if (props.between && n >= 2) {
      const a = anchor(wrap, x0 + gap / 2, y);
      const b = el("div", "rsa-label", a, { fontWeight: "500" });
      b.textContent = props.between;
      blurRise(tl, b, props.betweenAt ?? at + 0.45, { y: 12 });
    }
    return wrap;
  };

  /* ───────────────────────────── cards ───────────────────────────── */

  /**
   * Glass / UI card with slight 3D tilt and lit 1–3 px rim + inner glow.
   * Variants: 'dark' (#121414, r46, rim 1.5px — Dej) · 'glass' (transparent, 2.5px top/bottom-lit rim + 22px inner glow — Der0)
   * · 'frost' (white 8% + backdrop blur, navy scenes — Dej) · 'light' (#F3F5F5, r56, 3.5px blue gradient rim — Dej) · 'white' (DeV).
   * Entry: y 80→0, blur 16→0, rotateX 8°→tilt, 0.4 s power3.out. Sub-line types in after 0.25 s.
   * @param {object} props {variant='dark', x=540, y=1000, width=800, height?, radius?, tilt={rx:2, ry:-4}, icon? (html|emoji),
   *   iconSize=92, title?, titleSize?, sub?, value? (right-aligned figure, blur-rises at valueAt ?? at+0.3), valueColor?,
   *   body? (HTMLElement|html), padding?, from? ('below' default | 'left' | 'right' — side-slide entry with motion blur)}
   * @returns {HTMLElement} card (`.body` = content box)
   */
  RSA.card = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const cmb = el("div", "rsa-mb", a);
    const c = el("div", `rsa-card rsa-card--${props.variant || "dark"}`, cmb, { width: `${props.width || 800}px` });
    if (props.height) Object.assign(c.style, { height: `${props.height}px`, display: "flex", flexDirection: "column", justifyContent: "center" });
    if (props.radius) c.style.borderRadius = `${props.radius}px`;
    if (props.padding != null) c.style.padding = typeof props.padding === "number" ? `${props.padding}px` : props.padding;
    if (props.icon || props.title) {
      const row = el("div", "rsa-card-row", c);
      if (props.icon) {
        const ic = el("div", "rsa-card-icon", row, { width: `${props.iconSize || 92}px`, height: `${props.iconSize || 92}px` });
        if (/^</.test(props.icon)) ic.innerHTML = props.icon;
        else { const s = el("span", "rsa-emoji", ic, { fontSize: `${(props.iconSize || 92) * 0.86}px` }); s.textContent = props.icon; }
      }
      const tx = el("div", "rsa-card-tx", row);
      if (props.title) { const t = el("div", "rsa-card-title", tx); t.textContent = props.title; if (props.titleSize) t.style.fontSize = `${props.titleSize}px`; }
      if (props.sub) { const s = el("div", "rsa-card-sub", tx); typeInto(s, props.sub, tl, at + 0.25, 30); }
      if (props.value != null) {
        const v = el("div", "rsa-card-value", row);
        if (props.valueColor) v.style.color = props.valueColor;
        v.textContent = props.value;
        blurRise(tl, v, props.valueAt ?? at + 0.3, { y: 16, blur: 12 });
      }
    }
    c.body = el("div", "", c);
    if (props.body) { if (typeof props.body === "string") c.body.innerHTML = props.body; else c.body.appendChild(props.body); }
    const tilt = props.tilt || { rx: 2, ry: -4 };
    if (props.from === "left" || props.from === "right") {
      const d = props.from === "left" ? -1 : 1;
      tl.fromTo(c, { opacity: 0, x: 620 * d, rotationX: tilt.rx, rotationY: tilt.ry, transformPerspective: 1400 },
        { opacity: 1, x: 0, rotationX: tilt.rx, rotationY: tilt.ry, transformPerspective: 1400, duration: 0.42, ease: "expo.out" }, at);
      dirBlur(tl, cmb, at, 0.34, "x", 40, 0, "power2.out");
      return c;
    }
    tl.fromTo(c, { opacity: 0, y: 80, filter: "blur(16px)", rotationX: 8, rotationY: tilt.ry, transformPerspective: 1400 },
      { opacity: 1, y: 0, filter: "blur(0px)", rotationX: tilt.rx, rotationY: tilt.ry, transformPerspective: 1400, duration: 0.4, ease: "power3.out" }, at);
    return c;
  };

  /**
   * Glass pill (Dey): 84 px tall, fill darker than bg, 2.5 px gradient rim lit top-left, icon + 44–56 px label.
   * Entry: scale .6→1 + blur 8→0, 0.35 s back.out(1.6).
   * @param {object} props {text, icon? (emoji|html), x, y, size=48}
   */
  RSA.glassPill = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const p = el("div", "rsa-gpill", a);
    if (props.size) p.style.fontSize = `${props.size}px`;
    if (props.icon) {
      const i = el("span", /^</.test(props.icon) ? "" : "rsa-emoji", p, { fontSize: "44px", display: "flex" });
      if (/^</.test(props.icon)) i.innerHTML = props.icon; else i.textContent = props.icon;
    }
    el("span", "", p).textContent = props.text;
    tl.fromTo(p, { opacity: 0, scale: 0.6, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "back.out(1.6)" }, at);
    return p;
  };

  /** Minimal JS-ish tokenizer for the code window (kw pink, identifiers blue, rest grey). */
  function tokenize(line) {
    const out = [];
    const re = /(\s+)|(\b(?:const|let|var|return|import|from|export|function|await|async|new)\b)|(\.[A-Za-z_]\w*)|([A-Za-z_]\w*)|("[^"]*"|'[^']*')|(.)/g;
    let m, afterKw = false;
    while ((m = re.exec(line))) {
      if (m[1]) out.push({ t: m[1], c: "" });
      else if (m[2]) { out.push({ t: m[2], c: "kw" }); afterKw = true; continue; }
      else if (m[3]) out.push({ t: m[3], c: "id" });
      else if (m[4]) out.push({ t: m[4], c: afterKw ? "id" : "mut" });
      else if (m[5]) out.push({ t: m[5], c: "str" });
      else out.push({ t: m[6], c: "mut" });
      if (!m[1]) afterKw = false;
    }
    return out;
  }

  /**
   * Code window card (Dej scene 6): dark tilted card, traffic-light dots, code typed line by line with syntax colours.
   * @param {object} props {lines: string[], x=540, y=1000, width=800, cps=40, lineGap=0.1, size=40 (measured on Dej 22.8 s)}
   * @returns {HTMLElement} card
   */
  RSA.codeWindow = function (container, props, tl, at) {
    const body = el("div", "");
    const dots = el("div", "rsa-dots", body);
    ["#FF5F57", "#FEBC2E", "#28C840"].forEach((c) => { el("i", "", dots, { background: c }); });
    const card = RSA.card(container, Object.assign({ variant: "dark", body, padding: "34px 44px 40px" }, props, { title: null, icon: null }), tl, at);
    const cps = props.cps || 40;
    let t = at + 0.35;
    (props.lines || []).forEach((line) => {
      const ln = el("div", "rsa-mono", body);
      ln.style.fontSize = `${props.size || 40}px`;
      ln.innerHTML = tokenize(line).map((tk) => [...tk.t].map((ch) => `<span class="c ${tk.c ? "tok-" + tk.c : ""}">${ch === " " ? "&nbsp;" : esc(ch)}</span>`).join("")).join("");
      ln.style.whiteSpace = "nowrap";
      const cs = ln.querySelectorAll(".c");
      if (cs.length) tl.fromTo(cs, { opacity: 0, filter: "blur(5px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.1, ease: "none", stagger: 1 / cps }, t);
      t += line.length / cps + (props.lineGap ?? 0.1);
    });
    return card;
  };

  /**
   * Repo card (Dej scene 5): dark tilted card, GitHub mark 92 px + repo name (40 px) typed, then mono lines typed.
   * @param {object} props {name, title?, lines?: string[], x, y, width=800}
   */
  RSA.repoCard = function (container, props, tl, at) {
    const body = el("div", "");
    const row = el("div", "rsa-card-row", body, { gap: "22px" });
    el("div", "", row, { color: "#FBFDFD", display: "flex" }).innerHTML = RSA.icons.github(76);
    const nm = el("div", "", row, { fontSize: "40px", fontWeight: "400", whiteSpace: "nowrap" });
    const card = RSA.card(container, Object.assign({ variant: "dark", body }, props, { title: null, icon: null }), tl, at);
    typeInto(nm, props.name, tl, at + 0.3, 24);
    let t = at + 0.3 + props.name.length / 24 + 0.1;
    if (props.title) {
      const ti = el("div", "", body, { fontSize: "46px", fontWeight: "600", marginTop: "34px" });
      typeInto(ti, props.title, tl, t, 24); t += props.title.length / 24;
    }
    (props.lines || []).forEach((l, i) => {
      const ln = el("div", "rsa-mono", body, { marginTop: i ? "0" : "18px", fontSize: "30px", color: "#C9CBCB" });
      typeInto(ln, l, tl, t, 30); t += l.length / 30 + 0.08;
    });
    return card;
  };

  /* ───────────────────────────── screenshots ───────────────────────────── */

  /**
   * Screenshot frame (DeV/Dey): no device frame, brightness-matched, slight perspective tilt (rotateX ≈5°),
   * soft shadow; red 3 px outline highlight boxes that jump between rows (0.28 s expo.out); optional magnifier
   * lens (170 px, 4 px white ring) showing a zoomed copy of the content.
   * @param {object} props
   * @param {string} [props.src] real screenshot (PNG/JPG). Without it a placeholder iOS list is drawn from `rows`.
   * @param {Array<{icon?:string,src?:string,text:string,value?:string}>} [props.rows] placeholder rows (src = small 3D icon image)
   * @param {'dark'|'light'} [props.theme='dark']
   * @param {number} [props.x=540] [props.y=1000] [props.width=640] [props.height=900] [props.tilt=5] [props.radius=18]
   * @param {Array<{x,y,w,h,t}>} [props.highlights] boxes in screenshot px; first appears, others jump.
   * @param {'white'|'red'} [props.hlColor='red']
   * @param {{x,y,t,size?:number,zoom?:number}} [props.lens]
   * @param {'rise'|'slide'} [props.entry='rise']
   * @returns {HTMLElement} shot
   */
  RSA.screenshot = function (container, props, tl, at) {
    const W = props.width || 640, H = props.height || 900;
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const mb = el("div", "rsa-mb", a);
    const shot = el("div", "rsa-shot", mb, { width: `${W}px`, height: `${H}px`, borderRadius: `${props.radius ?? 18}px` });
    const content = el("div", "", shot, { position: "absolute", inset: "0" });
    if (props.src) content.innerHTML = `<img src="${esc(props.src)}" alt="">`;
    else content.appendChild(placeholderUI(props.rows || [], props.theme || "dark", W, props.title));
    if (props.entry === "slide") {
      const d = props.from === "right" ? 1 : -1;
      tl.fromTo(shot, { x: 500 * d, opacity: 0, rotationX: props.tilt ?? 5, transformPerspective: 1600 },
        { x: 0, opacity: 1, rotationX: props.tilt ?? 5, transformPerspective: 1600, duration: 0.4, ease: "expo.out" }, at);
      dirBlur(tl, mb, at, 0.34, "x", 50, 0);
    } else {
      tl.fromTo(shot, { opacity: 0, y: 120, filter: "blur(16px)", rotationX: (props.tilt ?? 5) + 8, transformPerspective: 1600 },
        { opacity: 1, y: 0, filter: "blur(0px)", rotationX: props.tilt ?? 5, transformPerspective: 1600, duration: 0.42, ease: "expo.out" }, at);
    }
    const hls = props.highlights || [];
    if (hls.length) {
      const box = el("div", "rsa-hl", shot);
      if (props.hlColor === "white") box.style.borderColor = "#fff";
      const h0 = hls[0];
      Object.assign(box.style, { width: `${h0.w}px`, height: `${h0.h}px` });
      tl.fromTo(box, { x: h0.x, y: h0.y, opacity: 0, scale: 1.12 }, { x: h0.x, y: h0.y, opacity: 1, scale: 1, duration: 0.28, ease: "expo.out" }, h0.t ?? at + 0.5);
      for (let i = 1; i < hls.length; i++) {
        const p = hls[i - 1], q = hls[i];
        tl.fromTo(box, { x: p.x, y: p.y, width: p.w, height: p.h },
          { x: q.x, y: q.y, width: q.w, height: q.h, duration: 0.28, ease: "expo.out", immediateRender: false }, q.t);
      }
    }
    if (props.lens) {
      const L = props.lens, size = L.size || 170, z = L.zoom || 1.6;
      const lens = el("div", "rsa-lens", shot, { width: `${size}px`, height: `${size}px`, left: `${L.x - size / 2}px`, top: `${L.y - size / 2}px` });
      lens.setAttribute("data-layout-allow-overlap", ""); // magnified copy intentionally overlaps the page
      lens.setAttribute("data-layout-allow-occlusion", "");
      const clone = content.cloneNode(true);
      Object.assign(clone.style, { inset: "auto", left: `${size / 2 - 4 - L.x * z}px`, top: `${size / 2 - 4 - L.y * z}px`,
        width: `${W}px`, height: `${H}px`, transformOrigin: "0 0", transform: `scale(${z})` });
      clone.querySelectorAll("*").forEach((n) => n.setAttribute("data-layout-allow-overlap", "")); // audit waiver is per text block
      lens.appendChild(clone);
      tl.fromTo(lens, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)" }, L.t ?? at + 0.8);
    }
    return shot;
  };

  function placeholderUI(rows, theme, W, title) {
    const ui = el("div", `rsa-ui rsa-ui--${theme}`);
    const dark = theme === "dark";
    const head = el("div", "", ui, { padding: "64px 40px 22px", fontSize: "44px", fontWeight: "600" });
    head.textContent = title || "Настройки";
    const group = el("div", "", ui, { margin: "0 28px", borderRadius: "22px", background: dark ? "#1C1C1E" : "#fff", overflow: "hidden" });
    rows.forEach((r, i) => {
      const row = el("div", "", group, { display: "flex", alignItems: "center", gap: "22px", height: "88px", padding: "0 24px",
        borderTop: i ? `1px solid ${dark ? "#2C2C2E" : "#E5E5EA"}` : "none", fontSize: "31px" });
      const ic = el("div", "rsa-emoji", row, { width: "52px", height: "52px", borderRadius: "12px", display: "flex", alignItems: "center",
        justifyContent: "center", fontSize: "32px", background: ["#0A84FF", "#30D158", "#FF9F0A", "#FF453A", "#5E5CE6", "#8E8E93"][i % 6] });
      if (r.src) { ic.style.background = "transparent"; ic.innerHTML = `<img src="${esc(r.src)}" alt="" style="width:52px;height:52px;object-fit:contain">`; }
      else ic.textContent = r.icon || "";
      el("div", "", row, { flex: "1" }).textContent = r.text;
      const v = el("div", "", row, { color: dark ? "#8E8E93" : "#8A8A8E" });
      v.textContent = (r.value || "") + "  ›";
    });
    return ui;
  }

  /* ───────────────────────────── devices ───────────────────────────── */

  /**
   * Slot-machine number roll (Der0 §4.3): each digit column scrolls vertically with motion blur, 0.38 s power3.out,
   * 0.03 s column stagger; unit («млн», «%») blurs in +0.05 s. Hero number 104–108 px weight 500.
   * @param {object} props {value: string (e.g. "2031", "100", "0"), unit?, x=540, y=960, size=106, color?, turns=1}
   * @returns {HTMLElement}
   */
  RSA.numberRoll = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 960));
    const n = el("div", "rsa-hero-num", a);
    if (props.size) n.style.fontSize = `${props.size}px`;
    if (props.color) n.style.color = props.color;
    const cols = [];
    [...String(props.value)].forEach((ch) => {
      if (!/\d/.test(ch)) { el("span", "", n).textContent = ch === " " ? "\u202F" : ch; return; } // thousands gap must not collapse
      const col = el("span", "rsa-roll-col", n);
      col.setAttribute("data-layout-allow-overflow", ""); // slot-machine stack is clipped on purpose
      const mb = el("span", "rsa-roll-stack", col);
      const d = +ch, seq = [];
      for (let i = 0; i < 10; i++) seq.push((d - i + 100) % 10); // top = target; rolling down reveals it last
      mb.innerHTML = seq.map((v) => `<span>${v}</span>`).join("");
      cols.push(mb);
    });
    cols.forEach((mb, i) => {
      const t = at + i * 0.03;
      tl.fromTo(mb, { yPercent: -90 }, { yPercent: 0, duration: 0.38, ease: "power3.out" }, t);
      dirBlur(tl, mb, t, 0.38, "y", 10, 0, "power3.out");
    });
    tl.fromTo(n, { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "none" }, at);
    if (props.unit) {
      const u = el("span", "rsa-roll-unit", n);
      u.textContent = props.unit;
      tl.fromTo(u, { opacity: 0, x: -10, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.3, ease: "expo.out" }, at + 0.05 + cols.length * 0.03);
    }
    return n;
  };

  /**
   * Keyword pill wipe (Der0 «ориентир», «минимум»): rounded pill grows L→R as a clip reveal while rotating −8°→0, 0.35 s power3.out.
   * On light: #151515 pill / white text; on dark: light pill / dark text. Use `headline.pills` for inline pills.
   * @param {object} props {text, x, y, size=56}
   */
  RSA.pill = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const p = el("div", "rsa-pill", a, { fontSize: `${props.size || 56}px`, fontWeight: "500" });
    p.textContent = props.text;
    pillWipe(tl, p, at);
    tl.fromTo(p, { opacity: 0 }, { opacity: 1, duration: 0.06 }, at);
    return p;
  };

  /**
   * Text-selection highlight (Der0 «в несколько лет», Dey «совпадать»): text sits in place; a selection fill
   * (#1C3C5C on dark) sweeps L→R in 0.3 s power2.out, the end caret handle (#2A90F6, 3 px bar + 15 px dot) travels with it.
   * @param {object} props {text, x, y, size=62, weight=500, before?, after?, selectAt?} — before/after = unselected text on the same line
   * @returns {HTMLElement}
   */
  RSA.selection = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const line = el("div", "", a, { display: "flex", alignItems: "baseline", gap: ".28em", fontSize: `${props.size || 62}px`, color: "var(--ink)",
      fontWeight: String(props.weight || 500), whiteSpace: "nowrap", letterSpacing: props.size > 90 ? "-0.015em" : "" });
    if (props.before) el("span", "", line).textContent = props.before;
    const s = el("span", "rsa-sel", line, { fontSize: "inherit", fontWeight: "inherit" });
    s.setAttribute("data-layout-allow-occlusion", "");
    const box = el("span", "rsa-sel-box", s);
    el("span", "rsa-sel-tx", s).textContent = props.text;
    const follow = el("span", "rsa-sel-follow", s);
    el("i", "rsa-handle rsa-handle--end", follow);
    const start = el("i", "rsa-handle rsa-handle--start", s);
    if (props.after) el("span", "", line).textContent = props.after;
    tl.fromTo(line, { opacity: 0, y: 20, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.36, ease: "expo.out" }, at);
    const t = props.selectAt ?? at + 0.4;
    tl.fromTo(box, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.3, ease: "power2.out" }, t);
    tl.fromTo(follow, { xPercent: -100, opacity: 0 }, { xPercent: 0, opacity: 1, duration: 0.3, ease: "power2.out" }, t);
    tl.fromTo(start, { opacity: 0 }, { opacity: 1, duration: 0.05 }, t);
    return s;
  };

  /**
   * Blue chip (Der0 «возможно», «✕ ИИ»): #2C7CF4, full radius, white 30 px Medium, 1 px top highlight. Pop 0.32 s back.out(1.7).
   * `variant:'marker'` = Dey highlight: #2478F6 r10 block wipes in L→R behind existing words.
   * @param {object} props {text, icon?, x, y, size=30, variant='chip'|'marker'}
   */
  RSA.chip = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    if (props.variant === "marker") {
      const m = el("span", "rsa-marker", a, { fontSize: `${props.size || 44}px`, fontWeight: "500" });
      const bg = el("span", "rsa-marker-bg", m);
      el("span", "rsa-marker-tx", m).textContent = props.text;
      blurRise(tl, m, at, { y: 14, blur: 10 });
      tl.fromTo(bg, { clipPath: "inset(0% 100% 0% 0% round 10px)" }, { clipPath: "inset(0% 0% 0% 0% round 10px)", duration: 0.3, ease: "power3.out" }, at + 0.2);
      return m;
    }
    const c = el("div", "rsa-chip", a, { fontSize: `${props.size || 30}px` });
    if (props.icon) el("span", "", c).textContent = props.icon;
    el("span", "", c).textContent = props.text;
    tl.fromTo(c, { opacity: 0, scale: 0.6, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.7)" }, at);
    return c;
  };

  /**
   * Dashed connector between two points (cubic S-curve), drawn on via a masked stroke-dashoffset (0.45 s power2.out).
   * Dashed 2 px 10/10 (Der0) or dotted 4 px dots / 12 gap. Colour = theme `--line`.
   * @param {object} props {from:[x,y], to:[x,y], style='dashed'|'dotted', width=2.5, color?, curve='s'|'arc', bend=0}
   * @returns {SVGSVGElement}
   */
  RSA.connector = function (container, props, tl, at) {
    const [x1, y1] = props.from, [x2, y2] = props.to;
    const svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("width", "1080"); svg.setAttribute("height", String(Math.max(y1, y2) + 40));
    Object.assign(svg.style, { position: "absolute", left: "0", top: "0", overflow: "visible" });
    const id = nextId("cn");
    let d;
    if (props.curve === "arc") {
      const mx = (x1 + x2) / 2 + (props.bend || 0), my = (y1 + y2) / 2 - Math.abs(props.bend || 0) * 0.3;
      d = `M${x1} ${y1} Q${mx} ${my} ${x2} ${y2}`;
    } else {
      const my = (y1 + y2) / 2;
      d = `M${x1} ${y1} C${x1} ${my} ${x2} ${my} ${x2} ${y2}`;
    }
    const dotted = props.style === "dotted";
    const w = props.width || (dotted ? 4 : 2.5);
    const color = props.color || "var(--line)";
    svg.innerHTML = `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="1300" height="${Math.max(y1, y2) + 300}">
        <path d="${d}" stroke="#fff" stroke-width="${w + 8}" fill="none" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/></mask></defs>
      <path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round"
        stroke-dasharray="${dotted ? "0.1 12" : "10 10"}" mask="url(#${id})"/>`;
    container.appendChild(svg);
    const m = svg.querySelector("mask path");
    tl.fromTo(m, { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: props.dur || 0.45, ease: "power2.out" }, at);
    return svg;
  };

  /**
   * Flow tree on a tall canvas + camera pan down it (Dey 5.7–11.4 s, Der0 33–38 s). Nodes are any RSA builder
   * ('glassPill' | 'chip' | 'card' | 'label' | 'pill' | 'hero' | 'headline'); edges are dashed connectors between
   * node anchors; pans move the canvas (and optionally the dot grid) with power2.inOut.
   * @param {object} props
   * @param {Array<{id:string, type:string, t:number, h?:number, props:object}>} props.nodes  node props carry x/y in canvas px
   * @param {Array<{from:string|number[], to:string|number[], t:number, style?:string}>} props.edges  ids anchor at node bottom→top (h = node height, default 84)
   * @param {Array<{t:number, y:number, dur?:number}>} [props.pans] camera y (canvas offset) keyframes; dur default 1.0
   * @param {HTMLElement} [props.grid] dot-grid element to scroll with the camera (layer.bg.grid)
   * @param {number} [props.gridOffset=-17] grid background-position offset (dark −17, light −11, maroon −9)
   * @returns {HTMLElement} canvas
   */
  RSA.flow = function (container, props, tl, at) {
    const canvas = el("div", "rsa-flow", container, { height: `${props.height || 4000}px` });
    const byId = {};
    (props.nodes || []).forEach((n) => { byId[n.id] = n; });
    const pt = (ref, end) => {
      if (Array.isArray(ref)) return ref;
      const n = byId[ref];
      const h = n.h ?? 84;
      return [n.props.x ?? 540, n.props.y + (end ? -h / 2 - 14 : h / 2 + 14)];
    };
    (props.edges || []).forEach((e) => RSA.connector(canvas, { from: pt(e.from, false), to: pt(e.to, true), style: e.style, curve: e.curve, bend: e.bend }, tl, e.t ?? at));
    (props.nodes || []).forEach((n) => {
      const fn = RSA[n.type];
      if (!fn) throw new Error(`RSA.flow: unknown node type ${n.type}`);
      n.el = fn(canvas, n.props, tl, n.t ?? at);
    });
    let prev = 0;
    (props.pans || []).forEach((p) => {
      const dur = p.dur || 1.0;
      tl.fromTo(canvas, { y: -prev }, { y: -p.y, duration: dur, ease: "power2.inOut", immediateRender: prev === 0 }, p.t);
      if (props.grid) {
        const off = props.gridOffset ?? -17;
        tl.fromTo(props.grid, { backgroundPosition: `${off}px ${off - prev}px` },
          { backgroundPosition: `${off}px ${off - p.y}px`, duration: dur, ease: "power2.inOut", immediateRender: false }, p.t);
      }
      prev = p.y;
    });
    canvas.nodes = byId;
    return canvas;
  };

  /**
   * Gradient progress bar (Der0 scene 8): ~800×26, full radius, track #E6E8E8 / #1E2121, fill #1C74F4→#3CA4FC→#ACE4FC→#1C74F4
   * with a moving shimmer band; fills L→R over `dur` (≈2 s).
   * @param {object} props {x=540, y=1000, width=800, height=26, dur=2}
   */
  RSA.progressBar = function (container, props, tl, at) {
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const w = props.width || 800, h = props.height || 26, dur = props.dur || 2;
    const bar = el("div", "rsa-bar", a, { width: `${w}px`, height: `${h}px` });
    const fill = el("div", "rsa-bar-fill", bar);
    blurRise(tl, bar, at, { y: 20, blur: 10, dur: 0.35 });
    tl.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power1.inOut" }, at + 0.15);
    tl.fromTo(fill, { backgroundPosition: "0% 0%" }, { backgroundPosition: "-200% 0%", duration: dur + 1, ease: "none" }, at + 0.15);
    return bar;
  };

  /**
   * Deterministic particle globe (Der0 finale): ~2000 dots on a Fibonacci sphere (seeded jitter), depth-shaded
   * #2A6A9A→#3B8BD0, 2 tilted orbit ellipses (#2A4A6A 1.5 px) that precess; rotates ~10°/s. Canvas redrawn from
   * a timeline proxy (seek-safe: the angle is a pure function of timeline time).
   * @param {object} props {x=540, y=1000, size=650, count=2000, speed=10 (deg/s), dur=4, seed=7}
   * @returns {HTMLElement} wrapper
   */
  RSA.globe = function (container, props, tl, at) {
    const size = props.size || 650, n = props.count || 2000, dur = props.dur || 4, speed = props.speed || 10;
    const a = anchor(container, num(props.x, 540), num(props.y, 1000));
    const wrap = el("div", "", a, { width: `${size * 1.5}px`, height: `${size * 1.5}px`, position: "relative" });
    const cv = el("canvas", "", wrap, { position: "absolute", left: `${size * 0.25}px`, top: `${size * 0.25}px`, width: `${size}px`, height: `${size}px` });
    const DPR = 2;
    cv.width = size * DPR; cv.height = size * DPR;
    const ctx = cv.getContext("2d");
    const r = RS.rand(props.seed || 7);
    const pts = [];
    const ga = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < n; i++) {
      const y = 1 - (i / (n - 1)) * 2, rad = Math.sqrt(1 - y * y), th = ga * i + (r() - 0.5) * 0.04;
      pts.push([Math.cos(th) * rad, y, Math.sin(th) * rad, 0.7 + r() * 0.6]);
    }
    const tilt = 0.35, ct = Math.cos(tilt), st = Math.sin(tilt);
    const R = size * DPR * 0.46, C = size * DPR / 2;
    function draw(deg) {
      const ang = (deg * Math.PI) / 180, ca = Math.cos(ang), sa = Math.sin(ang);
      ctx.clearRect(0, 0, cv.width, cv.height);
      for (let i = 0; i < n; i++) {
        const p = pts[i];
        const x = p[0] * ca + p[2] * sa, z0 = -p[0] * sa + p[2] * ca;
        const y = p[1] * ct - z0 * st, z = p[1] * st + z0 * ct;
        const k = (z + 1) / 2; // 0 back … 1 front
        ctx.fillStyle = `rgba(${Math.round(42 + 30 * k)},${Math.round(106 + 54 * k)},${Math.round(154 + 86 * k)},${(0.4 + 0.6 * k).toFixed(3)})`;
        const s = (3.0 + 2.6 * k) * p[3];
        ctx.fillRect(C + x * R - s / 2, C + y * R - s / 2, s, s);
      }
    }
    draw(0);
    const proxy = { a: 0 };
    tl.fromTo(proxy, { a: 0 }, { a: speed * dur, duration: dur, ease: "none", onUpdate: () => draw(proxy.a) }, at);
    const svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", `0 0 ${size * 1.5} ${size * 1.5}`);
    Object.assign(svg.style, { position: "absolute", inset: "0", width: "100%", height: "100%", overflow: "visible" });
    const c0 = size * 0.75;
    svg.innerHTML = [[-12, "#2A4A6A"], [-62, "#4A5254"]].map(([d, c]) => `<g transform="rotate(${d} ${c0} ${c0})"><ellipse class="orb" cx="${c0}" cy="${c0}" rx="${size * 0.68}" ry="${size * 0.19}" fill="none" stroke="${c}" stroke-width="1.6"/></g>`).join("");
    wrap.appendChild(svg);
    svg.querySelectorAll("ellipse").forEach((e, i) => {
      tl.fromTo(e, { rotation: 0, svgOrigin: `${c0} ${c0}` }, { rotation: i ? -6 : 6, svgOrigin: `${c0} ${c0}`, duration: dur, ease: "none" }, at);
    });
    tl.fromTo(wrap, { opacity: 0, scale: 0.9, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, at);
    return wrap;
  };

  /**
   * Hook display (Der0 0–2 s): tiny tracked label, giant ultra-wide display word (Unbounded 900, per-letter
   * blur 20→0 from opacity .2, 70 ms stagger, +30 px rise, 0.47 s — already mid-reveal on frame 0), a wide
   * sub-word, and a lime #BAE436 italic accent rotated −5° with two hand-drawn underlines.
   * @param {object} props {label?, word, sub?, accent?, wordSize=540, subSize=128, y=715 (word centre), squeeze=0.8 (scaleX)}
   * @returns {HTMLElement} word node
   */
  RSA.hookDisplay = function (container, props, tl, at) {
    const y = num(props.y, 715), ws = props.wordSize || 540;
    if (props.label) {
      const l = el("div", "rsa-hook-label", anchor(container, 540, 307));
      l.textContent = props.label;
      tl.fromTo(l, { opacity: 0.2, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "power2.out" }, at);
    }
    // Unbounded is wider than the ref's Benzin-like face: keep cap height (≈392 px) and squeeze to ≈786 px wide
    const w = el("div", "rsa-hook-word", anchor(container, 540, y), { fontSize: `${ws}px`, transform: `scaleX(${props.squeeze ?? 0.8})` });
    w.innerHTML = [...props.word].map((c) => `<span>${esc(c)}</span>`).join("");
    tl.fromTo(w.children, { opacity: 0.2, y: 30, filter: "blur(20px)" },
      { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.47, ease: "power2.out", stagger: 0.07 }, at);
    let yy = y + ws * 0.36 + 150;
    if (props.sub) {
      const s = el("div", "rsa-hook-sub", anchor(container, 540, yy), { fontSize: `${props.subSize || 128}px` });
      s.textContent = props.sub;
      blurRise(tl, s, at + 0.3, { y: 26, blur: 16, dur: 0.42 });
      yy += (props.subSize || 128) * 0.5 + 95;
    }
    if (props.accent) {
      const ac = el("div", "rsa-hook-accent", anchor(container, 540, yy));
      ac.textContent = props.accent;
      tl.fromTo(ac, { opacity: 0, y: 20, rotation: -5, filter: "blur(14px)" },
        { opacity: 1, y: 0, rotation: -5, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, at + 0.65);
      [[20, 0.08, 0.86], [40, 0.2, 0.62]].forEach(([dy, l, wd], i) => {
        const u = el("i", "rsa-hook-ul", ac, { top: `calc(100% + ${dy - 12}px)`, left: `${l * 100}%`, width: `${wd * 100}%` });
        tl.fromTo(u, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, at + 0.85 + i * 0.1);
      });
    }
    return w;
  };

  /* ───────────────────────────── list row ───────────────────────────── */

  /**
   * List row (layout `list`): 3D icon · title + grey sub · right-aligned value, hairline under the row, no card box.
   * Entry (build-down): row slides x +70→0 with blur 12→0 (0.36 s expo.out), icon pops back.out(1.6), hairline draws L→R,
   * value blur-rises +0.2 s.
   * @param {object} props {y (row centre), height=150, icon? (image src), emoji? (fallback), iconSize=112, title, sub?, value?,
   *   valueColor?, rule=true}
   * @returns {HTMLElement} row
   */
  RSA.listRow = function (container, props, tl, at) {
    const h = props.height || 150, is = props.iconSize || 112;
    const row = el("div", "rsa-row", container, { top: `${props.y - h / 2}px`, height: `${h}px` });
    let ic = null;
    if (props.icon || props.emoji) {
      ic = el("div", "rsa-row-icon", row, { width: `${is}px`, height: `${is}px` });
      if (props.icon) ic.innerHTML = `<img src="${esc(props.icon)}" alt="">`;
      else { const e = el("span", "rsa-emoji", ic, { fontSize: `${is * 0.86}px` }); e.textContent = props.emoji; }
    }
    const tx = el("div", "rsa-row-tx", row);
    el("div", "rsa-row-title", tx).textContent = props.title || "";
    if (props.sub) el("div", "rsa-row-sub", tx).textContent = props.sub;
    let v = null;
    if (props.value != null) {
      v = el("div", "rsa-row-value", row);
      if (props.valueColor) v.style.color = props.valueColor;
      v.textContent = props.value;
    }
    tl.fromTo(tx, { opacity: 0, x: 70, filter: "blur(12px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.36, ease: "expo.out" }, at + 0.04);
    if (ic) tl.fromTo(ic, { opacity: 0, scale: 0.2, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.6)" }, at);
    if (v) blurRise(tl, v, at + 0.2, { y: 14, blur: 12, dur: 0.34 });
    if (props.rule !== false) {
      const r = el("div", "rsa-row-rule", row, { top: `${h - 1}px` });
      tl.fromTo(r, { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "power2.out" }, at + 0.1);
    }
    return row;
  };

  /* ───────────────────────────── layouts (references/layouts.md) ───────────────────────────── */

  /*
   * Every scene picks ONE layout. A layout computes the vertical stack of its parts (kicker · headline · visual ·
   * caption …) from their known heights + the shared rhythm, then centres the whole block in the live area
   * (y 230–1575): block centre ≈ y 905 (rule: 860–940), block ≥ 600 px tall (except `statement`). It builds the
   * text parts itself, builds the visual from `props.visual` (spec or callback) and returns the geometry so
   * callers can add more components into the slots. Measured against the refs (Dej 3.0/7.0/26.0, DeV 25/53,
   * Der0 20.5, Dey 22.5): headline block centre 500–560, hero centre 820–1100, caption 1330–1500.
   */
  const LIVE = { top: 230, bottom: 1575, left: 90, right: 990, cy: 905 };
  const RHYTHM = { kickerHead: 34, headVisual: 90, visualCap: 72, headCap: 40, visualHead: 90, row: 0 };
  const TYPE = { h1: 78, h1Long: 64, lh: 1.06, cap: 42, capLh: 1.18, kicker: 56 };
  RSA.LIVE = LIVE; RSA.RHYTHM = RHYTHM; RSA.TYPE = TYPE;

  const linesOf = (t) => (t == null ? [] : toLines(t));
  const h1Size = (lines, size) => size || (Math.max(0, ...lines.map((l) => l.length)) > 16 ? TYPE.h1Long : TYPE.h1);
  const capLines = (t) => (t == null ? [] : Array.isArray(t) ? t : [t]);

  /**
   * Stack items top→bottom, centred on `cy`, clamped inside the live area.
   * items: [{key, h, gap? (gap ABOVE this item)}] → { [key]: {top, cy, h}, block: {top, bottom, cy, h} }
   */
  function stackItems(items, cy, minH) {
    let H = 0;
    items.forEach((it, i) => { H += (i ? it.gap || 0 : 0) + it.h; });
    // grow the flexible item so the block fills ≥ minH (layouts.md §1)
    const grow = items.find((it) => it.grow);
    if (grow && minH && H < minH) { const add = Math.min(minH - H, (grow.max || Infinity) - grow.h); if (add > 0) { grow.h += add; H += add; } }
    let top = cy - H / 2;
    top = Math.max(LIVE.top + 20, Math.min(top, LIVE.bottom - 20 - H));
    const out = { block: { top, bottom: top + H, cy: top + H / 2, h: H } };
    let y = top;
    items.forEach((it, i) => { y += i ? it.gap || 0 : 0; out[it.key] = { top: y, cy: y + it.h / 2, h: it.h }; y += it.h; });
    return out;
  }

  /** Build the visual for a slot: callback `(container, slot, tl, at) → el` or `{type, props, t}` naming any RSA builder. */
  function buildVisual(container, spec, slot, tl, at) {
    if (!spec) return null;
    if (typeof spec === "function") return spec(container, slot, tl, at);
    const fn = RSA[spec.type];
    if (!fn) throw new Error(`RSA.layout: unknown visual type ${spec.type}`);
    const auto = { x: slot.x, y: slot.y };
    if (spec.type === "hero" || spec.type === "globe") auto.size = slot.h;
    if (spec.type === "screenshot") { auto.height = slot.h; auto.width = slot.w; }
    if (spec.type === "card" || spec.type === "codeWindow" || spec.type === "repoCard") auto.width = slot.w;
    if (spec.type === "iconRow") auto.y = slot.y;
    return fn(container, Object.assign(auto, spec.props), tl, spec.t ?? at);
  }

  function headlineAt(container, p, y, tl, at) {
    return RSA.headline(container, { text: p.text, words: p.words, stagger: p.stagger, pills: p.pills, size: p.size, weight: p.weight,
      halo: p.halo, color: p.color, y }, tl, p.textAt ?? at);
  }
  function captionAt(container, p, y, tl, at) {
    return RSA.caption(container, { text: p.caption, y, color: p.captionColor, cps: p.cps }, tl, p.captionAt ?? at + 0.9);
  }
  /** Marks the block on the container for QA (data-rsa-block="top,bottom"). */
  function mark(container, id, g) {
    container.dataset.rsaLayout = id;
    container.dataset.rsaBlock = `${Math.round(g.block.top)},${Math.round(g.block.bottom)}`;
  }

  RSA.layout = {};

  /**
   * `hero` — headline top · one big 3D object centre · grey caption under it (Style A default).
   * Hero box default 620 px (Fluent/generated PNGs carry ≈ 6 % padding → visible object ≈ 545 px ≈ 50 % of frame width); headline lands ≈ y 500–540, caption ≈ 1350.
   * @param {HTMLElement} container  layer.inner
   * @param {object} props
   * @param {string} props.text  headline ("a / b"); [props.words], [props.pills], [props.size], [props.halo], [props.textAt]
   * @param {object|Function} props.visual  e.g. {type:'hero', props:{src, entry:'pop'}, t} — gets x/y/size from the slot
   * @param {number} [props.visualH=620]  visual height (hero size)
   * @param {string|string[]} [props.caption]  [props.captionAt=at+0.9], [props.captionColor]
   * @param {string} [props.kicker]  blue chip above the headline
   * @param {object} tl  @param {number} at  scene start (local s)
   * @returns {{block, slots:{visual:{x,y,w,h}}, headline, caption, visual, kicker}}
   */
  RSA.layout.hero = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = h1Size(hl, props.size), cl = capLines(props.caption);
    const items = [];
    if (props.kicker) items.push({ key: "kicker", h: TYPE.kicker });
    items.push({ key: "head", h: hl.length * size * TYPE.lh, gap: RHYTHM.kickerHead });
    items.push({ key: "vis", h: props.visualH || 620, gap: RHYTHM.headVisual, grow: true, max: 700 });
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: RHYTHM.visualCap });
    const g = stackItems(items, props.cy || LIVE.cy, 600);
    mark(container, props._id || "hero", g);
    const slot = { x: 540, y: g.vis.cy, w: Math.min(900, props.visualW || g.vis.h), h: g.vis.h };
    const r = { block: g.block, slots: { visual: slot } };
    if (props.kicker) r.kicker = RSA.chip(container, { text: props.kicker, y: g.kicker.cy, size: 34 }, tl, props.kickerAt ?? at);
    r.headline = headlineAt(container, Object.assign({}, props, { size }), g.head.cy, tl, at + (props.kicker ? 0.15 : 0));
    r.visual = buildVisual(container, props.visual, slot, tl, at + 0.15);
    if (cl.length) r.caption = captionAt(container, props, g.cap.cy, tl, at);
    return r;
  };

  /**
   * `visual-top` — big visual first (≤ 55 % of the live area), headline BELOW it (y ≈ 1250–1450), caption last.
   * Use for tall objects / drop entries; the asymmetric mass breaks the headline-on-top habit.
   * @param {object} props {text, visual, visualH=680, caption?, size?, words?, cy=1000}
   * @returns {{block, slots:{visual}, headline, caption, visual}}
   */
  RSA.layout["visual-top"] = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = h1Size(hl, props.size), cl = capLines(props.caption);
    const items = [{ key: "vis", h: props.visualH || 680, grow: true, max: 760 },
      { key: "head", h: hl.length * size * TYPE.lh, gap: RHYTHM.visualHead }];
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: RHYTHM.headCap });
    const g = stackItems(items, props.cy || 1000, 600);
    mark(container, "visual-top", g);
    const slot = { x: 540, y: g.vis.cy, w: Math.min(900, props.visualW || g.vis.h), h: g.vis.h };
    const r = { block: g.block, slots: { visual: slot } };
    r.visual = buildVisual(container, props.visual, slot, tl, at);
    r.headline = headlineAt(container, Object.assign({}, props, { size }), g.head.cy, tl, at + 0.3);
    if (cl.length) r.caption = captionAt(container, props, g.cap.cy, tl, at + 0.2);
    return r;
  };

  /**
   * `number` — giant slot-machine number centre (glyphs ≈ 0.71 × size tall; font size auto-fits 900 px width, ≤ 420),
   * grey label above (typed), keyword pill and/or caption below.
   * @param {object} props {value: string, unit?, label?, pill?, pillAt?, caption?, size?, color?, labelAt?, rollAt?}
   * @returns {{block, number, label, pill, caption}}
   */
  RSA.layout.number = function (container, props, tl, at) {
    const v = String(props.value);
    const digits = (v.match(/\d/g) || []).length, other = v.length - digits;
    const size = props.size || Math.min(420, Math.floor(900 / (digits * 0.58 + other * 0.3 + (props.unit ? props.unit.length * 0.5 + 0.22 : 0))));
    const cl = capLines(props.caption);
    const items = [];
    if (props.label) items.push({ key: "label", h: 52 });
    items.push({ key: "num", h: size * 0.86, gap: 44 });
    if (props.pill) items.push({ key: "pill", h: 72, gap: 56 });
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: props.pill ? 48 : RHYTHM.visualCap });
    const g = stackItems(items, props.cy || LIVE.cy, 600);
    mark(container, "number", g);
    const r = { block: g.block, slots: {} };
    let t = at;
    if (props.label) { r.label = RSA.label(container, { text: props.label, x: 540, y: g.label.cy, color: "var(--cap)" }, tl, props.labelAt ?? t); t += 0.35; }
    r.number = RSA.numberRoll(container, { value: v, unit: props.unit, x: 540, y: g.num.cy, size, color: props.color }, tl, props.rollAt ?? t);
    if (props.pill) r.pill = RSA.pill(container, { text: props.pill, y: g.pill.cy, size: 54 }, tl, props.pillAt ?? t + 0.6);
    if (cl.length) r.caption = captionAt(container, Object.assign({ captionAt: t + 1.0 }, props), g.cap.cy, tl, at);
    return r;
  };

  /**
   * `media` — real screenshot / photo / footage frame at 60–75 % of the live height with a short headline above
   * and an optional caption under. The visual defaults to `{type:'screenshot'}` sized from the slot.
   * @param {object} props {text, visual, visualH=860, visualW=640, caption?}
   * @returns {{block, slots:{visual}, headline, caption, visual}}
   */
  RSA.layout.media = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = h1Size(hl, props.size), cl = capLines(props.caption);
    const items = [];
    if (hl.length) items.push({ key: "head", h: hl.length * size * TYPE.lh });
    items.push({ key: "vis", h: props.visualH || 860, gap: RHYTHM.headVisual });
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: RHYTHM.visualCap });
    const g = stackItems(items, props.cy || LIVE.cy, 600);
    mark(container, "media", g);
    const slot = { x: 540, y: g.vis.cy, w: props.visualW || 640, h: g.vis.h };
    const r = { block: g.block, slots: { visual: slot } };
    if (hl.length) r.headline = headlineAt(container, Object.assign({}, props, { size }), g.head.cy, tl, at);
    r.visual = buildVisual(container, props.visual || { type: "screenshot" }, slot, tl, at + 0.2);
    if (cl.length) r.caption = captionAt(container, props, g.cap.cy, tl, at);
    return r;
  };

  /**
   * `list` — headline + 3–4 rows building downward in a centred 900 px column (RSA.listRow).
   * @param {object} props {text, items: [{icon|emoji, title, sub?, value?, t?}], rowH=150, interval=0.45, caption?}
   * @returns {{block, rows: HTMLElement[], headline, caption}}
   */
  RSA.layout.list = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = h1Size(hl, props.size), cl = capLines(props.caption);
    const its = props.items || [], rh = props.rowH || 150;
    const items = [];
    if (hl.length) items.push({ key: "head", h: hl.length * size * TYPE.lh });
    items.push({ key: "rows", h: its.length * rh, gap: RHYTHM.headVisual - 20 });
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: RHYTHM.visualCap });
    const g = stackItems(items, props.cy || LIVE.cy, 600);
    mark(container, "list", g);
    const r = { block: g.block, slots: {}, rows: [] };
    if (hl.length) r.headline = headlineAt(container, Object.assign({}, props, { size }), g.head.cy, tl, at);
    const t0 = at + 0.45, iv = props.interval ?? 0.45;
    its.forEach((it, i) => {
      r.rows.push(RSA.listRow(container, Object.assign({ height: rh, y: g.rows.top + rh * (i + 0.5), rule: i < its.length - 1 }, it), tl, it.t ?? t0 + i * iv));
    });
    if (cl.length) r.caption = captionAt(container, Object.assign({ captionAt: t0 + its.length * iv + 0.2 }, props), g.cap.cy, tl, at);
    return r;
  };

  /**
   * `compare` — two stacked states (before → after): two cards with a cut line + object between them.
   * The "before" card dims to 50 % when "after" lands. Cards slide in from opposite sides.
   * @param {object} props {text, before:{title, sub?, value?, icon?}, after:{…}, divider? (visual spec, e.g. scissors hero,
   *   default size 190; false = no cut line), cardH=210, beforeAt?, afterAt?, caption?, variants?: [before, after] card variants}
   * @returns {{block, before, after, divider, headline, caption}}
   */
  RSA.layout.compare = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = h1Size(hl, props.size), cl = capLines(props.caption);
    const ch = props.cardH || 210, dh = props.dividerH || 190;
    const items = [];
    if (hl.length) items.push({ key: "head", h: hl.length * size * TYPE.lh });
    items.push({ key: "a", h: ch, gap: RHYTHM.headVisual }, { key: "mid", h: dh, gap: 34 }, { key: "b", h: ch, gap: 34 });
    if (cl.length) items.push({ key: "cap", h: cl.length * TYPE.cap * TYPE.capLh, gap: RHYTHM.visualCap });
    const g = stackItems(items, props.cy || LIVE.cy, 600);
    mark(container, "compare", g);
    const light = /light/.test(container.closest(".rsa-layer")?.className || "");
    const [va, vb] = props.variants || (light ? ["white", "light"] : ["dark", "glass"]);
    const r = { block: g.block, slots: { divider: { x: 540, y: g.mid.cy, w: 900, h: dh } } };
    if (hl.length) r.headline = headlineAt(container, Object.assign({}, props, { size }), g.head.cy, tl, at);
    const card = (p, y, variant, t, from) => RSA.card(container, Object.assign({ variant, x: 540, y, width: 900, height: ch, radius: 44,
      padding: "0 48px", iconSize: 120, from }, p, { icon: p.icon && !/^</.test(p.icon) && /\.(png|webp|jpg|svg)$/i.test(p.icon) ? `<img src="${esc(p.icon)}" alt="" style="width:120px;height:120px;object-fit:contain">` : p.icon }), tl, t);
    const ta = props.beforeAt ?? at + 0.35, tb = props.afterAt ?? ta + 1.1;
    r.before = card(props.before || {}, g.a.cy, va, ta, "left");
    if (props.divider !== false) {
      RSA.connector(container, { from: [110, g.mid.cy], to: [970, g.mid.cy], color: props.lineColor }, tl, ta + 0.5);
      r.divider = buildVisual(container, props.divider, { x: 540, y: g.mid.cy, w: dh, h: dh }, tl, ta + 0.6);
    }
    r.after = card(props.after || {}, g.b.cy, vb, tb, "right");
    RS.dim(tl, r.before, tb + 0.15, 0.5, 0.3);
    if (cl.length) r.caption = captionAt(container, Object.assign({ captionAt: tb + 0.5 }, props), g.cap.cy, tl, at);
    return r;
  };

  /**
   * `statement` — breath scene: 2-line big headline only (default 116 px), centred at y 905. Optional
   * `select` = the second line is shown as an iOS text selection (fill sweeps, blue handles) instead of plain words.
   * Max one per ~6 scenes.
   * @param {object} props {text: "line1 / line2", size=116, select?: boolean, selectAt?, words?}
   * @returns {{block, headline, selection}}
   */
  RSA.layout.statement = function (container, props, tl, at) {
    const hl = linesOf(props.text), size = props.size || (Math.max(...hl.map((l) => l.length)) > 13 ? 96 : 116);
    const lineH = size * TYPE.lh;
    const g = stackItems([{ key: "head", h: hl.length * lineH }], props.cy || LIVE.cy, 0);
    mark(container, "statement", g);
    const r = { block: g.block, slots: {} };
    if (props.select && hl.length > 1) {
      r.headline = RSA.headline(container, { text: hl.slice(0, -1), words: props.words, size, y: g.head.top + (hl.length - 1) * lineH / 2 }, tl, at);
      r.selection = RSA.selection(container, { text: hl[hl.length - 1], x: 540, y: g.head.bottom - lineH / 2 + size * 0.04, size, weight: 600,
        selectAt: props.selectAt }, tl, at + 0.12 * hl[0].split(/\s+/).length + 0.1);
    } else {
      r.headline = RSA.headline(container, { text: hl, words: props.words, size, pills: props.pills, y: g.head.cy }, tl, at);
    }
    return r;
  };

  /**
   * `stack` — kicker chip + headline + ONE component, whole block centred (default component height 600).
   * @param {object} props {kicker?, text, visual, visualH=600, caption?}
   * @returns {{block, slots:{visual}, kicker, headline, visual, caption}}
   */
  RSA.layout.stack = function (container, props, tl, at) {
    return RSA.layout.hero(container, Object.assign({ visualH: 600 }, props, { _id: "stack" }), tl, at);
  };

  /**
   * `head-side` — transparent overlay for talking-head scenes (use `RSA.layer({theme:'none'})` over the footage).
   * One component sits in the chest band (y 880–1460) beside or below the face; an optional keyword line with a dark
   * halo sits at the top of the band (over the component's column for left/right). Never covers the face (band starts at y 880).
   * @param {object} props {side='below'|'left'|'right', text?, visual, visualH=420, size=64}
   * @returns {{block, slots:{visual}, headline, visual}}
   */
  RSA.layout["head-side"] = function (container, props, tl, at) {
    const band = { top: 880, bottom: 1460 };
    const side = props.side || "below";
    const hl = linesOf(props.text), size = props.size || 64;
    const headH = hl.length ? hl.length * size * TYPE.lh + 40 : 0;
    const vh = Math.min(props.visualH || 420, band.bottom - band.top - headH);
    const x = side === "left" ? 300 : side === "right" ? 780 : 540;
    const r = { block: { top: band.top, bottom: band.bottom, cy: (band.top + band.bottom) / 2, h: band.bottom - band.top }, slots: {} };
    container.dataset.rsaLayout = "head-side";
    if (hl.length) {
      r.headline = RSA.headline(container, { text: hl, words: props.words, size, halo: true, y: band.top + headH / 2 - 20 }, tl, at);
      // side variants: the keyword sits over its own column (keep ≤ 12 chars per line there)
      if (side === "left") Object.assign(r.headline.style, { left: "90px", right: "560px" });
      if (side === "right") Object.assign(r.headline.style, { left: "560px", right: "90px" });
    }
    const slot = { x, y: band.top + headH + vh / 2, w: side === "below" ? 820 : 420, h: vh };
    r.slots.visual = slot;
    r.visual = buildVisual(container, props.visual, slot, tl, at + 0.15);
    return r;
  };

  /**
   * Bookmark CTA ending (Dej 52.9 s, DeV 103.5 s): glossy 3D blue bookmark rises from below with motion blur,
   * "сохрани…" blur-rises +0.2 s, title types +0.5 s, caption types +1.0 s; held to the end (no end card).
   * Geometry comes from the layout engine (block centred at y≈905, bookmark = hero size).
   * @param {object} props {headline='сохрани', title?, caption?, layout='top'|'bottom', src? (bookmark PNG), size=470}
   * @returns {HTMLElement} bookmark node (`.layout` = {block, …} geometry)
   */
  RSA.bookmarkCTA = function (container, props, tl, at) {
    const bottom = props.layout === "bottom";
    const size = props.size || 470;
    const head = { key: "head", h: TYPE.h1 * TYPE.lh, gap: RHYTHM.visualHead };
    const vis = { key: "vis", h: size, gap: RHYTHM.headVisual };
    const items = bottom ? [vis, head] : [Object.assign({}, head, { gap: 0 }), vis];
    if (props.title) items.push({ key: "title", h: 56, gap: 64 });
    if (props.caption) items.push({ key: "cap", h: TYPE.cap * TYPE.capLh, gap: props.title ? 26 : RHYTHM.visualCap });
    const g = stackItems(items, LIVE.cy, 600);
    mark(container, "cta", g);
    const bm = RSA.hero(container, { src: props.src, blob: props.src ? undefined : "bookmark", size, x: 540, y: g.vis.cy, entry: "rise", shadow: !!props.src }, tl, at);
    RSA.headline(container, { text: props.headline || "сохрани", y: g.head.cy }, tl, at + 0.2);
    let t = at + 0.5;
    if (props.title) {
      RSA.label(container, { text: props.title, x: 540, y: g.title.cy, cls: "rsa-cta-title" }, tl, t);
      t += props.title.length / 24 + 0.1;
    }
    if (props.caption) RSA.caption(container, { text: props.caption, y: g.cap.cy }, tl, Math.max(t, at + 1.0));
    bm.layout = g;
    return bm;
  };

  /* ───────────────────────────── transitions ───────────────────────────── */

  const DIRS = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

  /**
   * Exit half of a transition — animates `from.content` (and `from.inner` for SVG motion blur). Never touches the clip.
   * @param {object} tl  @param {HTMLElement} from  layer from RSA.layer  @param {number} tc  transition centre (sentence onset)
   * @param {{type:'blur-drift'|'zoom'|'whip'|'lum'|'cut', dir?:string}} o
   */
  RSA.transitionOut = function (tl, from, tc, o) {
    o = o || {};
    const type = o.type || "blur-drift";
    const [dx, dy] = DIRS[o.dir || (type === "whip" ? "up" : "down")] || DIRS.down;
    if (type === "blur-drift") {
      // Dej §6: drift 260 px (ease-in), blur 0→24 px, fade, 0.28 s starting 0.18 s before the onset
      tl.fromTo(from.content, { x: 0, y: 0, opacity: 1, filter: "blur(0px)" },
        { x: dx * 260, y: dy * 260, opacity: 0, filter: "blur(24px)", duration: 0.28, ease: "power2.in", immediateRender: false }, tc - 0.18);
    } else if (type === "zoom") {
      tl.fromTo(from.content, { scale: 1, opacity: 1, filter: "blur(0px)" },
        { scale: 1.3, opacity: 0, filter: "blur(28px)", duration: 0.34, ease: "power2.in", immediateRender: false }, tc - 0.22);
    } else if (type === "whip") {
      // Der0 §6: content accelerates ~300 px in 150 ms (ease-in) with directional motion blur
      tl.fromTo(from.content, { x: 0, y: 0, opacity: 1 },
        { x: dx * 320, y: dy * 320, opacity: 0, duration: 0.15, ease: "power2.in", immediateRender: false }, tc - 0.15);
      dirBlur(tl, from.inner, tc - 0.15, 0.15, dx ? "x" : "y", 0, 26, "power2.in", [-8, 116]);
    } else if (type === "lum") {
      // Der0 §6: old content blurs 0→12, fades and drifts 40–80 px during the 250 ms luminance tween
      tl.fromTo(from.content, { y: 0, opacity: 1, filter: "blur(0px)" },
        { y: dy * 60 || -60, opacity: 0, filter: "blur(12px)", duration: 0.25, ease: "power1.in", immediateRender: false }, tc - 0.125);
    }
  };

  /**
   * Entry half of a transition — fades `to.bg` over the previous layer and brings `to.content` in.
   * The `to` clip must start at or before tc − 0.25 (see RSA.transitionWindow).
   * @param {{type, dir?, bg?: 'fade'|'cut', shared?: {el: HTMLElement, from: {x:number,y:number,scale?:number}, twin?: HTMLElement}}} o
   *   shared: element living in `to.over` at its final spot; it FLIPs from the given offset (0.5 s expo.inOut);
   *   `twin` (the copy in the old layer) is hidden as the hand-off starts.
   */
  RSA.transitionIn = function (tl, to, tc, o) {
    o = o || {};
    const type = o.type || "blur-drift";
    const [dx, dy] = DIRS[o.dir || (type === "whip" ? "up" : "down")] || DIRS.down;
    const bgFade = (start, dur) => {
      // same-theme whip: new plate appears only after the old content has left (invisible swap)
      if (o.bg === "cut") tl.fromTo(to.bg, { opacity: 0 }, { opacity: 1, duration: 0.01, ease: "none" }, tc);
      else tl.fromTo(to.bg, { opacity: 0 }, { opacity: 1, duration: dur, ease: "none" }, start);
    };
    if (type === "cut") return;
    if (type === "blur-drift" || type === "zoom") {
      bgFade(tc - 0.18, 0.28);
      const din = type === "zoom" ? [0, 0] : [-dx * 160, -dy * 160];
      tl.fromTo(to.content, { x: din[0], y: din[1], scale: type === "zoom" ? 0.92 : 1, opacity: 0, filter: "blur(20px)" },
        { x: 0, y: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }, tc - 0.05);
    } else if (type === "whip") {
      bgFade(tc - 0.15, 0.25);
      // arrives from ~270 px on the opposite side, 400 ms expo settle with decaying directional blur
      tl.fromTo(to.content, { x: -dx * 270, y: -dy * 270, opacity: 0 },
        { x: 0, y: 0, opacity: 1, duration: 0.4, ease: "expo.out" }, tc);
      dirBlur(tl, to.inner, tc, 0.3, dx ? "x" : "y", 18, 0, "power2.out", [-8, 116]);
    } else if (type === "lum") {
      bgFade(tc - 0.125, 0.25);
      tl.fromTo(to.content, { y: 250, opacity: 0, filter: "blur(14px)" },
        { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, tc + 0.1);
    }
    if (o.shared) {
      const s = o.shared, f = s.from || {};
      tl.fromTo(s.el, { x: f.x || 0, y: f.y || 0, scale: f.scale ?? 1 },
        { x: 0, y: 0, scale: 1, duration: 0.5, ease: "expo.inOut" }, tc - 0.25);
      if (s.twin) tl.fromTo(s.twin, { opacity: 1 }, { opacity: 0, duration: 0.01, immediateRender: false }, tc - 0.25);
    }
  };

  /**
   * Full transition between two layers.
   * Types: 'blur-drift' (0.28 s, Dej) · 'zoom' (zoom-through variant) · 'whip' (150 ms out + 400 ms expo from 270 px, Der0/Dey;
   * dir up|down|left|right) · 'lum' (250 ms luminance crossfade, optional shared element) · 'cut' (hook only).
   */
  RSA.transition = function (tl, from, to, tc, o) {
    o = Object.assign({}, o);
    if (o.type === "whip" && !o.bg) o.bg = from.theme === to.theme ? "cut" : "fade";
    RSA.transitionOut(tl, from, tc, o);
    RSA.transitionIn(tl, to, tc, o);
  };

  /** Clip windows a transition needs: the old layer must live until `end`, the new one start by `start`. */
  RSA.transitionWindow = function (tc, type) {
    if (type === "cut") return { start: tc, end: tc };
    return { start: tc - 0.25, end: tc + 0.15 };
  };

  window.RSA = RSA;
})();
