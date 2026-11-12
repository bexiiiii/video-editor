/* reels-studio · Style C "Keynote 3D" component library → global `RSC`.
 *
 * Fusion of Style A (RSA: 3D hero objects, keyword headlines, glass rim, whip with motion blur) and Style B
 * (RSB: chrome, kicker → headline, iOS components, literal captions, dissolve/portal). C builds ON the public
 * builders of both packs — load order: GSAP → runtime.js (RS) → a.js (RSA) → b.js (RSB) → c.js (RSC), CSS a → b → c.
 *
 * Contract (references/contracts.md): every builder is `RSC.x(container, props, tl, at) → HTMLElement|object`,
 * all times absolute local seconds, entrances are seek-safe `fromTo`, later state changes `immediateRender:false`.
 * Text never exits on its own; only RSC.tx.* moves pages out. Build after `await RSC.ready()` (headlines are
 * measured at build time), register the timeline last.
 *
 * Page model: RSC.page() → root with `.bg .content .inner .live .theme` — the same shape RSA.transition expects,
 * so A's whip/blur-drift run on C pages unchanged. Layouts (RSC.layout.*) put their blocks into `.live`, a flex
 * column spanning the live area (y 230–1575) so the content block is centred at y ≈ 902 (layouts.md §1).
 */
