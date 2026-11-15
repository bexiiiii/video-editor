/* reels-studio · Style F "Kinetic Talking Head" — component library (global RSF)
 * Spec: references/style-f.md · measurements: references/teardowns/style-f/tt_7632011473379790097.md
 * Load order: GSAP → lib/runtime.js (RS) → lib/tokens-f.css → lib/f.js. Build inside `await RSF.ready()`
 * (stacks are measured at build time: widths, baselines, x-height), register the timeline last.
 *
 * Model: the client's real talking head (two framings from one camera: wide 1.0 ↔ tight ≈ 1.4, hard cuts) carries
 * small literal captions; on key phrases a KINETIC STACK (huge lowercase words of mixed sizes, one accent colour,
 * interlocking lines) blurs in word by word over the chest; between head segments flat colour inserts (white /
 * salmon) and a tilted full-bleed screen-recording B-roll carry the same stacks + one cut-out object.
 *
 * Contract (references/contracts.md):  RSF.<builder>(container, props, tl, at) → HTMLElement
 *   - absolute LOCAL seconds; seek-safe fromTo / sets only; deterministic; text never exits on its own
 *     (a stack exits only with its clip — hard cut — or through an explicit `exitAt` blur-out).
 *   - layouts: RSF.layout.<id>(clip, spec, tl, at) → layer (`.parts`, `.layout`).
 * People: a human is ALWAYS real footage (`footage.node` = framework <video>, `footage.src` = photo) or, in an
 * assembled run, the head.mp4 clip underneath (`footage.transparent:true`). Otherwise a labelled neutral slot.
 * This library never draws figures or faces; missing objects / screen recordings become labelled slots.
 */
