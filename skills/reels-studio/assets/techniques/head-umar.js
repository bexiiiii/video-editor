/* reels-studio · technique pack "head-umar" — global `RSX`.
 *
 * Optional talking-head editorial techniques measured in teardowns/style-b/Dd1b9kEA-KL.md and Dd3Uz4Mgbn-.md
 * (karaoke captions, chest-band glow widgets + morphs, paper editorial section with giant numerals, condensed hero
 * word, dark grain section, lens-edge blur, jump zoom / phone pull-out, pixel glitch, voice-muffle cue).
 * Not a style: any style may call it. Loading it is inert — it only defines `window.RSX` and `.rsx-*` CSS.
 *
 * Contract (references/contracts.md):  RSX.<technique>(container, props, tl, at) → HTMLElement
 *   absolute LOCAL seconds; entrances fromTo, later state changes RSB.ft (immediateRender:false); deterministic;
 *   build after `await RSX.ready()` (glyph metrics are measured at build time); register the timeline last.
 * Requires: GSAP → runtime.js (RS) → tokens-b.css + b.js (RSB) → techniques/head-umar.css + head-umar.js.
 * If RSB is absent (e.g. a style-A-only composition) RSX stays undefined-safe: `RSX.available === false`.
 * People: a human is always real footage/photo (`node`/`src`); otherwise RSB.footage's labelled slot. No drawn figures.
 */