(function () {
  "use strict";
  const RS = window.RS, RSA = window.RSA, RSB = window.RSB;
  if (!RS || !RSA || !RSB) throw new Error("RSC needs runtime.js (RS), style-a lib (RSA) and style-b lib (RSB) loaded first");
  const RSC = { version: "1.0.0" };
  const el = (tag, cls, parent, style) => { const e = RS.el(tag, cls, parent); if (style) Object.assign(e.style, style); return e; };
  const ft = RSB.ft;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /** Rhythm (layouts.md §1) — identical in every scene of a video. */
  const RH = (RSC.RHYTHM = { kh: 34, hv: 90, vc: 74, live: { top: 230, bottom: 1575, left: 90, right: 990 } });

  /** C word reveal = A's blur-rise (blur 14, y 22) at B's tempo (0.3 s power3.out). */
  const WORD = { blur: 14, y: 22, x: 0, dur: 0.3, ease: "power3.out" };
  /** Normalise words: [{w,t}] | string (+at, stagger). */
  const words = (spec, at, stagger) => RSB.words(spec, at, stagger);
  RSC.words = words;

  /** Fonts the measuring builders depend on (Inter 300–800 via style-b tokens). */
  RSC.ready = function () {
    const f = document.fonts;
    const extra = f && f.load ? ["300 46px Inter", "400 40px Inter", "600 36px Inter", "700 92px Inter", "700 330px Inter"].map((s) => f.load(s).catch(() => null)) : [];
    return Promise.all([RSB.ready()].concat(extra)).then(() => (f ? f.ready : null));
  };

  const mark = (n) => { n.classList.add("rsc-m"); return n; }; // measured block (RSC.audit)

  /* ================================================================== *
   * PAGE + CHROME
   * ================================================================== */

  /**
   * Scene page. theme: 'dark' (#0B0D0D + 36 px dots) | 'light' (#FBFDFD + 24 px dots) | 'blue' (B takeover + white dots).
   * glow (dark only): 'orange' | 'teal' | 'emerald' | 'navy' | 'violet' (A accent backgrounds as overlays); 'lavender' on light.
   * kind: 'cinematic' (A look, 3D hero, keyword) | 'ui' (B component). glass: B components render as glass-on-dark
   * (default: true on cinematic dark scenes and on blue).
   * @returns {HTMLElement} root with .bg .content .inner .live .theme .kind
   */
  RSC.page = function (container, props = {}) {
    const theme = props.theme || "dark";
    const inkA = theme === "light" ? "rsa-theme-light" : "rsa-theme-dark";
    const inkB = theme === "light" ? "theme-light" : theme === "blue" ? "theme-blue" : "theme-dark";
    const root = el("div", `rsc rsb rsc-page rsc-${theme} ${inkA} ${inkB}`, container);
    const kind = props.kind || "cinematic";
    const glass = props.glass ?? (theme === "blue" || (theme === "dark" && kind === "cinematic"));
    if (glass) root.classList.add("rsc-glass");
    root.bg = el("div", "rsc-bg", root);
    if (theme === "blue") { el("div", "rsc-plate rsc-plate--blue", root.bg); el("div", "rsc-gridc rsc-gridc--blue", root.bg); }
    else RSA.background(root.bg, { theme: theme === "light" ? "light" : "dark" });
    if (props.glow) el("div", `rsc-glow rsc-glow--${props.glow}`, root.bg);
    root.content = el("div", "rsc-content", root);
    root.inner = el("div", "rsc-inner", root.content);
    root.live = el("div", "rsc-live", root.inner);
    root.theme = theme + (props.glow ? ":" + props.glow : "");
    root.kind = kind;
    root.dataset.theme = root.theme;
    return root;
  };

  /**
   * Persistent chrome (B breadcrumb + page dots), C variant: dots glow on dark. Same props as RSB.chrome;
   * step themes 'dark' | 'light' | 'blue' (glow variants map to 'dark').
   */
  RSC.chrome = function (container, props, tl, at = 0) {
    const map = (t) => (t ? String(t).split(":")[0] : t);
    const p = Object.assign({}, props, { theme: map(props.theme || "dark"), steps: (props.steps || []).map((s) => Object.assign({}, s, { theme: map(s.theme) })) });
    const c = RSB.chrome(container, p, tl, at);
    c.classList.add("rsc-chrome");
    return c;
  };

  /* ================================================================== *
   * TYPE
   * ================================================================== */

  function toLines(text) {
    if (Array.isArray(text)) return text;
    return String(text).split(/\s*(?:\/|\n)\s*/).filter(Boolean);
  }

  /**
   * Headline. mode 'keyword' (A: paraphrase, ≤2 lines, 92 px Bold) · 'ui' (B: literal, ONE line, 100 px) ·
   * 'statement' (2 big lines, 124 px). Words pre-laid-out at final positions, then blur-rise in place.
   * Shrinks to fit maxW (900) at build time. Highlight words take the iOS accent blue.
   * @param {{text:string|string[], words?:Array<{w,t}>, at?:number, stagger?:number, mode?:string, highlight?:string[],
   *          size?:number, maxW?:number, minPx?:number, mt?:number, color?:string}} p
   */
  RSC.headline = function (container, p, tl, at) {
    const mode = p.mode || "keyword";
    const h = mark(el("div", `rsc-h rsc-h--${mode}`, container));
    if (p.mt != null) h.style.marginTop = p.mt + "px";
    if (p.size) h.style.fontSize = p.size + "px";
    if (p.color) h.style.color = p.color;
    const t0 = p.at ?? at, st = p.stagger ?? 0.12;
    let lines = toLines(p.text || (p.words || []).map((o) => o.w).join(" "));
    if (mode === "ui" && lines.length > 1) lines = [lines.join(" ")];
    const timed = p.words || [];
    let k = 0;
    const spans = [];
    const rows = lines.map((line) => {
      const ln = el("div", "rsc-hl", h);
      const ws = line.split(/\s+/).filter(Boolean).map((w) => { const t = timed[k] ? timed[k].t : t0 + k * st; k++; return { w, t }; });
      spans.push(...RS.words(ln, ws, tl, Object.assign({}, WORD, { highlight: p.highlight, hlClass: "rsc-accent" })));
      return ln;
    });
    // fit: shrink the whole block until the widest line ≤ maxW (build time only)
    const maxW = p.maxW ?? 900, minPx = p.minPx ?? 64;
    const px0 = parseFloat(getComputedStyle(h).fontSize);
    const widest = Math.max(...rows.map((r) => { r.style.display = "inline-block"; const w = r.getBoundingClientRect().width; r.style.display = ""; return w; }));
    if (widest > maxW) h.style.fontSize = Math.max(minPx, Math.floor(px0 * maxW / widest)) + "px";
    h.words = spans;
    return h;
  };

  function textLine(cls, container, p, tl, at) {
    const n = mark(el("div", cls, container));
    if (p.mt != null) n.style.marginTop = p.mt + "px";
    if (p.color) n.style.color = p.color;
    const ws = words(p.words || p.text, p.at ?? at, p.stagger ?? 0.12);
    n.spans = RS.words(n, ws, tl, { blur: 11, x: 22, y: 0, dur: 0.14, ease: "power3.out", highlight: p.highlight, hlClass: "rsc-accent" });
    return n;
  }
  /** Kicker (B: 46 px Light grey, literal words, B word reveal). @param {{text|words, at, mt, highlight}} p */
  RSC.kicker = (container, p, tl, at) => textLine("rsc-kicker", container, p, tl, at);
  /** Sub line (46 px Light grey). */
  RSC.sub = (container, p, tl, at) => textLine("rsc-sub", container, p, tl, at);

  /**
   * Grey caption (A): anchored typewriter, each char blurs in, ~26 cps, words never reflow.
   * @param {{text:string, at?:number, cps?:number, mt?:number}} p
   */
  RSC.caption = function (container, p, tl, at) {
    const c = mark(el("div", "rsc-caption", container));
    if (p.mt != null) c.style.marginTop = p.mt + "px";
    c.innerHTML = String(p.text).split(/(\s+)/).map((tok) => /^\s+$/.test(tok) ? " " : `<span class="tw">${[...tok].map((ch) => `<span class="c">${esc(ch)}</span>`).join("")}</span>`).join("");
    const cs = c.querySelectorAll(".c");
    if (cs.length) tl.fromTo(cs, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "none", stagger: 1 / (p.cps || 26) }, p.at ?? at);
    return c;
  };

  /* ================================================================== *
   * OBJECTS
   * ================================================================== */

  /**
   * 3D hero (A object, C framing): in-flow box size×size with an accent glow behind and a soft floor contact,
   * the object enters through RSA.hero (pop | rise | slide | drop) with A's motion blur, then idles (finite sine bob).
   * @param {{src?:string, emoji?:string, blob?:string, size?:number (500–650), entry?:string, from?:string,
   *          glow?:string (css colour), idle?:boolean|{amp,period,until}, mt?:number}} p
   */
  RSC.hero3d = function (container, p, tl, at) {
    const size = p.size || 560;
    const box = mark(el("div", "rsc-hero", container, { width: size + "px", height: size + "px" }));
    if (p.mt != null) box.style.marginTop = p.mt + "px";
    const glow = el("div", "rsc-hero-glow", box);
    if (p.glow) glow.style.setProperty("--glow", p.glow);
    const floor = el("div", "rsc-hero-floor", box);
    tl.fromTo(glow, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" }, at);
    tl.fromTo(floor, { opacity: 0, scaleX: 0.5 }, { opacity: 1, scaleX: 1, duration: 0.4, ease: "power3.out" }, at + 0.08);
    const idle = p.idle === false ? null : Object.assign({ amp: 10, period: 3.2, until: at + 6 }, typeof p.idle === "object" ? p.idle : {});
    const obj = RSA.hero(box, { src: p.src, emoji: p.emoji, blob: p.blob, size, x: size / 2, y: size / 2, entry: p.entry || "pop", from: p.from, shadow: false, idle }, tl, at);
    box.obj = obj;
    return box;
  };

  /**
   * Glass card (A `glass` variant: lit rim + inner glow + slight 3D tilt) as an in-flow block.
   * Children go into the returned card (`.body`). @param {{width, height, tilt, padding, mt}} p
   */
  RSC.glassCard = function (container, p, tl, at) {
    const w = p.width || 800, h = p.height || 400;
    const holder = el("div", "rsc-slot", container, { width: w + "px", height: h + "px" });
    if (p.mt != null) holder.style.marginTop = p.mt + "px";
    const card = RSA.card(holder, { variant: "glass", x: w / 2, y: h / 2, width: w, height: h, radius: p.radius || 48, tilt: p.tilt || { rx: 2, ry: p.ry ?? -3 }, padding: p.padding ?? 36 }, tl, at);
    card.style.display = "flex"; card.style.flexDirection = "column"; card.style.alignItems = "center"; card.style.justifyContent = "space-between";
    card.style.position = "relative";
    holder.card = card;
    return holder;
  };

  /**
   * Stat inside a card/slot: A slot-machine roll (RSA.numberRoll) centred in an in-flow box.
   * @param {{value:string, unit?:string, size?:number, color?:string, width?:number}} p
   */
  RSC.stat = function (container, p, tl, at) {
    const size = p.size || 120, w = p.width || 300;
    const box = el("div", "rsc-slot", container, { width: w + "px", height: Math.round(size * 1.08) + "px" });
    const n = RSA.numberRoll(box, { value: p.value, unit: p.unit, x: w / 2, y: Math.round(size * 0.54), size, color: p.color }, tl, at);
    n.style.fontWeight = "700"; n.style.letterSpacing = "-0.04em";
    box.num = n;
    return box;
  };

  /**
   * B component restyled for C. kind = any RSB builder name ('card', 'quoteCard', 'notification', 'skeletonRows',
   * 'segmented', 'player', 'capsule', …). glass:true forces the glass-on-dark skin on this element even on a
   * non-glass page. Returns whatever the RSB builder returns.
   */
  RSC.uiCard = function (container, p, tl, at) {
    const fn = RSB[p.kind || "card"];
    if (typeof fn !== "function") throw new Error("RSC.uiCard: unknown RSB builder " + p.kind);
    const n = fn(container, p, tl, at);
    if (p.glass && n && n.classList) n.classList.add("rsc-glass-el");
    return n;
  };

  /**
   * Footage slot — neutral, labelled placeholder for talking-head parts (never a drawn person). Real runs mount
   * edit/head.mp4 underneath (assembler) and the scene page is transparent: pass `transparent:true` to skip it.
   * @param {{label?:string, sub?:string, transparent?:boolean}} p
   */
  RSC.footage = function (container, p = {}) {
    if (p.transparent) return null;
    const f = el("div", "rsc-footage", container);
    const l = el("div", "rsc-footage-label", f);
    l.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><rect x="2.5" y="6" width="13" height="12" rx="2.5"/><path d="M15.5 10.5l6-3.5v10l-6-3.5z"/></svg>
      <b>${esc(p.label || "FOOTAGE SLOT")}</b><span>${esc(p.sub || "edit/head.mp4 · говорящая голова")}</span>`;
    return f;
  };

  /* ================================================================== *
   * LAYOUTS — RSC.layout.<id>(page, spec, tl, at) → {root, parts…}
   * Every layout fills `.live` (centred block) unless noted. spec.* line props accept {text|words, at, highlight}.
   * ================================================================== */
  const L = (RSC.layout = {});
  const live = (page) => page.live || page;
  function slot(parent, w, h, mt) {
    const s = mark(el("div", "rsc-slot", parent));
    if (w) s.style.width = w + "px";
    if (h) s.style.height = h + "px";
    if (mt != null) s.style.marginTop = mt + "px";
    return s;
  }
  function head(parent, spec, tl, at, mode) {
    const parts = {};
    if (spec.kicker) parts.kicker = RSC.kicker(parent, spec.kicker, tl, at);
    if (spec.headline) parts.headline = RSC.headline(parent, Object.assign({ mode, mt: spec.kicker ? RH.kh : 0 }, spec.headline), tl, at);
    return parts;
  }
  /** Tier box for fixed-position layouts: flex column centred on stage y. */
  function tier(parent, y) {
    const t = el("div", "rsc-tier", parent);
    t.style.top = (y - RH.live.top - 500) + "px";
    return t;
  }

  /**
   * `stack` — kicker + headline (ui) + one component (+ caption), whole block centred.
   * spec: {kicker, headline, sub, visual:(slot)=>el, visualW, visualH, caption}
   */
  L.stack = function (page, spec, tl, at) {
    const r = live(page), parts = head(r, spec, tl, at, spec.headline?.mode || "ui");
    if (spec.sub) parts.sub = RSC.sub(r, Object.assign({ mt: 30 }, spec.sub), tl, at);
    if (spec.visual) { parts.slot = slot(r, spec.visualW, spec.visualH, RH.hv); parts.visual = spec.visual(parts.slot); }
    if (spec.caption) parts.caption = RSC.caption(r, Object.assign({ mt: RH.vc }, spec.caption), tl, at);
    return Object.assign({ root: r }, parts);
  };

  /**
   * `hero` — A's three tiers: keyword headline centred y 440, 3D hero centred y 960 (500–650 px), caption y 1450.
   * spec: {kicker?, headline, hero:{src,size,entry,at,glow}, visual?:(slot)=>el (instead of hero), caption}
   */
  L.hero = function (page, spec, tl, at) {
    const r = live(page), parts = {};
    const top = tier(r, spec.headlineY || 440);
    Object.assign(parts, head(top, spec, tl, at, spec.headline?.mode || "keyword"));
    const mid = tier(r, spec.visualY || 965);
    if (spec.hero) parts.hero = RSC.hero3d(mid, spec.hero, tl, spec.hero.at ?? at);
    else if (spec.visual) { parts.slot = slot(mid, spec.visualW, spec.visualH); parts.visual = spec.visual(parts.slot); }
    if (spec.caption) parts.caption = RSC.caption(tier(r, spec.captionY || 1450), spec.caption, tl, at);
    return Object.assign({ root: r }, parts);
  };

  /**
   * `visual-top` — big visual first (≤ 55 % height), headline below, caption. spec: {hero|visual, visualH, headline, caption, extra:(slot)=>…}
   */
  L.visualTop = function (page, spec, tl, at) {
    const r = live(page), parts = {};
    if (spec.hero) { parts.slot = slot(r); parts.hero = RSC.hero3d(parts.slot, spec.hero, tl, spec.hero.at ?? at); }
    else { parts.slot = slot(r, spec.visualW, spec.visualH); parts.visual = spec.visual(parts.slot); }
    if (spec.extra) spec.extra(parts.slot);
    parts.headline = RSC.headline(r, Object.assign({ mode: "keyword", mt: RH.hv }, spec.headline), tl, at);
    if (spec.caption) parts.caption = RSC.caption(r, Object.assign({ mt: 40 }, spec.caption), tl, at);
    return Object.assign({ root: r }, parts);
  };
  L["visual-top"] = L.visualTop;

  /**
   * `number` — kicker, giant number (B counter with vertical motion blur, 300–420 px), sub line, badge.
   * spec: {kicker, value:{from,to,dur,at,suffix,size,sep}, sub, badge:{text,kind,at}}
   */
  L.number = function (page, spec, tl, at) {
    const r = live(page), parts = head(r, spec, tl, at, "ui");
    const v = spec.value;
    const s = slot(r, null, null, 20);
    parts.number = RSB.counter(s, { from: v.from ?? 0, to: v.to, dur: v.dur ?? 1, size: v.size || 330, sep: v.sep ?? " ",
      suffix: v.suffix ? { text: v.suffix, size: v.suffixSize || 96, color: "var(--rsc-kick)" } : null, blur: 8 }, tl, v.at ?? at + 0.3);
    parts.number.classList.add("rsc-num");
    parts.number.num.style.lineHeight = "0.96";
    if (spec.sub) parts.sub = RSC.sub(r, Object.assign({ mt: 26 }, spec.sub), tl, at);
    if (spec.badge) { const b = slot(r, null, null, 56); parts.badge = RSB.capsule(b, Object.assign({ kind: "red" }, spec.badge), tl, spec.badge.at ?? at + 1); }
    return Object.assign({ root: r }, parts);
  };

  /**
   * `media` — iPhone mockup (B) at 60–75 % height with kicker + one-line headline above.
   * spec: {kicker, headline, phone:{width=460, html|src|node, at, enter}, after:(slot, phone, geo)=>…}
   * geo.toSlot(sx, sy) converts screen px (565-wide phone space, screen origin) → slot px for cursors/overlays.
   */
  L.media = function (page, spec, tl, at) {
    const r = live(page), parts = head(r, spec, tl, at, "ui");
    const w = spec.phone.width || 460, k = w / 565, h = Math.round(1160 * k);
    const s = slot(r, 900, h, 70);
    const x0 = Math.round((900 - w) / 2);
    parts.phone = RSB.iphone(s, Object.assign({ x: x0, y: 0, floor: true }, spec.phone, { width: w }), tl, spec.phone.at ?? at);
    parts.geo = { k, x0, toSlot: (sx, sy) => ({ x: x0 + (24 + sx) * k, y: (24 + sy) * k }) };
    parts.slot = s;
    if (spec.after) spec.after(s, parts.phone, parts.geo);
    return Object.assign({ root: r }, parts);
  };

  /**
   * `list` — kicker + headline + optional notification + 3–4 rows building downward (B skeletonRows).
   * spec: {kicker, headline, notification?:{…RSB.notification, at}, rows:[{emoji,caption,title,at}], enterAt, stagger}
   */
  L.list = function (page, spec, tl, at) {
    const r = live(page), parts = head(r, spec, tl, at, spec.headline?.mode || "ui");
    const s = slot(r, 800, null, RH.hv);
    s.style.gap = "30px";
    if (spec.notification) parts.notification = RSB.notification(s, Object.assign({ width: 790 }, spec.notification), tl, spec.notification.at ?? at);
    parts.rows = RSB.skeletonRows(s, { rows: spec.rows, enterAt: spec.enterAt ?? at + 0.3, stagger: spec.stagger ?? 0.1, height: spec.rowHeight || 150 }, tl, at);
    parts.slot = s;
    return Object.assign({ root: r }, parts);
  };

  /**
   * `compare` — keyword headline + two glass columns (before → after), each: title, 3D object, rolled stat, note.
   * spec: {headline, left:{title, src, value, unit, color, note, at}, right:{…}, caption, cardH=560}
   */
  L.compare = function (page, spec, tl, at) {
    const r = live(page), parts = head(r, spec, tl, at, "keyword");
    const row = mark(el("div", "rsc-row", r, { marginTop: RH.hv + "px" }));
    const H = spec.cardH || 560;
    const col = (c, ry) => {
      const holder = RSC.glassCard(row, { width: 400, height: H, ry, padding: "34px 24px 38px" }, tl, c.at);
      const card = holder.card;
      const t = el("div", "rsc-card-title", card); t.textContent = c.title;
      const obj = el("div", "rsc-slot", card, { width: "190px", height: "190px" });
      RSA.hero(obj, { src: c.src, emoji: c.emoji, size: 190, x: 95, y: 95, entry: "pop", shadow: false }, tl, c.at + 0.15);
      RSC.stat(card, { value: c.value, unit: c.unit, size: 112, color: c.color, width: 330 }, tl, c.at + 0.35);
      if (c.note) { const n = el("div", "rsc-card-note", card); n.textContent = c.note; RS.blurIn(tl, n, c.at + 0.6, { y: 10, blur: 8, dur: 0.3 }); }
      return holder;
    };
    parts.left = col(spec.left, 4);
    parts.right = col(spec.right, -4);
    parts.row = row;
    if (spec.caption) parts.caption = RSC.caption(r, Object.assign({ mt: RH.vc }, spec.caption), tl, at);
    return Object.assign({ root: r }, parts);
  };

  /** `statement` — 2-line big headline only (breath scene, max 1 per 6 scenes). spec: {headline:{text, words, highlight}} */
  L.statement = function (page, spec, tl, at) {
    const r = live(page);
    return { root: r, headline: RSC.headline(r, Object.assign({ mode: "statement" }, spec.headline), tl, at) };
  };

  /**
   * `head` — full-frame talking head (footage slot in demos) + literal word-synced captions (B, chest band y≈1398)
   * + optional hook sticker. spec: {footage:{label,sub,transparent}, sticker:{text, emoji, y, at}, phrases:[{words}], captionY}
   */
  L.head = function (page, spec, tl, at) {
    const parts = { root: page.inner };
    parts.footage = RSC.footage(page.inner, spec.footage || {});
    if (spec.sticker) parts.sticker = RSB.sticker(page.inner, spec.sticker, tl, spec.sticker.at ?? at);
    if (spec.phrases) parts.caption = RSB.caption(page.inner, { y: spec.captionY || 1398, phrases: spec.phrases }, tl, at);
    return parts;
  };

  /**
   * `head-side` — talking head + ONE component in the chest band (y 880–1460) + captions under it.
   * spec: {footage, component:(band)=>el, bandY=900, bandH=380, phrases, captionY=1420}
   */
  L.headSide = function (page, spec, tl, at) {
    const parts = { root: page.inner };
    parts.footage = RSC.footage(page.inner, spec.footage || {});
    const band = el("div", "rsc-slot", page.inner, { position: "absolute", left: "90px", width: "900px", top: (spec.bandY || 900) + "px", height: (spec.bandH || 380) + "px" });
    mark(band);
    parts.band = band;
    if (spec.component) parts.component = spec.component(band);
    if (spec.phrases) parts.caption = RSB.caption(page.inner, { y: spec.captionY || 1420, phrases: spec.phrases }, tl, at);
    return parts;
  };
  L["head-side"] = L.headSide;

  /* ================================================================== *
   * TRANSITIONS — RSC.tx.<name>(tl, from, to, at, opts)
   * between chapters: whip · within a chapter: dissolve · talking head ↔ motion: portal
   * ================================================================== */
  const tx = (RSC.tx = {});

  /**
   * Whip (A, Der0/Dey): old content accelerates ±320 px in 150 ms with directional SVG motion blur, new content
   * settles from ∓270 px over 400 ms expo with decaying blur; bg swaps invisibly (same theme) or fades 0.25 s.
   * `at` = next sentence onset. Clip windows: to starts ≤ at−0.25, from ends ≥ at+0.15. One whoosh at at−0.12.
   */
  tx.whip = function (tl, from, to, at, o = {}) {
    RSA.transition(tl, from, to, at, { type: "whip", dir: o.dir || "up", bg: from.theme === to.theme ? "cut" : "fade" });
  };

  /**
   * Dissolve (B): out page scales to .97 + blur 6 + fades over near-black (0.55 s), in page fades from at+0.06 and
   * its content un-blurs 10→0 (A softness). Clip windows: to starts ≤ at, from ends ≥ at+0.6.
   */
  tx.dissolve = function (tl, from, to, at, o = {}) {
    to.style.opacity = "0";
    RSB.tx.dissolve(tl, from, to, at, o);
    ft(tl, to.content, { filter: "blur(10px)" }, { filter: "blur(0px)", duration: 0.5, ease: "power2.out" }, at + 0.06);
  };

  /**
   * Portal (B, De1roE4t7Lf) between talking head and motion: light orb with blue bloom travels, grows ×32,
   * near-white (#FBFDFD) flash swaps the pages at at+0.6, fades out by at+1.2. Sub-boom SFX at at−0.15.
   * @param {HTMLElement} layer overlay host above both pages (stage root). Clip windows: to ≤ at, from ≥ at+1.25.
   */
  tx.portal = function (tl, from, to, at, o = {}, layer) {
    to.style.opacity = "0";
    const r = RSB.tx.portal(tl, from, to, at, o, layer);
    r.whiteout.style.background = "#FBFDFD";
        const bp = window.RS_BRAND && window.RS_BRAND.palette && window.RS_BRAND.palette.c; // brand bloom (branding.md)
    r.orb.style.boxShadow = `0 0 30px 12px rgba(255,255,255,.9), 0 0 140px 70px ${(bp && bp.portalGlow) || "rgba(10,132,255,.45)"}`;
    return r;
  };

  /** Clip window a transition needs around `at`: {start (next page), end (previous page)}. */
  RSC.txWindow = function (type, at) {
    if (type === "whip") return { start: at - 0.25, end: at + 0.15 };
    if (type === "dissolve") return { start: at, end: at + 0.6 };
    if (type === "portal") return { start: at, end: at + 1.25 };
    return { start: at, end: at };
  };

  /* ================================================================== *
   * QA helper — union bbox of measured blocks (.rsc-m) in stage px at the CURRENT seek time.
   * ================================================================== */
  RSC.audit = function (page) {
    const stage = page.closest("[data-composition-id]") || document.body;
    const s = stage.getBoundingClientRect(), k = s.height ? s.height / 1920 : 1;
    let top = Infinity, bottom = -Infinity, left = Infinity, right = -Infinity;
    page.querySelectorAll(".rsc-m").forEach((n) => {
      const b = n.getBoundingClientRect();
      if (!b.height) return;
      top = Math.min(top, (b.top - s.top) / k); bottom = Math.max(bottom, (b.bottom - s.top) / k);
      left = Math.min(left, (b.left - s.left) / k); right = Math.max(right, (b.right - s.left) / k);
    });
    const height = bottom - top;
    return { top: Math.round(top), bottom: Math.round(bottom), left: Math.round(left), right: Math.round(right),
      centre: Math.round((top + bottom) / 2), height: Math.round(height), fill: +(height / (RH.live.bottom - RH.live.top)).toFixed(2) };
  };

  window.RSC = RSC;
})();