(function () {
  "use strict";
  const RS = window.RS || {};
  const RSF = { version: "1.1.0" };
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  /** Brand palette (scripts/brand.py → lib/brand.js, window.RS_BRAND.palette.f); stock colours when absent. */
  const brand = (k, d) => {
    const p = window.RS_BRAND && window.RS_BRAND.palette && window.RS_BRAND.palette.f;
    return p && p[k] != null ? p[k] : d;
  };
  RSF.el = el;

  /** State-change tween: explicit from/to, never renders before its start (seek-safe). */
  function ft(tl, target, from, to, at) { return tl.fromTo(target, from, Object.assign({ immediateRender: false }, to), at); }
  RSF.ft = ft;

  /* ------------------------------------------------------------------ *
   * Measured constants (teardown §3–§6)
   * ------------------------------------------------------------------ */
  RSF.SIZE = { xxl: 300, xl: 240, l: 160, m: 115, s: 92 }; // role → font px (x-height 163 / 130 / 86 / 62 / 50)
  RSF.FONT = "'RSF Kinetic A', Montserrat";               // Montserrat 800 + single-storey а (tokens.css)
  RSF.M = {
    word: { blur: 16, scale: 1.05, dur: 0.22, ease: "power1.out", lead: 0.04 },   // 5–6 frames, in place
    rise: { blur: 18, y: 400, dur: 0.32, ease: "power3.out", lead: 0.2 },         // hook only
    exit: { blur: 18, dur: 0.28, ease: "power1.in" },                              // in-segment stack swap
    obj: { dur: 0.42, ease: "power3.out", dist: 760 },                             // drop / rise with motion blur
    gap: 0.12,            // baseline → next x-top = gap × previous x-height, capped at gapMax (ref 10–15 px)
    gapMax: 16,
    ascKiss: 3,           // a line with ascenders (б і һ digits ! ?): ascender top = previous baseline + 3 px
    stagger: 0.22,        // default word spacing in time when no word times are given
    capPitch: 52,         // small caption line pitch
    insertGap: 0.2,       // inserts open on an empty colour page for 0.16–0.28 s
    tight: 1.4,           // tight framing (ref 1.25–1.55, median 1.40)
  };
  RSF.STACK_CY = 1255;    // stack centre over the head (band 1050–1460)
  RSF.CAP_TOP = 1300;     // small caption box top
  RSF.COLORS = { white: "#FCFCFC", black: "#000000", yellow: "#FCF900", red: "#FC0000", salmon: "#EEB596" };

  let XH = 0.54;           // x-height / em of the kinetic face, measured in ready()
  /** Wait for the kinetic face (Montserrat 800 + single-storey а) and Oswald incl. Kazakh glyphs, then measure the x-height. */
  RSF.ready = function () {
    const f = document.fonts;
    const sample = "ӘәҒғҚқҢңӨөҰұҮүҺһІі абвгдежзийклмнопрстуфхцчшщъыьэюя a 0123456789";
    const specs = ["700 56px Montserrat", "800 56px Montserrat", "800 165px Montserrat", "800 165px 'RSF Kinetic A'", "700 232px Oswald"];
    const done = () => {
      try {
        const c = document.createElement("canvas").getContext("2d");
        c.font = `800 200px ${RSF.FONT}`;
        const m = c.measureText("x");
        if (m && m.actualBoundingBoxAscent > 50) XH = m.actualBoundingBoxAscent / 200;
      } catch (e) { /* keep default */ }
      RSF.XH = XH;
    };
    if (!f || !f.load) { done(); return Promise.resolve(); }
    return Promise.all(specs.map((s) => f.load(s, sample).catch(() => null))).then(() => f.ready).then(done);
  };

  /* ------------------------------------------------------------------ *
   * Shared entrances
   * ------------------------------------------------------------------ */
  /** Word reveal in place: opacity 0→1, blur 16→0, scale 1.05→1, 0.22 s power1.out, lead 0.04 s. */
  function wordIn(tl, node, t, mode) {
    if (mode === "rise") {
      const m = RSF.M.rise;
      tl.fromTo(node, { opacity: 0, y: m.y, filter: `blur(${m.blur}px)` },
        { opacity: 1, y: 0, filter: "blur(0px)", duration: m.dur, ease: m.ease }, Math.max(0, t - m.lead));
    } else {
      const m = RSF.M.word;
      tl.fromTo(node, { opacity: 0, scale: m.scale, filter: `blur(${m.blur}px)` },
        { opacity: 1, scale: 1, filter: "blur(0px)", duration: m.dur, ease: m.ease }, Math.max(0, t - m.lead));
    }
  }
  RSF.wordIn = wordIn;
  /** Generic blur-in for a block (headline, handle). */
  function enter(tl, node, at, o = {}) {
    tl.fromTo(node, { opacity: 0, filter: `blur(${o.blur ?? 14}px)`, y: o.y ?? 0, scale: o.scale ?? 1.04 },
      { opacity: 1, filter: "blur(0px)", y: 0, scale: 1, duration: o.dur ?? 0.24, ease: o.ease || "power1.out" }, at);
    return node;
  }
  RSF.enter = enter;
  /** In-segment exit: blur 0→18 + fade, 0.28 s power1.in (ref 16.96–17.24). */
  RSF.exit = function (tl, node, at, o = {}) {
    const m = RSF.M.exit;
    ft(tl, node, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: `blur(${o.blur ?? m.blur}px)`, duration: o.dur ?? m.dur, ease: m.ease }, at);
    return node;
  };

  /* ------------------------------------------------------------------ *
   * Layers
   * ------------------------------------------------------------------ */
  /** Full-frame `.rsf` layer. kind: 'head' (white type, soft shadow) | 'insert' | 'broll' | 'cta'. */
  RSF.layer = function (container, props = {}) {
    const L = el("div", "rsf rsf-layer" + (props.cls ? " " + props.cls : ""), container);
    L.kind = props.kind || "head";
    if (L.kind === "head" || L.kind === "broll") L.classList.add("rsf-on-footage");
    return L;
  };
  /** Flat colour insert page: bg 'white' (#FCFCFC) | 'salmon' (#EEB596) | 'black' | any hex. */
  RSF.insert = function (container, props = {}) {
    const bg = props.bg || "white";
    const L = RSF.layer(container, { kind: "insert", cls: "rsf-insert" + (["salmon", "black"].includes(bg) ? " " + bg : "") });
    if (!["white", "salmon", "black"].includes(bg)) L.style.background = bg;
    if (bg === "salmon") L.style.background = brand("salmon", RSF.COLORS.salmon);
    L.theme = bg === "black" ? "dark" : bg === "salmon" ? "salmon" : "light";
    if (L.theme === "dark") L.classList.add("rsf-dark");
    return L;
  };

  const CAMERA = `<svg viewBox="0 0 48 36"><rect x="2" y="7" width="32" height="24" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M34 15l11-6v18l-11-6z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;
  const IMAGE = `<svg viewBox="0 0 48 48"><rect x="4" y="8" width="40" height="32" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="17" cy="20" r="4" fill="currentColor"/><path d="M6 36l12-11 9 8 6-5 11 9" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;

  /**
   * Talking-head base + the "two camera" framing camera. Real footage via `node` (framework-owned <video>, authored
   * statically) or `src` (photo); `transparent:true` in assembled runs (head.mp4 underneath; framings come from
   * edit/cuts.json punch_ins). Otherwise a labelled neutral slot (face box + eye line) that visibly re-frames.
   * framings: [{at, scale (1 = wide, ≈1.4 = tight), origin?:'50% 30%', drift?:0.03, end?}] — hard scale sets on
   * cuts; `drift` adds a slow linear zoom (scale → scale·(1+drift)) until `end` (optional, off in the reference).
   * @param {{node?:HTMLElement, src?:string, transparent?:boolean, label?:string, sub?:string, origin?:string,
   *          framings?:Array<{at:number, scale?:number, origin?:string, drift?:number, end?:number}>, badge?:boolean}} props
   * @returns {HTMLElement} head (`.cam`)
   */
  RSF.footage = function (container, props = {}, tl, at = 0) {
    const head = el("div", "rsf-head" + (props.transparent ? " transparent" : ""), container);
    const cam = el("div", "rsf-cam", head);
    if (props.origin) cam.style.transformOrigin = props.origin;
    let slot = false;
    if (props.node || props.src) {
      const m = props.node || el("img");
      if (!props.node) { m.src = props.src; m.alt = ""; }
      m.classList.add("rsf-media");
      cam.appendChild(m); head.media = m;
    } else if (!props.transparent) {
      slot = true;
      const s = el("div", "rsf-slot", cam);
      el("div", "grid", s);
      el("div", "body", s);
      const face = el("div", "face", s);
      el("div", null, face, CAMERA);
      el("div", "lb", face).textContent = props.label || "ваше видео";
      el("div", "sb", face).textContent = props.sub || "talking head · 9:16";
      const eyes = el("div", "eyes", s);
      el("span", null, eyes).textContent = "линия глаз ≈ 30 %";
      head.slot = s;
    }
    const fr = props.framings && props.framings.length ? props.framings : [{ at, scale: 1 }];
    fr.forEach((f, i) => {
      const sc = f.scale ?? 1;
      tl.set(cam, { scale: sc, transformOrigin: f.origin || props.origin || "50% 30%" }, f.at ?? at);
      if (f.drift) {
        const end = f.end ?? (fr[i + 1] ? fr[i + 1].at : (f.at ?? at) + 3);
        ft(tl, cam, { scale: sc }, { scale: sc * (1 + f.drift), duration: Math.max(0.1, end - (f.at ?? at)), ease: "none" }, f.at ?? at);
      }
    });
    if (slot && props.badge !== false) {
      // framing badge (slot only, not scaled): shows which "camera" the cut lands on
      fr.forEach((f, i) => {
        const sc = f.scale ?? 1;
        const b = el("div", "rsf-badge", head);
        b.innerHTML = `<i></i>${sc > 1.05 ? "крупный план" : "общий план"} · ${sc.toFixed(2).replace(/0$/, "")}×`;
        tl.fromTo(b, { opacity: 0 }, { opacity: 1, duration: 0.06, ease: "none" }, f.at ?? at);
        if (fr[i + 1]) tl.set(b, { opacity: 0 }, fr[i + 1].at);
      });
    }
    head.cam = cam;
    return head;
  };

  /* ------------------------------------------------------------------ *
   * KINETIC STACK
   * ------------------------------------------------------------------ */
  const accentOf = (theme) => (theme === "light" ? "red" : theme === "salmon" ? "black" : "yellow");

  function normLines(lines, at, stagger, theme, accent) {
    let k = 0;
    const defColor = theme === "light" ? "black" : "white";
    return (lines || []).map((ln) => {
      if (typeof ln === "string") ln = { text: ln };
      const role = ln.role || "m";
      const color = ln.color || defColor;
      let words = ln.words;
      if (!words) {
        // `*two words*` marks an accent phrase spanning several tokens
        const toks = String(ln.text || "").split(/\s+/).filter(Boolean);
        let on = false;
        words = toks.map((w, i) => {
          const open = w.startsWith("*"), close = /\*[.,!?…]*$/.test(w);
          const acc = on || open;
          if (open && !close) on = true;
          if (close) on = false;
          const clean = w.replace(/^\*/, "").replace(/\*([.,!?…]*)$/, "$1");
          return { w: acc ? `*${clean}*` : clean, t: ln.at != null ? ln.at + i * (ln.stagger ?? stagger) : null };
        });
      }
      words = words.map((o, j) => {
        if (typeof o === "string") o = { w: o };
        let w = o.w, c = o.color || null;
        const mk = /^\*(.+)\*([.,!?…]*)$/.exec(w);
        if (mk) { w = mk[1] + mk[2]; c = c || ln.accent || accent || accentOf(theme); }
        const t = o.t != null ? o.t : ln.at != null ? ln.at + j * (ln.stagger ?? stagger) : at + k * stagger;
        k++;
        return { w, t, role: o.role || role, color: c || color, size: o.size || ln.size || null };
      });
      return { words, align: ln.align || "left", dx: ln.dx || 0, gap: ln.gap, rot: ln.rot || 0, role };
    });
  }

  /**
   * Kinetic stack (measured on the reference, teardown §4): lines of huge lowercase words with per-word size roles
   * (xxl 300 · xl 240 · l 160 · m 115 · s 92 px; big/small/big contrast: "2-ақ" xl / "вариант" m ≈ 0.48 / "бар!" xl)
   * and colours (white · black · yellow · red · dim; `*word*` = the ONE optional accent: yellow over footage, red on
   * white, black on salmon — most insert stacks are plain black, most footage stacks plain white).
   * Geometry: a LEFT-aligned block (per-line `align` right/center against the widest line and `dx` nudges allowed)
   * whose bounding box is centred on `cx`; lines interlock — next x-top = previous baseline + min(0.12 × previous
   * x-height, 16 px) (ref 10–15 px), and a line with ascenders / digits / ! is lowered only until its ascender top
   * sits 3 px under the previous baseline (ref б of "бар!" kisses "вариант"); descenders of the line above dig into
   * the next line. `rot` tilts one line (deg, about its left baseline; ref "вариант" +3°). Auto-fit to `maxW` 900.
   * Words blur in on their spoken times at their FINAL positions (the block never re-centres while words arrive).
   * @param {{lines: Array<string | {text?:string, words?:Array<{w:string,t?:number,role?:string,color?:string}>,
   *          role?:'xxl'|'xl'|'l'|'m'|'s', color?:string, size?:number, align?:'left'|'right'|'center', dx?:number,
   *          gap?:number, rot?:number, at?:number, stagger?:number, accent?:string}>,
   *          theme?:'dark'|'light'|'salmon', cy?:number, top?:number, bottom?:number, cx?:number, maxW?:number,
   *          enter?:'blur'|'rise', exitAt?:number, keepCase?:boolean, stagger?:number}} props
   *          top = ink top (ascenders incl.), bottom = last baseline, cy = centre of the ink block
   * @returns {HTMLElement} stack with `.metrics {top, xTop, base, bottom, left, right, k, lines[]}` and `.words`
   */
  RSF.stack = function (host, props, tl, at) {
    const theme = props.theme || "dark";
    const st = el("div", "rsf-stack" + (props.keepCase ? " keep-case" : ""), host);
    const lines = normLines(props.lines, at, props.stagger ?? RSF.M.stagger, theme, props.accent);
    const maxW = props.maxW ?? 900;
    const C = Object.assign({}, RSF.COLORS, { yellow: brand("accent", RSF.COLORS.yellow), red: brand("alert", RSF.COLORS.red) });
    const rows = lines.map((ln) => {
      const d = el("div", "rsf-line", st);
      const spans = ln.words.map((o, i) => {
        const s = el("span", `rsf-w ${o.role} ${o.color}`, d);
        s.textContent = o.w + (i < ln.words.length - 1 ? " " : "");
        if (C[o.color]) s.style.color = C[o.color];
        return s;
      });
      const bl = el("i", "bl", d);
      return { ln, d, spans, bl };
    });
    const sizeOf = (o) => o.size || RSF.SIZE[o.role] || RSF.SIZE.m;
    const apply = (k) => rows.forEach((r) => r.ln.words.forEach((o, i) => { r.spans[i].style.fontSize = (sizeOf(o) * k).toFixed(2) + "px"; }));
    // horizontal: relative x of each line against the widest (anchor) line, then centre the bounding box on cx
    const layoutX = (k) => {
      const ws = rows.map((r) => r.d.offsetWidth);
      const Wa = Math.max(1, ...ws);
      const xs = rows.map((r, i) => (r.ln.align === "right" ? Wa - ws[i] : r.ln.align === "center" ? (Wa - ws[i]) / 2 : 0) + r.ln.dx * k);
      const minX = Math.min(...xs), maxX = Math.max(...xs.map((x, i) => x + ws[i]));
      return { ws, xs, minX, W: maxX - minX };
    };
    apply(1);
    let k = 1, X = layoutX(1);
    if (X.W > maxW) { k = maxW / X.W; apply(k); X = layoutX(k); }
    // ink ascent of each line (canvas, same face / size / tracking) → ascender kiss
    const cv = document.createElement("canvas").getContext("2d");
    const inkAsc = (r) => Math.max(...r.ln.words.map((o) => {
      const fs = sizeOf(o) * k;
      cv.font = `800 ${fs}px ${RSF.FONT}`;
      const m = cv.measureText(props.keepCase ? o.w : o.w.toLowerCase());
      return m && m.actualBoundingBoxAscent ? m.actualBoundingBoxAscent : XH * fs;
    }));
    let base = 0, prevXh = 0;
    const meta = rows.map((r, i) => {
      const f = Math.max(...r.ln.words.map((o) => sizeOf(o) * k));
      const xh = XH * f;
      const ascX = Math.max(0, inkAsc(r) - xh);                  // ascender height above the x-height
      const hasAsc = ascX > 0.12 * xh;
      let xTop;
      if (i === 0) xTop = 0;
      else if (r.ln.gap != null) xTop = base + r.ln.gap * k;
      else {
        xTop = base + Math.min(RSF.M.gap * prevXh, RSF.M.gapMax * k);
        if (hasAsc) xTop = Math.max(xTop, base + RSF.M.ascKiss * k + ascX);
      }
      base = xTop + xh; prevXh = xh;
      return { f, xh, ascX, hasAsc, xTop, base, w: X.ws[i], off: r.bl.offsetTop };
    });
    const last = meta[meta.length - 1];
    const top0 = meta[0].hasAsc ? -meta[0].ascX : 0;            // ink top relative to the first x-top
    const inkH = last.base - top0;
    let Y0;                                                       // y of the first line's x-top
    if (props.top != null) Y0 = props.top - top0;
    else if (props.bottom != null) Y0 = props.bottom - last.base;
    else Y0 = (props.cy ?? RSF.STACK_CY) - inkH / 2 - top0;
    const cx = props.cx ?? 540;
    const left0 = Math.round(cx - X.W / 2 - X.minX);
    rows.forEach((r, i) => {
      const m = meta[i];
      r.d.style.left = Math.round(left0 + X.xs[i]) + "px";
      r.d.style.top = Math.round(Y0 + m.base - m.off) + "px";
      if (r.ln.rot) { r.d.style.transformOrigin = `0px ${m.off}px`; r.d.style.transform = `rotate(${r.ln.rot}deg)`; }
      r.spans.forEach((s, j) => wordIn(tl, s, r.ln.words[j].t, props.enter));
    });
    st.words = rows.flatMap((r) => r.spans);
    st.metrics = {
      top: Math.round(Y0 + top0), xTop: Math.round(Y0), base: Math.round(Y0 + last.base),
      bottom: Math.round(Y0 + last.base + 0.2 * last.f), left: Math.round(cx - X.W / 2), right: Math.round(cx + X.W / 2), k: +k.toFixed(3),
      firstAt: Math.min(...lines.flatMap((l) => l.words.map((o) => o.t))),
      lines: meta.map((m, i) => ({ xTop: Math.round(Y0 + m.xTop), base: Math.round(Y0 + m.base), xh: Math.round(m.xh), left: Math.round(left0 + X.xs[i]), w: Math.round(m.w) })),
    };
    if (props.exitAt != null) RSF.exit(tl, st, props.exitAt);
    return st;
  };

  /* ------------------------------------------------------------------ *
   * SMALL CAPTIONS (word-synced phrases, hard on / hard off)
   * ------------------------------------------------------------------ */
  /** Assembler caption track (window.RS_CAPTIONS) — when on, it already draws the style-F captions (scripts/captions.py). */
  RSF.captionsOn = () => !!(window.RS_CAPTIONS && window.RS_CAPTIONS.on);
  /**
   * Small centred literal captions: 1–3 words, Montserrat Alternates 800 56 px white, highlight word yellow, ≤ 2 lines
   * (pitch 52, " / " forces the break, > 20 chars breaks at the middle word), top y 1300. Each phrase is shown whole on
   * its first word (0.06 s) and hard-swapped by the next. Keep phrases out of kinetic-stack windows.
   * With the assembled caption track on, returns an empty hidden element (no duplicate text).
   * @param {{phrases: Array<{text:string, at:number, end:number, hl?:string[]}>, top?:number}} props
   */
  RSF.caption = function (host, props, tl) {
    if (RSF.captionsOn() && !props.force) { const n = el("div", "rsf-caps", host); n.style.display = "none"; return n; }
    const scope = el("div", "rsf rsf-capscope", host);         // tokens are scoped to .rsf
    const box = el("div", "rsf-caps", scope);
    if (props.top != null) box.style.top = props.top + "px";
    const hlC = brand("accent", RSF.COLORS.yellow);
    (props.phrases || []).forEach((p) => {
      const ph = el("div", "rsf-ph", box);
      const hl = new Set((p.hl || []).map((s) => s.toLowerCase()));
      let parts = String(p.text).split(/\s*\/\s*/);
      if (parts.length === 1 && p.text.length > 20) {
        const ws = p.text.split(/\s+/);
        const h = Math.ceil(ws.length / 2);
        parts = [ws.slice(0, h).join(" "), ws.slice(h).join(" ")];
      }
      let acc = false;
      ph.innerHTML = parts.slice(0, 2).map((ln) => `<span class="ln">${ln.split(/\s+/).map((w) => {
        const open = w.startsWith("*"), close = /\*[.,!?…]*$/.test(w);
        const inAcc = acc || open;
        if (open && !close) acc = true;
        if (close) acc = false;
        const word = w.replace(/^\*/, "").replace(/\*([.,!?…]*)$/, "$1");
        const on = inAcc || hl.has(word.replace(/[.,!?…:;«»"]/g, "").toLowerCase());
        return on ? `<span class="hl" style="color:${hlC}">${esc(word)}</span>` : esc(word);
      }).join(" ")}</span>`).join("");
      tl.fromTo(ph, { opacity: 0 }, { opacity: 1, duration: 0.06, ease: "none" }, p.at);
      if (p.end != null) tl.set(ph, { opacity: 0 }, p.end);
    });
    return box;
  };

  /* ------------------------------------------------------------------ *
   * INSERT PIECES: condensed headline, cut-out object, number, screen-recording B-roll, leak, end card
   * ------------------------------------------------------------------ */
  /** Condensed caps headline ("2-ВАРИАНТ"): Oswald 700 232 px (cap ≈ 183), black, centred, top y (default 500). */
  RSF.headline = function (host, props, tl, at) {
    const h = el("div", "rsf-cond", host);
    h.textContent = props.text;
    h.style.top = (props.top ?? 500) + "px";
    if (props.size) h.style.fontSize = props.size + "px";
    if (props.color) h.style.color = RSF.COLORS[props.color] || props.color;
    // shrink to the 900 px column
    const w = h.scrollWidth;
    if (w > 900) h.style.fontSize = ((props.size || 232) * 900 / w).toFixed(1) + "px";
    enter(tl, h, props.at ?? at);
    return h;
  };

  /**
   * Cut-out object: a real glossy 3D render / product shot / logo as a transparent PNG (`src`, from reels-art:
   * "glossy photoreal 3D <object>, studio light, white seamless background, soft shadow" → cut out) with a soft
   * contact shadow under it on inserts (ref capsules); drops from the top or rises from the bottom with motion blur
   * (0.42 s power3.out), or blurs in. `circle:true` = white circle mask (ref money circle 459 px); `bw:true` = b/w photo
   * cut-out; `rotate` tilts the object (deg, ref capsules ±6°); `shadow:false` drops the contact shadow.
   * Without src/node → labelled slot (never a drawn person).
   * @param {{src?:string, node?:HTMLElement, label?:string, sub?:string, w?:number, h?:number, x?:number, y?:number,
   *          circle?:boolean, bw?:boolean, rotate?:number, shadow?:boolean, from?:'top'|'bottom'|'blur', dist?:number,
   *          at?:number}} props  x/y = centre
   */
  RSF.object = function (host, props, tl, at) {
    const w = props.w ?? 420, h = props.h ?? w;
    const o = el("div", "rsf-obj" + (props.circle ? " circle" : "") + (props.bw ? " bw" : ""), host);
    Object.assign(o.style, { left: Math.round((props.x ?? 540) - w / 2) + "px", top: Math.round((props.y ?? 760) - h / 2) + "px", width: w + "px", height: h + "px" });
    const real = !!(props.src || props.node);
    if (real && props.shadow !== false && !props.circle) el("div", "shadow", o);
    const inner = el("div", "in", o);
    if (props.rotate) inner.style.transform = `rotate(${props.rotate}deg)`;
    if (real) {
      const m = props.node || el("img");
      if (!props.node) { m.src = props.src; m.alt = ""; }
      inner.appendChild(m);
    } else {
      const s = el("div", "rsf-objslot", inner);
      el("div", null, s, IMAGE);
      el("div", "lb", s).textContent = props.label || "объект";
      el("div", "sb", s).textContent = props.sub || "PNG без фона";
    }
    const t = props.at ?? at, m = RSF.M.obj, from = props.from || "top";
    if (from === "blur") {
      const r = props.rotate || 0;
      tl.fromTo(inner, { opacity: 0, scale: 1.08, rotation: r, filter: "blur(16px)" }, { opacity: 1, scale: 1, rotation: r, filter: "blur(0px)", duration: 0.28, ease: "power1.out" }, t);
    } else {
      const d = (props.dist ?? m.dist) * (from === "top" ? -1 : 1);
      tl.fromTo(o, { y: d, opacity: 0 }, { y: 0, opacity: 1, duration: m.dur, ease: m.ease }, t);
      if (RS.motionBlur) RS.motionBlur(tl, inner, t, m.dur, "y", 26);
    }
    return o;
  };

  /**
   * Full-bleed B-roll, rotated ≈ −10° with mild perspective (rotateX 8°), darkened ≈ 20 %, slow motion. Three sources:
   *  - `node` = the produced clip as a framework-owned <video> (scripts/broll.py → broll/<scene>.mp4, 1080×1920,
   *    muted; author it statically with its own data-start/data-duration at the ROOT, never inside a timed wrapper):
   *    the clip already scrolls, so the plane only drifts (`scroll` default 22 px/s) and zooms 1 → 1.06 (`zoom`);
   *    plane scale default 1.8 (ref: one listing card fills the width — a desktop-layout capture needs it),
   *  - `src` = a long page screenshot (image): scrolls up at `scroll` px/s (default 60);
   *  - nothing → labelled slot (scrolling fake listing).
   * @param {{node?:HTMLElement, src?:string, label?:string, rotate?:number, tiltX?:number, scale?:number, dim?:number,
   *          scroll?:number, zoom?:number, dur?:number}} props
   */
  RSF.broll = function (host, props, tl, at) {
    const isClip = !!(props.node && props.node.tagName === "VIDEO") || /\.(mp4|webm|mov)(\?|$)/i.test(props.src || "");
    const b = el("div", "rsf-broll" + (isClip ? " clip" : ""), host);
    const plane = el("div", "plane", b);
    plane.style.transform = `rotateX(${props.tiltX ?? 8}deg) rotate(${props.rotate ?? -10}deg) scale(${props.scale ?? (isClip ? 1.8 : 1.25)})`;
    const page = el("div", "page", plane);
    if (props.node || props.src) {
      const m = props.node || el(isClip ? "video" : "img");
      if (!props.node) { m.src = props.src; if (isClip) { m.muted = true; m.playsInline = true; } else m.alt = ""; }
      m.classList.add("rsf-media");
      page.appendChild(m);
    } else {
      const s = el("div", "rsf-brslot", page);
      el("div", "tag", s, `${IMAGE.replace("<svg", '<svg width="34" height="34"')}<span>${esc(props.label || "запись экрана")}</span>`);
      for (let i = 0; i < 9; i++) el("div", "row", s, `<div class="ph"></div><div class="tx"><b></b><i></i><i style="width:${70 - (i % 3) * 12}%"></i><u></u></div>`);
    }
    const shade = el("div", "shade", b);
    shade.style.opacity = props.dim ?? 0.2;
    if (!props.node && !props.src) {   // keep the slot labelled while the page scrolls away
      const bd = el("div", "rsf-badge", b);
      bd.innerHTML = `<i></i>${esc(props.label || "запись экрана")} · слот`;
    }
    const dur = props.dur ?? 2.5;
    const sp = props.scroll ?? (isClip ? 22 : 60);
    tl.fromTo(page, { y: 0, scale: 1 }, { y: -sp * dur, scale: isClip ? (props.zoom ?? 1.06) : 1, duration: dur, ease: "none" }, at);
    tl.fromTo(plane, { filter: "blur(8px)" }, { filter: "blur(0px)", duration: 0.25, ease: "power1.out" }, at);
    return b;
  };

  /** Light-leak flash over a cut: 3 frames of orange/white burn (ref 56.20–56.32). Put it on the top layer. */
  RSF.leak = function (host, tl, at) {
    const l = el("div", "rsf-leak", host);
    tl.fromTo(l, { opacity: 0, scale: 0.8, x: -80 }, { opacity: 0.95, scale: 1.1, x: 0, duration: 0.06, ease: "power1.in" }, at - 0.04);
    ft(tl, l, { opacity: 0.95 }, { opacity: 0, scale: 1.3, x: 120, duration: 0.14, ease: "power1.out" }, at + 0.06);
    return l;
  };

  const CHEV = `<svg viewBox="0 0 248 295"><path d="M30 34 L124 124 L218 34" fill="none" stroke="currentColor" stroke-width="44" stroke-linecap="square"/><path d="M30 164 L124 254 L218 164" fill="none" stroke="currentColor" stroke-width="44" stroke-linecap="square"/></svg>`;
  /**
   * End card: black page, white double chevron ↓ (248×295), 2-line "link below" stack (white + one yellow word), optional handle.
   * Identity (handle) comes from the brief only.
   * @param {{lines?:Array, handle?:string, at?:number}} props  lines = RSF.stack lines (default kk "төмендегі / *сілтемеге* өтіңіз")
   */
  RSF.cta = function (host, props, tl, at) {
    const c = el("div", "rsf-cta", host);
    const ch = el("div", "rsf-chev", c, CHEV);
    ch.style.top = "583px";                                      // ref chevron 248×295 at y 583–877, white
    tl.fromTo(ch, { opacity: 0, y: -60, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }, at + 0.1);
    const lines = props.lines || [{ text: "төмендегі", size: 78, at: at + 0.3 }, { words: [{ w: "*сілтемеге*", size: 78 }, { w: "өтіңіз", size: 78 }], at: at + 0.5 }];
    c.stack = RSF.stack(c, { lines, theme: "dark", top: 1130 }, tl, at + 0.3);
    if (props.handle) {
      const hd = el("div", "rsf-handle", c);
      hd.textContent = props.handle;
      hd.style.top = (c.stack.metrics.bottom + 46) + "px";
      enter(tl, hd, at + 0.8);
    }
    return c;
  };

  /* ------------------------------------------------------------------ *
   * TRANSITIONS — F is a hard-cut style
   * ------------------------------------------------------------------ */
  RSF.tx = {
    /** Hard cut: nothing to draw — adjacent clips. Kept for API symmetry. */
    cut() {},
    /** In-segment stack swap: blur-out the old stack; the next one starts ≥ 0.25 s later. Returns next start. */
    swap(tl, outEl, at) { RSF.exit(tl, outEl, at); return at + RSF.M.exit.dur + 0.25; },
    leak: (tl, host, at) => RSF.leak(host, tl, at),
  };

  /* ------------------------------------------------------------------ *
   * LAYOUTS — RSF.layout.<id>(clip, spec, tl, at) → layer with `.parts`
   * ------------------------------------------------------------------ */
  const layout = (RSF.layout = {});
  const stacksOf = (spec) => (spec.stacks || (spec.stack ? [spec.stack] : []));

  /**
   * `head` — full-frame talking head with framings; small captions only (they come from the caption track).
   * @param {{footage?:object, caption?:object}} spec  caption = RSF.caption props (demo / no assembler track)
   */
  layout.head = function (clip, spec, tl, at) {
    const L = RSF.layer(clip, { kind: "head" });
    const parts = { head: RSF.footage(L, spec.footage || {}, tl, at) };
    if (spec.caption) parts.caption = RSF.caption(L, spec.caption, tl);
    L.parts = parts; L.layout = "head";
    return L;
  };

  /**
   * `head-side` — kinetic stack(s) over the head, centred on the chest (cy 1255, band 1050–1460), never over the face.
   * Several stacks in one segment: give each an `exitAt` (blur-out) before the next starts.
   * @param {{footage?:object, stack?:object, stacks?:object[]}} spec  stack = RSF.stack props (+ `at`)
   */
  layout.headSide = layout["head-side"] = function (clip, spec, tl, at) {
    const L = layout.head(clip, { footage: spec.footage, caption: spec.caption }, tl, at);
    L.parts.stacks = stacksOf(spec).map((s) => RSF.stack(L, Object.assign({ theme: "dark" }, s), tl, s.at ?? at + 0.1));
    L.layout = "head-side";
    return L;
  };

  /**
   * `insert-statement` — flat colour page + optional condensed headline (top 500) + one big stack (centre 960, or
   * under the headline). Opens empty for 0.2 s.
   * @param {{bg?:string, headline?:{text,at?,top?}, stack:object}} spec
   */
  layout.insertStatement = layout["insert-statement"] = function (clip, spec, tl, at) {
    const L = RSF.insert(clip, { bg: spec.bg || "white" });
    const parts = {};
    if (spec.headline) parts.headline = RSF.headline(L, spec.headline, tl, spec.headline.at ?? at + RSF.M.insertGap);
    const s = spec.stack;
    const pos = parts.headline ? { top: (spec.headline.top ?? 500) + 330 } : { cy: 960 };
    parts.stack = RSF.stack(L, Object.assign({ theme: L.theme }, pos, s), tl, s.at ?? at + RSF.M.insertGap);
    L.parts = parts; L.layout = "insert-statement";
    return L;
  };

  /**
   * `insert-object` — flat colour page + cut-out object(s) (drop / rise) sitting DIRECTLY on the stack under it
   * (+ optional stack above). Ref 2.6 s: capsules y 648–890 (≈ 240 px tall, ≈ 0.45 × stack height), stack ink
   * 889–1382, object bottom = stack ink top − `gap` (default 0; the contact shadow tucks behind the first line),
   * whole block centred on y ≈ 1015 (`cy`). `objects:[…]` places several objects side by side (ref: red + blue pill,
   * x centres ±115 px from the block centre). object.x/y override the automatic placement.
   * @param {{bg?:string, object?:object, objects?:object[], stack:object, above?:object, cy?:number, gap?:number}} spec
   */
  layout.insertObject = layout["insert-object"] = function (clip, spec, tl, at) {
    const L = RSF.insert(clip, { bg: spec.bg || "white" });
    const parts = {};
    const obs = (spec.objects || [spec.object]).map((o) => Object.assign({ w: 420 }, o));
    const oh = Math.max(...obs.map((o) => o.h ?? o.w));
    const t0 = at + RSF.M.insertGap;
    // build the stack first (hidden measuring pass is the real one: positions are final, words reveal on time)
    const gap = spec.gap ?? 0;
    parts.stack = RSF.stack(L, Object.assign({ theme: L.theme, top: 0 }, spec.stack), tl, spec.stack.at ?? t0 + 0.25);
    const sm = parts.stack.metrics;
    const stackH = sm.base - sm.top;
    const blockH = oh + gap + stackH;
    const top = obs[0].y != null ? obs[0].y - oh / 2 : Math.round((spec.cy ?? 1015) - blockH / 2);
    const dy = top + oh + gap - sm.top;
    parts.stack.querySelectorAll(".rsf-line").forEach((d) => { d.style.top = (parseFloat(d.style.top) + dy) + "px"; });
    ["top", "xTop", "base", "bottom"].forEach((k) => { sm[k] += dy; });
    sm.lines.forEach((l) => { l.xTop += dy; l.base += dy; });
    const cxs = obs.length === 1 ? [540] : obs.map((o, i) => 540 + (i - (obs.length - 1) / 2) * (o.spread ?? 230));
    parts.objects = obs.map((o, i) => RSF.object(L, Object.assign({ x: cxs[i] }, o, { y: o.y ?? top + oh - (o.h ?? o.w) / 2 }), tl, o.at ?? t0 + 0.08 + i * 0.06));
    parts.object = parts.objects[0];
    if (spec.above) parts.above = RSF.stack(L, Object.assign({ theme: L.theme, bottom: top - 40 }, spec.above), tl, spec.above.at ?? t0);
    L.parts = parts; L.layout = "insert-object";
    return L;
  };

  /**
   * `media` — tilted full-bleed B-roll + kinetic stack (white, ≤ 1 yellow word) centred on y 960. `broll.node` = the
   * scripts/broll.py clip as a root-level <video> (see RSF.broll); without it the labelled slot.
   * @param {{broll:object, stack:object}} spec
   */
  layout.media = function (clip, spec, tl, at) {
    const L = RSF.layer(clip, { kind: "broll" });
    const parts = { broll: RSF.broll(L, spec.broll || {}, tl, at) };
    parts.stack = RSF.stack(L, Object.assign({ theme: "dark", cy: 960 }, spec.stack), tl, spec.stack.at ?? at + 0.15);
    L.parts = parts; L.layout = "media";
    return L;
  };

  /**
   * `number` — colour page: small label + big number (keep case, digits) at the top, optional b/w cut-out rising over
   * the number, stack under it (ref "остаток / 2 000 000" + person + "мойнына қарыз").
   * @param {{bg?:string, label?:string, value:string, at?:number, valueAt?:number, object?:object, stack?:object, top?:number}} spec
   */
  layout.number = function (clip, spec, tl, at) {
    const L = RSF.insert(clip, { bg: spec.bg || "white" });
    const t0 = spec.at ?? at + RSF.M.insertGap;
    const lines = [];
    if (spec.label) lines.push({ text: spec.label, size: 64, at: t0 });
    lines.push({ words: [{ w: spec.value, t: spec.valueAt ?? t0 + 0.25 }], size: spec.size || 170 });
    const parts = {};
    parts.number = RSF.stack(L, { lines, theme: L.theme, top: spec.top ?? 560, keepCase: true }, tl, t0);
    let y = parts.number.metrics.bottom;
    if (spec.object) {
      const ob = Object.assign({ w: 520, from: "bottom" }, spec.object);
      const oh = ob.h ?? ob.w;
      parts.object = RSF.object(L, Object.assign({}, ob, { y: y - 30 + oh / 2 }), tl, ob.at ?? t0 + 0.35);
      y = y - 30 + oh;
    }
    if (spec.stack) parts.stack = RSF.stack(L, Object.assign({ theme: L.theme, top: y + 50 }, spec.stack), tl, spec.stack.at ?? t0 + 0.7);
    L.parts = parts; L.layout = "number";
    return L;
  };

  /**
   * `list` — colour page: condensed headline + 2–4 numbered kinetic lines (index digit in the accent colour + words),
   * each on its spoken time, left-aligned block.
   * @param {{bg?:string, headline?:{text,at?}, items:Array<{n?:string, text:string, at:number, role?:string}>}} spec
   */
  layout.list = function (clip, spec, tl, at) {
    const L = RSF.insert(clip, { bg: spec.bg || "white" });
    const parts = {};
    const top = spec.headline ? (spec.top ?? 600) : (spec.top ?? 760);
    if (spec.headline) parts.headline = RSF.headline(L, Object.assign({ top }, spec.headline), tl, spec.headline.at ?? at + RSF.M.insertGap);
    const acc = L.theme === "light" ? "red" : accentOf(L.theme);
    const lines = spec.items.map((it, i) => ({
      align: "left",
      words: [{ w: it.n || String(i + 1), t: it.at, role: "l", color: acc }].concat(
        it.text.split(/\s+/).map((w, j) => ({ w, t: it.at + 0.1 + j * 0.12, role: it.role || (i % 2 ? "m" : "l") }))),
    }));
    parts.list = RSF.stack(L, { lines, theme: L.theme, top: top + (spec.headline ? 330 : 0) }, tl, at);
    L.parts = parts; L.layout = "list";
    return L;
  };

  /** `cta` — black end card (chevrons + "link below" stack + optional handle from the brief). */
  layout.cta = function (clip, spec, tl, at) {
    const L = RSF.layer(clip, { kind: "cta" });
    L.parts = { cta: RSF.cta(L, spec, tl, at) };
    L.layout = "cta";
    return L;
  };

  /** Debug: metrics of every stack inside a layer (for snapshot checks). */
  RSF.audit = function (root) {
    return [...(root || document).querySelectorAll(".rsf-stack")].map((s) => s.metrics);
  };

  window.RSF = RSF;
})();