(function () {
  "use strict";
  const RS = window.RS, RSB = window.RSB;
  const RSX = { version: "1.0.0", available: !!(RS && RSB) };
  window.RSX = RSX;
  if (!RSX.available) return; // inert without RS + RSB
  const el = RS.el, ft = RSB.ft, words = RSB.words;
  const FPS = 30, F = 1 / FPS;
  RSX.BAND = [880, 1460];

  const CHECK = (stroke = "#fff", w = 3.4) =>
    `<svg viewBox="0 0 24 24"><path d="M5 12.5l4.6 4.6L19 7.7" fill="none" stroke="${stroke}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

  /* ---------------------------------------------------------------- helpers */

  /** Load Inter (RSB.ready) + Oswald 200/700 + Inter 500 display sizes. */
  RSX.ready = function () {
    const f = document.fonts, base = RSB.ready();
    if (!f || !f.load) return base;
    return Promise.all([base].concat(["200 215px Oswald", "700 330px Oswald", "500 1150px Inter", "550 58px Inter"].map((s) => f.load(s).catch(() => null)))).then(() => f.ready);
  };
  let _ctx = null;
  function metrics(font, sample) {
    _ctx = _ctx || document.createElement("canvas").getContext("2d");
    _ctx.font = font;
    const m = _ctx.measureText(sample);
    return { asc: m.actualBoundingBoxAscent, fa: m.fontBoundingBoxAscent, fd: m.fontBoundingBoxDescent, w: m.width };
  }
  /** Offset from an element's top to the top of `sample`'s glyphs for line-height lineH (px). */
  function glyphOffset(font, sample, lineH) { const m = metrics(font, sample); return (lineH - (m.fa + m.fd)) / 2 + m.fa - m.asc; }
  /** Font size whose glyph height of `sample` = h. */
  function sizeForHeight(family, weight, sample, h) { return Math.round((h / metrics(`${weight} 100px ${family}`, sample).asc) * 100); }
  RSX.metrics = metrics; RSX.glyphOffset = glyphOffset; RSX.sizeForHeight = sizeForHeight;
  function abs(n, x, y, z) { n.style.position = "absolute"; if (x != null) n.style.left = x + "px"; if (y != null) n.style.top = y + "px"; if (z != null) n.style.zIndex = z; return n; }

  /** Karaoke word reveal: words pre-placed; at onset grey → full colour + opacity, blur 5→0, 0.21 s (optional x-settle). */
  function karaoke(target, ws, tl, o = {}) {
    const spans = RS.words(target, ws, tl, { fromOpacity: 0, blur: o.blur ?? 5, x: o.settle ?? 0, dur: o.dur ?? 0.21, ease: "power2.out" });
    if (o.from && o.to) spans.forEach((s, i) => tl.fromTo(s, { color: o.from }, { color: o.to, duration: o.dur ?? 0.21, ease: "power2.out", immediateRender: false }, ws[i].t));
    return spans;
  }
  RSX.karaoke = karaoke;

  /* ================================================================== *
   * SURFACES
   * ================================================================== */

  /**
   * Editorial / dark surface page. paper = warm radial #F4F2F0→#DDDAD7 (+ embossed hairlines `emboss:{v:[x…],h:[y…]}`,
   * ref x 342/736, y 660/1257); light = flat #EDEBE9; dark = #212121 + grain + 54 px grid in a radial mask
   * (`grid:{x,y,r}`), lit near the widget; head = near-black. `lensPass` = left-side directional blur (Dd3Uz4Mgbn- §2).
   * @param {{theme?:'paper'|'light'|'dark'|'head', emboss?, grid?, lensPass?:boolean, visible?:boolean}} props
   * @returns {HTMLElement} page (`.content`)
   */
  RSX.page = function (container, props = {}) {
    const theme = props.theme || "paper";
    const page = el("div", `rsx rsx-page ${theme}`, container);
    if (theme === "paper" && props.emboss) {
      (props.emboss.v || []).forEach((x) => abs(el("div", "rsx-emboss v", page), x - 2, null));
      (props.emboss.h || []).forEach((y) => abs(el("div", "rsx-emboss h", page), null, y - 1));
    }
    if (theme === "dark") {
      const g = Object.assign({ x: 540, y: 900, r: 470 }, props.grid || {});
      const grid = el("div", "rsx-dgrid", page);
      grid.style.webkitMaskImage = grid.style.maskImage = `radial-gradient(circle at ${g.x}px ${g.y}px, #000 0, rgba(0,0,0,.55) ${Math.round(g.r * 0.55)}px, transparent ${g.r}px)`;
      const lit = el("div", "rsx-dgrid lit", page);
      lit.style.webkitMaskImage = lit.style.maskImage = `radial-gradient(circle at ${g.x}px ${g.y}px, rgba(0,0,0,.9) 0, transparent ${Math.round(g.r * 0.62)}px)`;
      el("div", "rsx-grain", page);
    }
    page.content = el("div", "rsx-content", page);
    if (props.lensPass) el("div", "rsx-lenspass", page);
    if (props.visible === false) page.style.opacity = "0";
    return page;
  };

  /* ================================================================== *
   * FOOTAGE: lens edge blur, jump zoom, pull-out
   * ================================================================== */

  /**
   * Zoom a layer about a point (transform-origin stays centre → GSAP owns x/y/scale). kind 'jump' = 2-frame jump
   * to `scale` (2.4× in Dd3Uz4Mgbn- 6.125 s); 'punch' = 0.25 s power3.out. `drift` px/s while zoomed; `until` = hard cut back.
   * @param {{scale?, origin?:[x,y], kind?:'jump'|'punch', drift?, until?, w?, h?}} z
   */
  function zoomAbout(tl, node, at, z = {}) {
    const S = z.scale ?? 2.4, W = z.w ?? 1080, H = z.h ?? 1920;
    const [ox, oy] = z.origin || [W * 0.62, H * 0.4];
    const x = Math.round((1 - S) * (ox - W / 2)), y = Math.round((1 - S) * (oy - H / 2));
    const d = z.kind === "punch" ? 0.25 : 2 * F;
    ft(tl, node, { scale: 1, x: 0, y: 0 }, { scale: S, x, y, duration: d, ease: z.kind === "punch" ? "power3.out" : "none" }, at);
    if (z.until != null) {
      if (z.drift) ft(tl, node, { x }, { x: x + Math.round(z.drift * (z.until - at - d)), duration: z.until - at - d, ease: "none" }, at + d);
      tl.set(node, { scale: 1, x: 0, y: 0 }, z.until);
    }
  }
  RSX.zoomAbout = zoomAbout;
  /** Jump zoom 2.4× (2 frames) on any layer — alias of zoomAbout with kind 'jump'. */
  RSX.jumpZoom = function (tl, node, at, o = {}) { zoomAbout(tl, node, at, Object.assign({ kind: "jump" }, o)); };

  /**
   * Full-frame talking head with strong lens edge blur (sharp ellipse over face+torso, radial smear at the edges,
   * camera-fixed above the zoom layer — Dd1b9kEA-KL §1) and optional jump zooms.
   * @param {{node?, src?, label?, sub?, slot?, lens?:boolean|number, warm?:boolean, zooms?:Array}} props
   * @returns {HTMLElement} head (`.cam`, `.footage`)
   */
  RSX.headBase = function (container, props = {}, tl, at) {
    const head = el("div", "rsx rsx-head", container);
    const cam = el("div", "cam", head);
    const f = RSB.footage(cam, { node: props.node, src: props.src, fit: props.fit, label: props.label, sub: props.sub, slot: props.slot || { x: 170, y: 250, w: 740, h: 620 } });
    if (props.lens !== false) RSX.lens(head, { blur: typeof props.lens === "number" ? props.lens : null, warm: props.warm });
    (props.zooms || []).forEach((z) => zoomAbout(tl, cam, z.at, z));
    head.cam = cam; head.footage = f;
    return head;
  };
  /** Lens edge blur overlay alone (put it above any footage layer). @param {{blur?:number, warm?:boolean}} props */
  RSX.lens = function (container, props = {}) {
    const l = el("div", "rsx-lens" + (props.warm ? " warm" : ""), container);
    if (props.blur) l.style.backdropFilter = l.style.webkitBackdropFilter = `blur(${props.blur}px)`;
    return l;
  };

  /**
   * Proof iPhone with full-frame → phone pull-out (RSB.iphone, enter 'pullout': scale 2→1 in 8 frames expo.out;
   * 575×1170 at y 270 — Dd3Uz4Mgbn- §5). `exitAt` lifts it −300 px / scale .96 (power2.in 0.4 s).
   * @param {{x?, y?, width?, node?, src?, html?, label?, enter?, floor?, exitAt?}} props
   */
  RSX.pullout = function (container, props = {}, tl, at) {
    const W = props.width ?? 575;
    const h = RSB.iphone(container, { x: props.x ?? Math.round((1080 - W) / 2), y: props.y ?? 270, width: W, node: props.node, src: props.src, html: props.html, label: props.label, enter: props.enter || "pullout", floor: props.floor ?? false }, tl, at);
    if (props.exitAt != null) ft(tl, h, { y: 0, scale: 1 }, { y: -300, scale: 0.96, duration: 0.4, ease: "power2.in" }, props.exitAt);
    return h;
  };

  /* ================================================================== *
   * CAPTIONS
   * ================================================================== */
  const CAP = {
    head: { y: 1398, size: 62, color: "#FFFFFF", from: "#9A9A9A", settle: 0 },
    paper: { y: 1329, size: 63, color: "#1A1A1A", from: "#8A8A8A", settle: 28 },
    dark: { y: 1375, size: 48, color: "#FFFFFF", from: "#9A9A9A", settle: 0 },
    light: { y: 295, size: 44, color: "#211F1E", from: "#B9B7B5", settle: 0 },
  };
  /**
   * Karaoke caption line (Dd1b9kEA-KL §4, Dd3Uz4Mgbn- §4): one centred line ≤ 32 chars, 500, −0.05em; words pre-placed,
   * grey → full colour in 0.21 s (+5 px blur; paper +28 px x-settle); phrase swap in one frame. Wraps RSB.caption.
   * @param {{theme?:'head'|'paper'|'dark'|'light', y?, size?, color?, from?, settle?, phrases:Array<{words?|text?, at?}>}} props
   */
  RSX.caption = function (container, props, tl, at) {
    const th = props.theme || "head";
    (props.phrases || []).forEach((p) => { const t = p.text || (p.words || []).map((w) => w.w).join(" "); if (t.length > 32) console.warn(`[RSX.caption] "${t}" > 32 chars`); });
    const cap = RSB.caption(container, Object.assign({}, CAP[th], props), tl, at);
    cap.classList.add("rsx-cap-" + th);
    return cap;
  };

  /* ================================================================== *
   * CHEST BAND + WIDGETS + MORPHS
   * ================================================================== */

  /** Chest-band host (y 880–1460 on the A-roll; face stays clear); children centred. @param {{band?:[a,b], gap?}} props */
  RSX.band = function (container, props = {}) {
    const [a, b] = props.band || RSX.BAND;
    const h = abs(el("div", "rsx rsx-band", container), 90, a);
    h.style.height = (b - a) + "px"; h.style.gap = (props.gap ?? 36) + "px";
    return h;
  };

  /**
   * Morph entrance dot (16) → app tile (90, back.out 8 f) → hold → full widget (9 f expo.out), content fades in on the
   * last frames (Dd1b9kEA-KL 21.5–22.65 s). Uniform scale + border-radius only.
   * @param {{w:number, radius:number, expandAt?:number, icon?:HTMLElement, content?:HTMLElement, tile?:number}} o
   * @returns {number} expand time
   */
  function morphIn(tl, node, at, o) {
    const w = o.w, sDot = 16 / w, sTile = (o.tile ?? 90) / w, ea = o.expandAt ?? at + 1.2;
    tl.fromTo(node, { opacity: 0, scale: sDot, borderRadius: w / 2 }, { opacity: 1, duration: F, ease: "none" }, at);
    ft(tl, node, { scale: sDot, borderRadius: w / 2 }, { scale: sTile, borderRadius: 22 / sTile, duration: 8 * F, ease: "back.out(1.7)" }, at + F);
    ft(tl, node, { scale: sTile, borderRadius: 22 / sTile }, { scale: 1, borderRadius: o.radius, duration: 9 * F, ease: "expo.out" }, ea);
    if (o.icon) { tl.fromTo(o.icon, { opacity: 0 }, { opacity: 1, duration: 4 * F }, at + 2 * F); ft(tl, o.icon, { opacity: 1 }, { opacity: 0, duration: 3 * F }, ea); }
    if (o.content) tl.fromTo(o.content, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 5 * F, ease: "power2.out" }, ea + 5 * F);
    return ea;
  }
  RSX.morphIn = morphIn;

  /**
   * Glow progress widget (Dd1b9kEA-KL dark hero): 559 r120 #E9E9ED, white bloom (no drop shadow); emoji + title + "1.";
   * 4 green #4AD477 dots checked one by one; label; result word hard-swaps; percent + bar with moving specular.
   * Enters with morphIn unless `morph:false`.
   * @param {{x?, y?, flow?, emoji?, title?, index?, dots?, checks?:number[], label?, result?:Array<{text,at}>, percent?:Array<{v,at}>, expandAt?, morph?}} props
   */
  RSX.widget = function (container, props, tl, at) {
    const w = el("div", "rsx rsx-widget", container);
    if (props.flow) w.style.position = "relative"; else abs(w, props.x ?? 260, props.y ?? 680);
    const icon = el("div", "icon emo", w); icon.textContent = props.emoji || "🎬";
    const c = el("div", "content", w);
    const r1 = el("div", "row1", c);
    el("span", "emo", r1).textContent = props.emoji || "🎬";
    el("div", "ttl", r1).textContent = props.title || "";
    el("div", "idx", r1).textContent = props.index || "1.";
    el("div", "div", c);
    const dots = el("div", "dots", c), checks = props.checks || [];
    const ds = Array.from({ length: props.dots ?? 4 }, () => el("div", "dot", dots, CHECK("#fff", 3)));
    el("div", "lbl", c).textContent = props.label || "Natija";
    const res = el("div", "res", c), R = props.result || [];
    const wordEls = R.map((r) => { const s = el("div", "word", res); s.textContent = r.text; return s; });
    const pct = el("div", "pct", res), P = props.percent || [{ v: 0, at }];
    pct.textContent = P[0].v + "%";
    const bar = el("div", "bar", c), fill = el("i", null, bar), spec = el("b", null, bar);
    let ea = at;
    if (props.morph === false) { RSB.pop(tl, w, at, { from: 0.85 }); tl.set(icon, { opacity: 0 }, at); }
    else ea = morphIn(tl, w, at, { w: 559, radius: 120, icon, content: c, expandAt: props.expandAt });
    ds.forEach((d, i) => {
      const p = d.querySelector("path");
      tl.fromTo(p, { strokeDasharray: 24, strokeDashoffset: 24 }, { strokeDashoffset: checks[i] != null ? 0 : 24, duration: 0.2, ease: "power2.out" }, checks[i] ?? ea);
      if (checks[i] != null) ft(tl, d, { scale: 1 }, { scale: 1.08, duration: 0.08, yoyo: true, repeat: 1 }, checks[i]);
    });
    wordEls.forEach((s, i) => {
      tl.fromTo(s, { opacity: 0 }, { opacity: i === 0 ? 1 : 0, duration: 0.001 }, ea);
      if (i > 0) { tl.set(s, { opacity: 1 }, R[i].at); tl.set(wordEls[i - 1], { opacity: 0 }, R[i].at); }
    });
    tl.fromTo(fill, { scaleX: P[0].v / 100 }, { scaleX: P[0].v / 100, duration: 0.001 }, ea);
    for (let i = 1; i < P.length; i++) {
      const o = { v: P[i - 1].v };
      tl.fromTo(o, { v: P[i - 1].v }, { v: P[i].v, duration: 0.45, ease: "power2.out", immediateRender: false, onUpdate: () => { pct.textContent = Math.round(o.v) + "%"; } }, P[i].at);
      ft(tl, fill, { scaleX: P[i - 1].v / 100 }, { scaleX: P[i].v / 100, duration: 0.45, ease: "power2.out" }, P[i].at);
    }
    tl.fromTo(spec, { x: -80 }, { x: 440, duration: 1.4, ease: "power1.inOut", repeat: 3, repeatDelay: 0.6 }, ea + 0.3);
    w.content = c; w.icon = icon; w.dots = ds; w.size = 559;
    return w;
  };

  /**
   * Gauge widget 419 r90 #E9FDFC (Dd1b9kEA-KL 28.6 s) with a 270° arc, labels and 3 blue buttons. With `from` (previous
   * widget) = squash/re-inflate morph: content blanks 2 f → squashes to 400×90 (5 f) → new tile tilted −8° → back.out(1.4).
   * @param {{x?, y?, from?:HTMLElement, tl?, tr?, a?, b?, c?, value?:number}} props
   */
  RSX.gauge = function (container, props, tl, at) {
    const S = 419, g = el("div", "rsx rsx-widget gauge", container);
    abs(g, props.x ?? Math.round((1080 - S) / 2), props.y ?? 750);
    const c = el("div", "content", g);
    const R = 150, L = 2 * Math.PI * R * 0.75, val = props.value ?? 0.62;
    c.insertAdjacentHTML("beforeend", `<svg class="arc" viewBox="0 0 331 331"><g transform="rotate(135 165.5 165.5)"><circle cx="165.5" cy="165.5" r="${R}" fill="none" stroke="#8B8B91" stroke-width="16" stroke-linecap="round" stroke-dasharray="${L} 1000"/><circle class="fg" cx="165.5" cy="165.5" r="${R}" fill="none" stroke="#34C759" stroke-width="16" stroke-linecap="round" stroke-dasharray="${L * val} 1000"/></g></svg>`);
    const t1 = abs(el("div", "t", c), 40, 30); t1.textContent = props.tl || "";
    const t2 = abs(el("div", "t", c), null, 30); t2.style.right = "40px"; t2.textContent = props.tr || "";
    const st = el("div", "stack", c);
    const a = el("div", "a", st), b = el("div", "b", st), cc = el("div", "c", st);
    a.textContent = props.a || ""; b.textContent = props.b || ""; cc.textContent = props.c || "";
    const btns = el("div", "btns", c);
    [[60, "❙❙", 20], [84, "▶", 32], [60, "✕", 24]].forEach(([s, t, fs]) => { const i = el("i", null, btns); i.style.width = i.style.height = s + "px"; i.style.fontSize = fs + "px"; i.textContent = t; });
    let t0 = at;
    if (props.from) {
      const fw = props.from;
      ft(tl, fw.content || fw, { opacity: 1 }, { opacity: 0, duration: 2 * F }, at);
      ft(tl, fw, { scaleX: 1, scaleY: 1 }, { scaleX: 400 / (fw.size || 559), scaleY: 90 / (fw.size || 559), duration: 5 * F, ease: "power3.in" }, at + 2 * F);
      ft(tl, fw, { opacity: 1 }, { opacity: 0, duration: 0.001 }, at + 7 * F);
      t0 = at + 7 * F;
    }
    tl.fromTo(g, { opacity: 0, scale: 270 / S, rotation: -8 }, { opacity: 1, duration: F, ease: "none" }, t0);
    ft(tl, g, { scale: 270 / S, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.35, ease: "back.out(1.4)" }, t0);
    tl.fromTo(c.querySelector(".fg"), { strokeDasharray: "0 1000" }, { strokeDasharray: `${L * val} 1000`, duration: 0.45, ease: "power2.out" }, t0 + 3 * F);
    [t1, t2, a, b, cc, ...btns.children].forEach((n, i) => tl.fromTo(n, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.18, ease: "back.out(1.8)" }, t0 + 3 * F + i * 2 * F));
    g.content = c; g.size = S;
    return g;
  };

  /** Widget implode (6 frames): content fades 3 f → shrinks to a blank 300 px tile → gone. */
  RSX.implode = function (tl, w, at) {
    ft(tl, w.content || w, { opacity: 1 }, { opacity: 0, duration: 3 * F }, at);
    ft(tl, w, { scale: 1 }, { scale: 300 / (w.size || 559), duration: 3 * F, ease: "power3.in" }, at + 2 * F);
    ft(tl, w, { opacity: 1 }, { opacity: 0, duration: F }, at + 5 * F);
  };

  /**
   * Chest-band stat widget: #EEEEEC r64 with white glow ring, emoji + label, rolling number (RSB.counter) + unit, green bar.
   * Morphs in from a dot (dot → tile → card) unless `morph:false`.
   * @param {{emoji?, title, value:{from?,to,dur?,at?}, unit?, bar?:{to,at}, width?, flow?, x?, y?, expandAt?, morph?}} props
   */
  RSX.stat = function (container, props, tl, at) {
    const s = el("div", "rsx rsx-stat", container), w = props.width || 760;
    s.style.width = w + "px";
    if (!props.flow) abs(s, props.x ?? Math.round((1080 - w) / 2), props.y ?? 960); // centred for any width
    const top = el("div", "top", s);
    if (props.emoji) el("span", "emo", top).textContent = props.emoji;
    el("span", null, top).textContent = props.title || "";
    const big = el("div", "big", s), v = props.value;
    const ea = props.morph === false ? at : (props.expandAt ?? at + 0.75);
    const cnt = RSB.counter(big, { flow: true, from: v.from ?? 0, to: v.to, dur: v.dur ?? 0.8, size: 150, blur: 6 }, tl, v.at ?? ea + 0.35);
    if (props.unit) el("span", "u", big).textContent = props.unit;
    if (props.bar) { const b = el("div", "bar", s), fill = el("i", null, b); tl.fromTo(fill, { scaleX: 0 }, { scaleX: props.bar.to, duration: 0.7, ease: "power2.inOut" }, props.bar.at); }
    const content = [...s.children];
    if (props.morph === false) RSB.enter(tl, s, at);
    else {
      const icon = el("div", "emo", s);
      Object.assign(icon.style, { position: "absolute", inset: "0", display: "grid", placeItems: "center", fontSize: Math.round(60 * w / 90) + "px" });
      icon.textContent = props.emoji || "✓";
      morphIn(tl, s, at, { w, radius: 64, icon, expandAt: ea });
      content.forEach((n) => tl.fromTo(n, { opacity: 0 }, { opacity: 1, duration: 5 * F, ease: "power2.out" }, ea + 5 * F));
    }
    s.counter = cnt;
    return s;
  };

  /** Avatar → pill CTA morph (wraps RSB.ctaFollow: avatar pop → pill unroll → name types → blue #227DE5 press → #2B2B2B chip). Identity from props only. */
  RSX.ctaPill = function (container, props, tl, at) {
    if (!props || !props.name || !props.name.length) throw new Error("RSX.ctaPill: name lines come from brief.cta");
    const pill = RSB.ctaFollow(container, Object.assign({ y: 1184 }, props), tl, at);
    if (props.exitAt != null) [pill.box.querySelector(".ava"), pill.box.querySelector(".name"), pill.box].forEach((n, i) => ft(tl, n, { opacity: 1 }, { opacity: 0, duration: 0.001 }, props.exitAt + i * F));
    return pill;
  };

  /* ================================================================== *
   * EDITORIAL TYPE: hero word, ghost numeral, section numerals, speaker window, checks, label pill
   * ================================================================== */

  /**
   * Condensed hero word between two lines (Dd1b9kEA-KL hook "CHEATCODE"): 58 px medium kicker / thin condensed CAPS
   * (cap height 155 ≈ 215 px Oswald 200, ≤ 880 px) / 58 px line, placed by glyph tops y₀ / y₀+75 / y₀+250 (ref y₀ 1088).
   * Kicker words reveal karaoke-style; the hero pops in 3 frames (opacity, scale 1.04→1).
   * @param {{top?:{words|text,at}, hero:{text,at}, bottom?:{words|text,at}, y?:number, ink?:boolean, capHeight?, maxW?, weight?}} props
   */
  RSX.heroWord = function (container, props, tl, at) {
    const y0 = props.y ?? 1088, ink = !!props.ink;
    const root = abs(el("div", "rsx rsx-hero" + (ink ? " ink" : ""), container), 0, 0); root.style.width = "1080px";
    const to = ink ? "#1A1A1A" : "#FFFFFF";
    const line = (spec, gt) => {
      if (!spec) return null;
      const d = abs(el("div", "k", root), 0, Math.round(gt - glyphOffset("550 58px Inter", "Ib", 58))); d.style.width = "1080px"; d.style.height = "58px";
      karaoke(d, words(spec.words || spec.text, spec.at ?? at, spec.stagger ?? 0.25), tl, { from: "#9A9A9A", to, dur: 0.19 });
      return d;
    };
    const wt = props.weight ?? 200;
    let size = sizeForHeight("Oswald", wt, "H", props.capHeight ?? 155);
    const m = metrics(`${wt} ${size}px Oswald`, props.hero.text.toUpperCase());
    if (m.w > (props.maxW ?? 880)) size = Math.floor(size * (props.maxW ?? 880) / m.w);
    const h = abs(el("div", "h", root), 0, Math.round(y0 + 75 - glyphOffset(`${wt} ${size}px Oswald`, "H", size)));
    Object.assign(h.style, { width: "1080px", fontWeight: wt, fontSize: size + "px", lineHeight: size + "px", height: size + "px" });
    h.textContent = props.hero.text;
    tl.fromTo(h, { opacity: 0, scale: 1.04 }, { opacity: 1, scale: 1, duration: 3 * F, ease: "power1.out" }, props.hero.at ?? at);
    root.top = line(props.top, y0); root.bottom = line(props.bottom, y0 + 250); root.hero = h;
    return root;
  };

  /**
   * Giant pale section numeral "01/02/03" (Dd3Uz4Mgbn- §2): Inter 500 ≈ 1150 px #C2C2C2 blur 3, glyph top 1130,
   * bleeding off bottom/right, behind content; digits rise +420 px, 0.1 s stagger, 0.33 s expo.out; static after.
   * @param {{text:string, size?, glyphTop?, x?}} props
   */
  RSX.ghostNumeral = function (container, props, tl, at) {
    const size = props.size ?? 1150, lh = Math.round(size * 0.8);
    const g = el("div", "rsx rsx-ghost", container);
    g.style.fontSize = size + "px"; g.style.lineHeight = lh + "px";
    abs(g, props.x ?? -14, Math.round((props.glyphTop ?? 1130) - glyphOffset(`500 ${size}px Inter`, "0", lh)), 0);
    [...String(props.text)].forEach((ch, i) => { const s = el("span", "d", g); s.textContent = ch; tl.fromTo(s, { y: 420, opacity: 0 }, { y: 0, opacity: 1, duration: 0.33, ease: "expo.out" }, at + i * 0.1); });
    return g;
  };

  let vb = 0;
  /**
   * Bold condensed section numbers "1 2 3" (Dd3Uz4Mgbn- hook): Oswald 700, cap height 235 (≈ 330 px) #121313 over grid
   * columns x 190/544/896, glyph tops 276; 4-frame stagger, 40 % grey → ink in 4 f; first one permanently
   * vertically motion-blurred / doubled (SVG filter).
   * @param {{items?, cols?, glyphTop?, capHeight?, stagger?, blurFirst?}} props
   */
  RSX.sectionNumbers = function (container, props = {}, tl, at) {
    const items = props.items || ["1", "2", "3"], cols = props.cols || [190, 544, 896];
    const size = sizeForHeight("Oswald", 700, "1", props.capHeight ?? 235);
    const top = Math.round((props.glyphTop ?? 276) - glyphOffset(`700 ${size}px Oswald`, "1", size));
    const root = el("div", "rsx rsx-nums", container);
    let fid = null;
    if (props.blurFirst !== false) {
      fid = `rsx-vblur-${++vb}`;
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.style.position = "absolute";
      svg.innerHTML = `<filter id="${fid}" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur in="SourceGraphic" stdDeviation="0 9" result="b"/><feOffset in="SourceGraphic" dy="-22" result="o"/><feComponentTransfer in="o" result="o2"><feFuncA type="linear" slope=".42"/></feComponentTransfer><feMerge><feMergeNode in="o2"/><feMergeNode in="b"/></feMerge></filter>`;
      root.appendChild(svg);
    }
    root.items = items.map((t, i) => {
      const n = abs(el("div", "n", root), cols[i], top); n.textContent = t;
      Object.assign(n.style, { fontSize: size + "px", lineHeight: size + "px", height: size + "px" });
      if (i === 0 && fid) n.style.filter = `url(#${fid})`;
      tl.fromTo(n, { opacity: 0, color: "#9A9A9A" }, { opacity: 1, color: "#121313", duration: 4 * F, ease: "power1.out" }, at + i * (props.stagger ?? 0.167));
      return n;
    });
    return root;
  };

  /**
   * Speaker window = grid cell 392×595 at (344, 662), radius 0 (Dd3Uz4Mgbn- intro): unfolds from a 1 px line
   * (width 2 f → height 3 f back.out(1.2)); `collapseAt` implodes to 60×100 in 3 f. Footage via node/src, else slot.
   */
  RSX.window = function (container, props = {}, tl, at) {
    const W = props.w ?? 392, H = props.h ?? 595;
    const win = abs(el("div", "rsx rsx-window", container), props.x ?? 344, props.y ?? 662);
    win.style.width = W + "px"; win.style.height = H + "px";
    RSB.footage(win, { node: props.node, src: props.src, label: props.label || "ваше видео", sub: props.sub || "talking head" });
    tl.fromTo(win, { scaleX: 0.02, scaleY: 0.004 }, { scaleX: 1, duration: 2 * F, ease: "power2.out" }, at);
    ft(tl, win, { scaleY: 0.004 }, { scaleY: 1, duration: 3 * F, ease: "back.out(1.2)" }, at + 2 * F);
    if (props.collapseAt != null) {
      ft(tl, win, { scaleX: 1, scaleY: 1 }, { scaleX: 60 / W, scaleY: 100 / H, duration: 3 * F, ease: "power3.in" }, props.collapseAt);
      ft(tl, win, { opacity: 1 }, { opacity: 0, duration: 0.001 }, props.collapseAt + 3 * F);
    }
    return win;
  };

  /**
   * Green checks list (dark or paper): 790×120 rows (gap 28) rise with their words; ring fills #4AD477 with glow and a
   * white ✓ draws 0.2 s after the last word. @param {{rows:Array<{text?|words?, at, check?}>, dark?, width?, flow?, x?, y?}} props
   */
  RSX.checks = function (container, props, tl, at) {
    const list = el("div", "rsx rsx-checks" + (props.dark ? " dark" : ""), container);
    if (props.width) list.style.width = props.width + "px";
    if (!props.flow) abs(list, props.x ?? Math.round((1080 - (props.width || 790)) / 2), props.y ?? 700); // centred for any width
    list.rows = (props.rows || []).map((r) => {
      const row = el("div", "row", list), c = el("div", "c", row), fb = el("b", null, c);
      c.insertAdjacentHTML("beforeend", CHECK("#fff", 3.6));
      const tx = el("div", "tx", row), ws = words(r.words || r.text, r.at, r.stagger ?? 0.18);
      tl.fromTo(row, { opacity: 0, y: 30, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }, r.at - 0.08);
      karaoke(tx, ws, tl, props.dark ? { from: "#9A9A9A", to: "#FFFFFF" } : { from: "#8A8A8A", to: "#1A1A1A" });
      const ct = r.check ?? ws[ws.length - 1].t + 0.35;
      tl.fromTo(fb, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, ct);
      tl.fromTo(c.querySelector("path"), { strokeDasharray: 24, strokeDashoffset: 24 }, { strokeDashoffset: 0, duration: 0.2, ease: "power2.out" }, ct + 0.08);
      return row;
    });
    return list;
  };

  /** White label pill typed on a phone ("Text" → " hook", Dd3Uz4Mgbn- 12.9 s): 122 px r30 #F3F3F3, 90 px medium. @param {{parts:Array<{text,at}>, y?, cx?, cps?}} props */
  RSX.label = function (container, props, tl, at) {
    // centred with CSS on a full-width row (not from a pre-font offsetWidth measurement, which drifted off-centre)
    const cx = props.cx ?? 540, half = Math.min(cx, 1080 - cx);
    const row = abs(el("div", "rsx", container), cx - half, props.y ?? 934);
    Object.assign(row.style, { width: 2 * half + "px", display: "flex", justifyContent: "center" });
    const p = el("div", "rsx rsx-label", row), spans = [];
    p.style.position = "relative";
    (props.parts || []).forEach((part) => [...part.text].forEach((ch, i) => { const s = el("span", "c", p); s.textContent = ch === " " ? " " : ch; spans.push({ s, t: part.at + i / (props.cps ?? 22) }); }));
    tl.fromTo(p, { opacity: 0, scaleX: 0.6 }, { opacity: 1, scaleX: 1, duration: 0.25, ease: "back.out(1.4)" }, at);
    spans.forEach(({ s, t }) => tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: 0.03, ease: "none" }, t));
    return p;
  };

  /* ================================================================== *
   * TRANSITIONS + AUDIO CUE
   * ================================================================== */
  RSX.tx = {
    /** Hard cut between two layers. */
    cut(tl, outEl, inEl, at) { if (outEl) ft(tl, outEl, { opacity: 1 }, { opacity: 0, duration: 0.001 }, at); if (inEl) ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: 0.001 }, at); },
    /** Pixel glitch 6 frames @24 fps (0.25 s) into the CTA (Dd3Uz4Mgbn- 36.33 s) — RSB.tx.datamosh. */
    glitch(tl, outEl, inEl, at, o = {}) { RSB.tx.datamosh(tl, outEl, inEl, at, Object.assign({ frames: 6, fps: 24, seed: 13 }, o)); },
    /** Blank beat: flat colour for `frames` frames between two layers (Dd3Uz4Mgbn- 5.0 / 19.85 s). */
    blank(tl, outEl, inEl, at, o = {}) {
      const b = el("div", "rsx-blank", o.layer || outEl.parentNode); b.style.background = o.color || "#EFEDEC";
      tl.fromTo(b, { opacity: 0 }, { opacity: 0, duration: 0.001 }, 0);
      ft(tl, b, { opacity: 0 }, { opacity: 1, duration: 0.001 }, at); if (outEl) ft(tl, outEl, { opacity: 1 }, { opacity: 0, duration: 0.001 }, at);
      const t2 = at + (o.frames ?? 2) * F;
      ft(tl, b, { opacity: 1 }, { opacity: 0, duration: 0.001 }, t2); if (inEl) ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: 0.001 }, t2);
      return b;
    },
  };

  /**
   * Voice-muffle gag cue (Dd3Uz4Mgbn- 15.75–18.6 s: voice −11 dB + low-pass while "on mute" is explained). Visual-only
   * compositions cannot filter audio, so this records the cue for the mixer: pushed to `RSX.cues` and written to the
   * container as `data-rsx-muffle="start,end,gain_db,lowpass_hz"` — the director copies it into scenes.json
   * `audio.muffle[]` for scripts/mix.py. Returns the cue object.
   * @param {{start:number, end:number, gain_db?:number, lowpass?:number}} props  (global/final-timeline seconds)
   */
  RSX.cues = [];
  RSX.muffle = function (container, props) {
    const cue = { type: "muffle", start: props.start, end: props.end, gain_db: props.gain_db ?? -11, lowpass: props.lowpass ?? 1200 };
    RSX.cues.push(cue);
    if (container && container.setAttribute) container.setAttribute("data-rsx-muffle", [cue.start, cue.end, cue.gain_db, cue.lowpass].join(","));
    return cue;
  };
})();
