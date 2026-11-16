/* reels-studio · Style G "Editorial Selfie" — component library (global RSG)
 * Spec: references/style-g.md · measurements: references/teardowns/style-g/DekIQiwIrSz.md
 * Load order: GSAP → lib/runtime.js (RS) → lib/tokens-g.css → lib/g.js. Build inside `await RSG.ready()` (fonts incl.
 * Kazakh glyphs; stacks are measured at build time: line widths, baselines, x-heights), register the timeline last.
 *
 * Model: the client's real phone-selfie talking head, almost uncut, carries EDITORIAL CAPTION STACKS on the chest:
 * small lead words on top, ONE big emphasis word below (fitted to ≈ 620 px), each emphasis wearing a semantic
 * TREATMENT (bold-yellow value · glow-pink devotion/giving · serif-pink/grey reflection · red warning · bold-white
 * duty · glow-yellow neon on scenes · serif-gold honour title · navy on the mint page · condensed extra). Lines
 * interlock (lead baseline → emphasis x-top ≈ 6 px; tucked words sit on the emphasis baseline, spread to its edges).
 * Inserts (front-loaded): pale mint kinetic page with navy stacks · cinematic generated scene (image/video) with a
 * huge translucent number/word behind the emphasis · white page with CLIENT-SUPPLIED calligraphy.
 *
 * Contract (references/contracts.md):  RSG.<builder>(container, props, tl, at) → HTMLElement
 *   - absolute LOCAL seconds; seek-safe fromTo / sets only; deterministic; text never exits on its own
 *     (a stack disappears by a hard swap at `until`, or with its clip — hard cut).
 *   - layouts: RSG.layout.<id>(clip, spec, tl, at) → layer (`.parts`, `.layout`).
 *   - RSG.captionTrack(container, plan, tl) renders the assembler's caption plan (scripts/captions.py, style "g").
 * People: a human is ALWAYS real footage (`footage.node` = framework <video>, `footage.src` = photo) or, in an
 * assembled run, head.mp4 underneath (`footage.transparent:true`). Otherwise a labelled neutral slot. Generated
 * scenes are abstract / light / silhouettes only — this library never draws figures or faces, and calligraphy is
 * shown only from a client-supplied image (never generated type for holy names).
 */
(function () {
  "use strict";
  const RS = window.RS || {};
  const RSG = { version: "1.0.0" };
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  RSG.el = el;
  /** State-change tween: explicit from/to, never renders before its start (seek-safe). */
  function ft(tl, target, from, to, at) { return tl.fromTo(target, from, Object.assign({ immediateRender: false }, to), at); }
  RSG.ft = ft;

  /* ------------------------------------------------------------------ *
   * Measured constants (teardown §3–§5)
   * ------------------------------------------------------------------ */
  /** Size roles (font px, Inter Tight, x-height 0.546): lead/small 80 (x-height 44), statement M 125 (68),
   *  emphasis L 200 (109) · XL 288 (157) for words of ≤ 4 letters ("слов"). */
  RSG.SIZE = { s: 80, m: 125, l: 200, xl: 288 };
  /** Emphasis fit (ref widths 500–740): words keep their x-height; a word wider than maxW is SQUEEZED horizontally
   *  (CapCut-style box fit, ref "всевышнему" ≈ 0.69×) down to minScale, then shrunk. */
  RSG.FIT = { maxW: 700, minScale: 0.68, xlChars: 4, serifSize: 200 };
  RSG.TREATMENTS = ["bold-yellow", "glow-yellow", "glow-pink", "serif-pink", "serif-grey", "serif-gold", "red",
    "bold-white", "navy", "condensed", "ink"];
  RSG.M = {
    fade: 0.1,            // opacity 0→1 in 3 frames
    blur: 5,              // faint blur on the first frame
    rise: { lead: 6, emph: 24, m: 10, tuck: 6, title: 0 },  // px, settles over `settle`
    settle: 0.3,          // rise ease power2.out
    glide: 0.3,           // block re-centring when a line is added below
    stagger: 0.2,         // default per-word spacing when no word times are given
    gap: { "lead>emph": 6, "emph>tuck": -4, "lead>lead": 31, "m>m": 4, "tuck>emph": 4, "emph>lead": 10, "title>lead": -6,
      "lead>title": 6, "emph>emph": 4, "m>emph": 6, "lead>m": 8, def: 6 },   // baseline(prev) → x-top(next), px
    flicker: 6,           // glow-yellow: frames of on/off before it holds
    backdropOpacity: 1,   // backdrop colour already carries .42 alpha
  };
  RSG.BAND_CY = 1335;     // emphasis band centre over the chest
  RSG.CX = 520;           // stack centre x
  RSG.INSERT_CY = 960;    // stacks on inserts / scenes (no chest to sit on)
  RSG.COLORS = { white: "#FBF9FE", lead: "#FFFAF6", value: "#F9E376", neon: "#F4FF15", pink: "#FAE0F9", serifPink: "#F0D8F2",
    gold: "#F8E377", red: "#D9031D", navy: "#0B297E", mint: "#C3E0DE", paper: "#FBF9FC", ink: "#020003" };
  /** Vertical metrics per family at line-height 1 (fractions of the font size), refined in ready(). */
  RSG.MET = {
    sans: { base: 0.86, xh: 0.546 },     // baseline from the line-box top; x-height
    serif: { base: 0.89, xh: 0.50 },
    cond: { base: 0.86, xh: 0.53 },
  };
  const familyOf = (treat) => (/^serif/.test(treat || "") ? "serif" : treat === "condensed" ? "cond" : "sans");

  /** Wait for the faces (incl. Kazakh glyphs) and measure baseline / x-height of each family. */
  RSG.ready = function () {
    const f = document.fonts;
    const sample = "ӘәҒғҚқҢңӨөҰұҮүҺһІі абвгдежзийклмнопрстуфхцчшщъыьэюя АБВГ aoʻgʻ 0123456789 %";
    const specs = ["700 86px 'Inter Tight'", "700 200px 'Inter Tight'", "500 40px 'Inter Tight'", "700 100px Arimo",
      "500 200px 'Noto Serif Display'", "800 200px 'Roboto Condensed'"];
    const fams = { sans: "700 200px 'Inter Tight', Arimo, sans-serif", serif: "500 200px 'Noto Serif Display', serif",
      cond: "800 200px 'Roboto Condensed', sans-serif" };
    const done = () => {
      try {
        const c = document.createElement("canvas").getContext("2d");
        Object.keys(fams).forEach((k) => {
          c.font = fams[k];
          const mx = c.measureText("н"), mh = c.measureText("Hxgу");
          const fa = mh.fontBoundingBoxAscent, fd = mh.fontBoundingBoxDescent;
          if (fa > 50 && fd > 0 && mx.actualBoundingBoxAscent > 40) {
            RSG.MET[k] = { base: ((200 - fa - fd) / 2 + fa) / 200, xh: mx.actualBoundingBoxAscent / 200 };
          }
        });
      } catch (e) { /* keep defaults */ }
    };
    if (!f || !f.load) { done(); return Promise.resolve(); }
    return Promise.all(specs.map((s) => f.load(s, sample).catch(() => null))).then(() => f.ready).then(done);
  };

  /* ------------------------------------------------------------------ *
   * Word reveal
   * ------------------------------------------------------------------ */
  /** opacity 0→1 in 3 frames + faint blur, rise `dy` px settling over 0.3 s; starts ON the spoken onset (never early). */
  function wordIn(tl, node, t, dy, o = {}) {
    const m = RSG.M;
    const at = Math.max(0, t);
    tl.fromTo(node, { opacity: 0, filter: `blur(${o.blur ?? m.blur}px)` }, { opacity: 1, filter: "blur(0px)", duration: m.fade, ease: "none" }, at);
    if (dy) tl.fromTo(node, { y: dy }, { y: 0, duration: m.settle, ease: "power2.out", immediateRender: true }, at);
    if (o.flicker) {
      for (let i = 1; i <= RSG.M.flicker; i++) tl.set(node, { opacity: i % 2 ? 0.12 : 1 }, at + m.fade + i / 30);
      tl.set(node, { opacity: 1 }, at + m.fade + (RSG.M.flicker + 1) / 30);
    }
  }
  RSG.wordIn = wordIn;
  /** Generic soft entrance for a block (scene media, calligraphy, backdrop). */
  RSG.enter = function (tl, node, at, o = {}) {
    tl.fromTo(node, { opacity: 0, scale: o.scale ?? 1 }, { opacity: o.to ?? 1, scale: 1, duration: o.dur ?? 0.14, ease: o.ease || "power1.out" }, at);
    return node;
  };

  /* ------------------------------------------------------------------ *
   * Layers
   * ------------------------------------------------------------------ */
  /** Full-frame `.rsg` layer. kind: 'head' | 'mint' | 'paper' | 'scene' | 'dark'. */
  RSG.layer = function (container, props = {}) {
    const k = props.kind || "head";
    const L = el("div", "rsg rsg-layer" + (k === "mint" ? " rsg-insert mint rsg-on-mint" : k === "paper" ? " rsg-insert rsg-on-paper"
      : k === "dark" ? " rsg-insert dark" : "") + (props.cls ? " " + props.cls : ""), container);
    L.kind = k;
    return L;
  };
  /** Insert page: bg 'mint' (radial, vignette) | 'paper' (white #FBF9FC) | 'dark'. */
  RSG.insert = function (container, props = {}) { return RSG.layer(container, { kind: props.bg || "mint" }); };

  /** 1-frame white flash (ref head → mint at 1.033 s). Put it on the INCOMING clip at its first frame. */
  RSG.flash = function (container, props = {}, tl, at = 0) {
    const f = el("div", "rsg-flash", container);
    tl.set(f, { opacity: 1 }, at);
    tl.set(f, { opacity: 0 }, at + (props.frames ?? 1) / 30);
    return f;
  };

  const CAMERA = `<svg viewBox="0 0 48 36"><rect x="2" y="7" width="32" height="24" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M34 15l11-6v18l-11-6z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;

  /**
   * Talking-head base (phone selfie, one take). Real footage via `node` (framework-owned <video>, authored statically)
   * or `src` (photo); `transparent:true` in assembled runs (head.mp4 underneath). Otherwise a labelled neutral slot
   * (face box + eye line at 40 %). No framings: the reference never cuts or zooms the head.
   * @param {{node?:HTMLElement, src?:string, transparent?:boolean, label?:string, sub?:string}} props
   */
  RSG.footage = function (container, props = {}) {
    const head = el("div", "rsg-head" + (props.transparent ? " transparent" : ""), container);
    if (props.node || props.src) {
      const m = props.node || el("img");
      if (!props.node) { m.src = props.src; m.alt = ""; }
      m.classList.add("rsg-media");
      head.appendChild(m); head.media = m;
    } else if (!props.transparent) {
      const s = el("div", "rsg-slot", head);
      const face = el("div", "face", s);
      el("div", null, face, CAMERA);
      el("div", "lb", face).textContent = props.label || "ваше видео";
      el("div", "sb", face).textContent = props.sub || "селфи · 9:16 · один дубль";
      const eyes = el("div", "eyes", s);
      el("span", null, eyes).textContent = "линия глаз ≈ 40 %";
      head.slot = s;
    }
    return head;
  };

  /* ------------------------------------------------------------------ *
   * EDITORIAL STACK
   * ------------------------------------------------------------------ */
  const ROLE_CLS = { lead: "lead", small: "small", m: "m", emph: "emph", tuck: "lead", title: "emph" };
  function measureWidth(container, cls, text, size, treat) {
    const probe = el("div", "rsg-line " + cls + (treat ? " rsg-t-" + treat : ""), container);
    probe.style.cssText = `position:absolute;left:-9999px;top:0;visibility:hidden;font-size:${size}px`;
    probe.textContent = text;
    const w = probe.getBoundingClientRect().width;
    probe.remove();
    return w;
  }
  /** Emphasis size + horizontal squeeze: L 200 (XL 288 for ≤ 4 letters; serif 190), squeezed to ≤ FIT.maxW. */
  RSG.fitSize = function (container, text, treat, o = {}) {
    const serif = familyOf(treat) === "serif";
    const letters = text.replace(/[^\p{L}\p{N}]/gu, "").length;
    let size = o.size ?? (serif ? RSG.FIT.serifSize : letters <= RSG.FIT.xlChars ? RSG.SIZE.xl : RSG.SIZE.l);
    const maxW = o.maxW ?? RSG.FIT.maxW;
    const w = (measureWidth(container, "emph", text, 100, treat) || letters * 55) * size / 100;
    let scale = 1;
    if (w > maxW) {
      scale = Math.max(RSG.FIT.minScale, maxW / w);
      if (w * scale > maxW) size = Math.floor(size * maxW / (w * scale));
    }
    return { size, scale: Math.round(scale * 1000) / 1000 };
  };

  function normWords(line, k) {
    if (Array.isArray(line.words)) return line.words.map((w, i) => (typeof w === "string" ? { w, at: (line.at ?? 0) + i * (line.stagger ?? RSG.M.stagger) } : w));
    const parts = String(line.text || "").split(/\s+/).filter(Boolean);
    const st = line.stagger ?? (line.role === "emph" || line.role === "title" ? 0.12 : RSG.M.stagger);
    return parts.map((w, i) => ({ w, at: (line.at ?? 0) + i * st }));
  }

  /**
   * Editorial caption stack: small lead words + ONE emphasis word (treatment) + optional tucked/spread words.
   * lines: [{ role:'lead'|'small'|'m'|'emph'|'tuck'|'title', text | words:[{w,at}], at, stagger?, treat?,
   *           align:'left'|'center'|'right'|'spread' (default lead 'left' when above an emph, else 'center'),
   *           size?, dx?, gap? (baseline(prev) → x-top(this) px), bullet?, keepCase? }]
   * Layout: one block, lines absolutely placed, block centred on (cx, cy) in its FINAL state; while lines arrive the
   * block glides so the visible lines stay centred (0.3 s power2.out). Words reveal on their times (never early).
   * @param {{lines:Array<Object>, cx?:number, cy?:number, until?:number, glide?:boolean, maxW?:number}} props
   * @returns {HTMLElement} block (`.lines`, `.metrics`)
   */
  RSG.stack = function (container, props = {}, tl, at = 0) {
    const block = el("div", "rsg-stack", container);
    const cx = props.cx ?? RSG.CX, cy = props.cy ?? RSG.BAND_CY;
    const specs = (props.lines || []).map((l, k) => Object.assign({ at }, l, { role: l.role || "lead" }));
    const emphIdx = specs.findIndex((l) => l.role === "emph" || l.role === "title");
    const built = specs.map((l, k) => {
      const words = normWords(l, k);
      const treat = l.treat || (l.role === "emph" ? "bold-white" : l.role === "title" ? "serif-gold" : null);
      let size = l.size, sx = 1;
      if (l.role === "emph" || l.role === "title") {
        const f = RSG.fitSize(container, words.map((w) => w.w).join(" "), treat, Object.assign({ size: l.size }, l.fit || {}));
        size = f.size; sx = f.scale;
      } else if (!size) size = l.role === "m" ? RSG.SIZE.m : RSG.SIZE.s;
      const node = el("div", "rsg-line " + ROLE_CLS[l.role] + (treat && (l.role === "emph" || l.role === "title") ? " rsg-t-" + treat : "")
        + (l.keepCase || l.role === "title" ? " keepcase" : ""), block);
      node.style.fontSize = size + "px";
      if (l.color) node.style.color = l.color;
      if (l.bullet) el("span", "rsg-bullet", node);
      const spans = words.map((w, i) => {
        const s = el("span", "w", node);
        s.textContent = w.w;
        if (i < words.length - 1 && l.align !== "spread") s.style.marginRight = "0.14em";   // ref word spaces are tight (≈ 0.12–0.15 em)
        return s;
      });
      const fam = familyOf(l.role === "emph" || l.role === "title" ? treat : null);
      if (sx !== 1) { node.style.transform = `scaleX(${sx})`; node.style.transformOrigin = "0 0"; }
      return { l, node, spans, words, size, treat, fam, sx, w: 0, x: 0, y: 0 };
    });
    // widths
    built.forEach((b) => { b.w = b.node.getBoundingClientRect().width; });
    const ref = emphIdx >= 0 ? built[emphIdx] : built.reduce((a, b) => (b.w > a.w ? b : a), built[0]);
    let refW = ref ? ref.w : 0;
    if (props.maxW && refW > props.maxW) refW = props.maxW;
    const blockW = Math.max(refW, ...built.filter((b) => b.l.align !== "spread").map((b) => b.w));
    built.forEach((b) => {
      const al = b.l.align || (emphIdx >= 0 && b.l.role !== "emph" && b.l.role !== "title" ? "left" : "center");
      if (al === "spread") { b.node.classList.add("spread"); b.node.style.width = refW + "px"; b.w = refW; b.x = (blockW - refW) / 2; }
      else if (al === "left") b.x = (blockW - refW) / 2;
      else if (al === "right") b.x = (blockW + refW) / 2 - b.w;
      else b.x = (blockW - b.w) / 2;
      b.x += b.l.dx || 0;
    });
    // vertical interlock: x-top(next) = baseline(prev) + gap
    let y = 0;
    built.forEach((b, k) => {
      if (k > 0) {
        const p = built[k - 1];
        const key = `${p.l.role === "small" ? "lead" : p.l.role}>${b.l.role === "small" ? "lead" : b.l.role}`;
        const gap = b.l.gap ?? RSG.M.gap[key] ?? RSG.M.gap.def;
        const MP = RSG.MET[p.fam], MB = RSG.MET[b.fam];
        y = p.y + MP.base * p.size + gap - (MB.base - MB.xh) * b.size;
        // true ascenders (Latin b d f h k l t, digits, capitals, @) may not cut into the previous line: ascender top
        // ≥ previous baseline + 2 px (Cyrillic б / й / ё are allowed to dip in, as in the reference "обещал")
        const txt = b.words.map((w) => w.w).join("");
        const shown = (b.l.keepCase || b.l.role === "title") ? txt : txt.toLowerCase();
        if (/[bdfhklt0-9A-ZА-ЯЁ@%]/.test(shown)) {
          const ascTop = y + (MB.base - 0.74) * b.size;
          const minTop = p.y + MP.base * p.size + 2;
          if (ascTop < minTop) y += minTop - ascTop;
        }
      }
      b.y = y;
    });
    // ink extents: ascender top ≈ baseline − 0.74 em, descender ≈ baseline + 0.12 em
    const inkTop = (b) => b.y + (RSG.MET[b.fam].base - 0.74) * b.size;
    const bottom = (b) => b.y + (RSG.MET[b.fam].base + 0.12) * b.size;
    const top0 = Math.min(...built.map(inkTop));
    built.forEach((b) => { b.y -= top0; b.node.style.left = b.x.toFixed(1) + "px"; b.node.style.top = b.y.toFixed(1) + "px"; });
    const H = Math.max(...built.map(bottom));
    // anchor: emphasis x-band centre on cy (ref 1335) — unless lines follow the emphasis (tuck / 2nd emphasis):
    // then the whole block's ink centre sits on cy − 20 (ref final stack centre ≈ 1312)
    const E = emphIdx >= 0 ? built[emphIdx] : null;
    const after = E ? built.slice(emphIdx + 1).length > 0 : false;
    let topPx;
    if (E && !after && props.anchor !== "block") {
      const ME = RSG.MET[E.fam];
      topPx = cy - (E.y + (ME.base - ME.xh / 2) * E.size);
    } else topPx = (E ? cy - 20 : cy) - H / 2;
    block.style.width = blockW.toFixed(1) + "px";
    block.style.height = H.toFixed(1) + "px";
    block.style.left = (cx - blockW / 2).toFixed(1) + "px";
    block.style.top = topPx.toFixed(1) + "px";
    // reveals
    built.forEach((b) => {
      const dy = RSG.M.rise[b.l.role === "small" ? "lead" : b.l.role] ?? 6;
      b.spans.forEach((s, i) => wordIn(tl, s, b.words[i].at, dy, { flicker: b.treat === "glow-yellow" && (b.l.role === "emph") }));
      const bul = b.node.querySelector(".rsg-bullet");
      if (bul) wordIn(tl, bul, b.words[0].at, 0);
    });
    // glide (ref "мужчина / тем более", "слово / даже важнее / жизни"): lines added BELOW the emphasis push the block
    // up so the visible lines stay centred — offset = (final bottom − visible bottom) / 2, 0.3 s power2.out.
    // Lines above / the emphasis itself never move the block (the lead stays put when the emphasis lands).
    if (props.glide !== false && after) {
      const tE = Math.min(...E.words.map((w) => w.at));
      const order = built.map((b, k) => ({ k, t: Math.min(...b.words.map((w) => w.at)), bot: bottom(b) })).sort((a, b) => a.t - b.t);
      let maxBot = Math.max(...order.filter((o) => o.k <= emphIdx).map((o) => o.bot));
      let curY = (H - maxBot) / 2;
      tl.set(block, { y: curY }, Math.max(0, Math.min(at, tE)));
      order.filter((o) => o.k > emphIdx).forEach((o) => {
        if (o.bot <= maxBot + 1) return;
        maxBot = o.bot;
        const ny = (H - maxBot) / 2;
        ft(tl, block, { y: curY }, { y: ny, duration: RSG.M.glide, ease: "power2.out" }, Math.max(o.t, tE));
        curY = ny;
      });
    }
    if (props.until != null) tl.set(block, { opacity: 0 }, props.until);
    block.lines = built.map((b) => b.node);
    block.metrics = built.map((b) => ({ role: b.l.role, treat: b.treat, size: b.size, w: Math.round(b.w), x: Math.round(cx - blockW / 2 + b.x),
      baseline: Math.round(topPx + b.y + RSG.MET[b.fam].base * b.size),
      xTop: Math.round(topPx + b.y + (RSG.MET[b.fam].base - RSG.MET[b.fam].xh) * b.size) }));
    return block;
  };

  /** Sequence of stacks with HARD swaps: each stack hides when the next one's first word starts (or at `until`). */
  RSG.stacks = function (container, list = [], tl, at = 0, o = {}) {
    const firstT = (s) => Math.min(...(s.lines || []).map((l) => (Array.isArray(l.words) && l.words[0] && l.words[0].at != null ? l.words[0].at : l.at ?? s.at ?? at)));
    return list.map((s, i) => {
      const next = list[i + 1];
      const until = s.until ?? (next ? firstT(next) : o.until);
      return RSG.stack(container, Object.assign({ cy: o.cy }, s, { until }), tl, s.at ?? at);
    });
  };

  /* ------------------------------------------------------------------ *
   * Inserts: scene media, backdrop number, calligraphy
   * ------------------------------------------------------------------ */
  /**
   * Cinematic generated scene: full-bleed image or video (reels-art / connector), slow push 1 → 1.06 for stills.
   * Missing media → labelled slot. Art direction: abstract light / particles / silhouettes — never faces of
   * prophets, companions or holy figures (light or silhouette only).
   * @param {{node?:HTMLElement, src?:string, label?:string, push?:number, dur?:number}} props
   */
  RSG.scene = function (container, props = {}, tl, at = 0) {
    const L = el("div", "rsg-scene", container);
    if (props.node || props.src) {
      const m = props.node || el("img");
      if (!props.node) { m.src = props.src; m.alt = ""; }
      m.classList.add("rsg-media");
      L.appendChild(m); L.media = m;
      if (!props.node && props.push !== 0) ft(tl, m, { scale: 1 }, { scale: 1 + (props.push ?? 0.06), duration: props.dur ?? 2.2, ease: "none" }, at);
    } else {
      const s = el("div", "rsg-scene-slot", L);
      s.textContent = props.label || "сгенерированная сцена · свет / частицы, без лиц";
    }
    return L;
  };
  /** Huge translucent number/word behind the emphasis ("100 %"): fades in 0.3 s, overflowing the frame. */
  RSG.backdrop = function (container, props = {}, tl, at = 0) {
    const b = el("div", "rsg-backdrop", container);
    b.textContent = props.text || "100%";
    b.style.fontSize = (props.size ?? 530) + "px";
    b.style.top = ((props.cy ?? RSG.INSERT_CY) - (props.size ?? 530) * 0.5) + "px";
    tl.fromTo(b, { opacity: 0 }, { opacity: props.opacity ?? 1, duration: 0.3, ease: "power1.out" }, at);
    return b;
  };
  /**
   * Calligraphy / ornament on the white page — CLIENT-SUPPLIED image only (`src`), verified by the client.
   * Without `src` a labelled slot; never typeset or generate holy names.
   * @param {{src?:string, box?:{x:number,y:number,w:number,h:number}, label?:string}} props
   */
  RSG.calligraphy = function (container, props = {}, tl, at = 0) {
    const bx = props.box || { x: 204, y: 626, w: 580, h: 490 };
    const c = el("div", "rsg-callig" + (props.src ? "" : " slot"), container);
    Object.assign(c.style, { left: bx.x + "px", top: bx.y + "px", width: bx.w + "px", height: bx.h + "px" });
    if (props.src) { const i = el("img", null, c); i.src = props.src; i.alt = ""; }
    else { el("div", null, c).textContent = props.label || "каллиграфия клиента"; el("div", "sb", c).textContent = "только файл клиента · проверено"; }
    RSG.enter(tl, c, at, { dur: 0.14, scale: 1.02 });
    return c;
  };

  /* ------------------------------------------------------------------ *
   * Caption track (assembled runs, scripts/captions.py style "g")
   * ------------------------------------------------------------------ */
  /**
   * plan = composition/captions.json: { y, phrases:[{ words:[{w,s,appear}], emph?:{i, treat, tuck?}, kind?:'small'|'statement',
   *   show, hide }] }. Each phrase becomes one stack (hard swaps). Emphasis = the director-marked word (contracts.md
   * → "Style G emphasis"); words before it = lead line, `tuck` words after it = spread line under it.
   */
  RSG.captionTrack = function (container, plan = {}, tl) {
    const L = el("div", "rsg rsg-layer rsg-captions", container);
    const cy = plan.y || RSG.BAND_CY;
    (plan.phrases || []).forEach((p) => {
      // editorial stacks carry no punctuation (ref); onset = reveal start (never early)
      const ws = p.words.map((w) => ({ w: String(w.w).replace(/[.,!?…:;«»"]+/g, "").trim() || w.w, at: Math.max(w.s, p.show) }));
      const lines = [];
      if (p.emph && p.emph.i != null && ws[p.emph.i]) {
        const i = p.emph.i, tuck = p.emph.tuck || 0;
        if (i > 0) lines.push({ role: "lead", words: ws.slice(0, i), align: p.emph.leadAlign || (i > 2 ? "center" : "left") });
        lines.push({ role: "emph", words: [ws[i]], treat: p.emph.treat || "bold-white" });
        const tw = ws.slice(i + 1, i + 1 + tuck);
        if (tw.length) lines.push({ role: "tuck", words: tw, align: tw.length > 1 ? "spread" : "center" });
        const j = p.emph2 && p.emph2.i != null ? p.emph2.i : ws.length;
        const rest = ws.slice(i + 1 + tuck, j);
        if (rest.length) lines.push({ role: "lead", words: rest, align: "center" });
        if (p.emph2 && ws[j]) lines.push({ role: "emph", words: [ws[j]], treat: p.emph2.treat || p.emph.treat, align: "left" });
      } else if (p.kind === "statement" && ws.length > 1) {
        const h = Math.ceil(ws.length / 2);
        lines.push({ role: "m", words: ws.slice(0, h), align: "center" }, { role: "m", words: ws.slice(h), align: "center" });
      } else {
        lines.push({ role: "small", words: ws, align: "center" });
      }
      const b = RSG.stack(L, { lines, cy, until: p.hide }, tl, p.show);
      tl.set(b, { opacity: 1 }, Math.max(0, p.show));
    });
    return L;
  };

  /* ------------------------------------------------------------------ *
   * Layouts — RSG.layout.<id>(clip, spec, tl, at) → layer
   * ------------------------------------------------------------------ */
  const parts = (L, o) => { L.parts = o; return L; };
  RSG.layout = {
    /** head: footage + small-only captions / statements (lead lines, no emphasis). spec {footage, stacks[]} */
    head(clip, spec = {}, tl, at = 0) {
      const L = RSG.layer(clip, { kind: "head" }); L.layout = "head";
      const f = RSG.footage(L, spec.footage || {});
      const st = RSG.stacks(L, spec.stacks || [], tl, at, { cy: spec.cy, until: spec.until });
      return parts(L, { footage: f, stacks: st });
    },
    /** head-emphasis: footage + editorial stacks with one emphasis treatment each. spec {footage, stacks[]} */
    headEmphasis(clip, spec = {}, tl, at = 0) {
      const L = RSG.layout.head(clip, spec, tl, at); L.layout = "head-emphasis"; return L;
    },
    /** insert-kinetic: mint page (or paper) + navy stack centred on y 960, optional 1-frame flash in. spec {bg, flash, stacks[]} */
    insertKinetic(clip, spec = {}, tl, at = 0) {
      const L = RSG.layer(clip, { kind: spec.bg || "mint" }); L.layout = "insert-kinetic";
      const st = RSG.stacks(L, (spec.stacks || []).map((s) => Object.assign({}, s, {
        lines: s.lines.map((l) => Object.assign({ treat: l.role === "emph" ? (L.kind === "paper" ? "ink" : "navy") : undefined }, l)) })),
      tl, at, { cy: spec.cy ?? RSG.INSERT_CY });
      const fl = spec.flash !== false ? RSG.flash(L, {}, tl, at) : null;
      return parts(L, { stacks: st, flash: fl });
    },
    /** insert-scene: generated image/video + optional huge translucent backdrop + stacks. spec {media, backdrop:{text,at,size}, stacks[]} */
    insertScene(clip, spec = {}, tl, at = 0) {
      const L = RSG.layer(clip, { kind: "scene" }); L.layout = "insert-scene";
      const sc = RSG.scene(L, Object.assign({ dur: spec.dur }, spec.media || {}), tl, at);
      const bd = spec.backdrop ? RSG.backdrop(L, Object.assign({ cy: spec.cy ?? RSG.INSERT_CY }, spec.backdrop), tl, spec.backdrop.at ?? at + 0.3) : null;
      const st = RSG.stacks(L, spec.stacks || [], tl, at, { cy: spec.cy ?? RSG.INSERT_CY });
      return parts(L, { scene: sc, backdrop: bd, stacks: st });
    },
    /** insert-calligraphy: white page + client calligraphy image + black lead words over its top. spec {src, box, stacks[]} */
    insertCalligraphy(clip, spec = {}, tl, at = 0) {
      const L = RSG.layer(clip, { kind: "paper" }); L.layout = "insert-calligraphy";
      const c = RSG.calligraphy(L, { src: spec.src, box: spec.box, label: spec.label }, tl, spec.calligraphyAt ?? at + 0.2);
      const st = RSG.stacks(L, spec.stacks || [], tl, at, { cy: spec.cy ?? 860 });
      return parts(L, { calligraphy: c, stacks: st });
    },
    /** statement: footage (or a dark page) + white M two-line statement (+ optional emphasis); also the CTA ending. */
    statement(clip, spec = {}, tl, at = 0) {
      const L = RSG.layer(clip, { kind: spec.footage ? "head" : (spec.bg || "dark") }); L.layout = "statement";
      const f = spec.footage ? RSG.footage(L, spec.footage) : null;
      const st = RSG.stacks(L, spec.stacks || [], tl, at, { cy: spec.cy ?? (spec.footage ? RSG.BAND_CY : RSG.INSERT_CY) });
      return parts(L, { footage: f, stacks: st });
    },
  };
  RSG.layout["head-emphasis"] = RSG.layout.headEmphasis;
  RSG.layout["insert-kinetic"] = RSG.layout.insertKinetic;
  RSG.layout["insert-scene"] = RSG.layout.insertScene;
  RSG.layout["insert-calligraphy"] = RSG.layout.insertCalligraphy;

  /** Stack metrics of every stack under root (for side-by-side checks against the teardown numbers). */
  RSG.audit = function (root) {
    return Array.from((root || document).querySelectorAll(".rsg-stack")).map((b) => (b.metrics || []));
  };
  RSG.esc = esc;
  window.RSG = RSG;
})();
