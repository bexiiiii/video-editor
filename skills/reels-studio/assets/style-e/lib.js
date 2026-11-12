/* reels-studio · Style E "Data News" — component library (global RSE)
 * Spec: references/style-e.md · measurements: references/teardowns/style-e/DfmpUlfuHod.md
 * Load order: GSAP → lib/runtime.js (RS) → lib/tokens-e.css → lib/e.js. Build inside `await RSE.ready()`
 * (captions and layouts are measured at build time), register the timeline last.
 *
 * Model: ONE continuous white page (`RSE.page`) with a persistent channel header + chapter tabs; content beats
 * (`RSE.layout.*`) replace each other with a blur-out / blur-in swap (`RSE.tx.blur`); a literal uppercase caption
 * track (`RSE.caption`) runs underneath, independent of the beats.
 * Every builder: `RSE.x(host, props, tl, at) → HTMLElement`; builders append IN FLOW to `host` (layouts own the
 * geometry); all times are absolute local seconds; entrances are fromTo, later state changes use `RSE.ft`
 * (fromTo + immediateRender:false) so any seek is exact. Self-contained: needs only GSAP + RS (runtime.js).
 */
(function () {
  const RSE = { version: "1.0" };
  const RS = window.RS || {};
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  RSE.el = el;

  /** State-change tween: explicit from/to, never renders before its start (seek-safe). */
  function ft(tl, target, from, to, at) { return tl.fromTo(target, from, Object.assign({ immediateRender: false }, to), at); }
  RSE.ft = ft;

  /* ------------------------------------------------------------------ *
   * Measured motion constants (DfmpUlfuHod §4/§6)
   * ------------------------------------------------------------------ */
  RSE.M = {
    enter: { blur: 14, y: 22, scale: 0.98, dur: 0.32, ease: "power2.out" },   // every element: blur-in 0.25–0.35 s
    exit: { blur: 20, dur: 0.21, ease: "power1.in" },                         // whole beat: blur-out 6–7 frames
    gap: 0.17,                                                                 // empty page between beats (5 frames)
    stagger: 0.08,                                                             // kicker → headline → first card
    tab: { dur: 0.6, ease: "power3.out" },                                     // tab segment fill 16/60/100/126/140/148/152 px @10 fps
    count: { dur: 0.9, ease: "power3.out" },                                   // 0 → 140 in 0.9 s (107 at +0.3 s)
    pct: { dur: 3.6, ease: "power2.out" },                                     // % bars: 86 % reached after ≈4 s
  };

  /** Wait for Inter + Inter Tight (captions, layouts and fit are measured at build time). */
  RSE.ready = function () {
    const f = document.fonts;
    if (!f || !f.load) return Promise.resolve();
    const specs = ["400 30px Inter", "500 30px Inter", "600 30px Inter", "700 80px Inter", "800 400px Inter", "800 48px 'Inter Tight'"];
    const sample = "ӘәҒғҚқҢңӨөҰұҮүҺһІі";
    return Promise.all(specs.map((s) => f.load(s, sample).catch(() => null))).then(() => f.ready);
  };

  /** Generic element entrance: blur 14→0, opacity 0→1, y +22→0, scale .98→1 (0.32 s power2.out). */
  function enter(tl, node, at, o = {}) {
    const m = RSE.M.enter;
    tl.fromTo(node, { opacity: 0, filter: `blur(${o.blur ?? m.blur}px)`, y: o.y ?? m.y, scale: o.scale ?? m.scale },
      { opacity: 1, filter: "blur(0px)", y: 0, scale: 1, duration: o.dur ?? m.dur, ease: o.ease || m.ease }, at);
    return node;
  }
  RSE.enter = enter;

  /** Number format for kk/ru: thin-space thousands, decimal comma ("8 061", "93,2"). */
  function fmt(v, dec = 0, sep = " ") {
    const s = Math.abs(v).toFixed(dec).split(".");
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    return (v < 0 ? "−" : "") + s.join(",");
  }
  RSE.fmt = fmt;

  /** Seek-safe count-up into node.textContent. o: {from=0,to,dur,ease,dec,prefix,suffix}. */
  function count(tl, node, at, o) {
    const st = { v: o.from ?? 0 };
    const show = () => { node.textContent = (o.prefix || "") + fmt(st.v, o.dec || 0) + (o.suffix || ""); };
    show();
    tl.fromTo(st, { v: o.from ?? 0 }, { v: o.to, duration: o.dur ?? RSE.M.count.dur, ease: o.ease || RSE.M.count.ease, onUpdate: show, immediateRender: false }, at);
    return node;
  }
  RSE.count = count;

  /* ---- icons (stroke, currentColor) ---- */
  const I = {
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    comment: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 4v-4A2.5 2.5 0 0 1 4 13.5z"/></svg>',
    repost: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 10V8a2 2 0 0 1 2-2h11M15 3l3 3-3 3M19 14v2a2 2 0 0 1-2 2H6M9 21l-3-3 3-3"/></svg>',
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M21 3 3 10.5l7 2.5 2.5 7z"/><path d="M10 13 21 3"/></svg>',
    views: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5 10 17l9-10"/></svg>',
    up: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
    arrow: '<svg viewBox="0 0 56 32" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16h46M38 5l12 11-12 11"/></svg>',
    camera: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M3 8.5A2.5 2.5 0 0 1 5.5 6h2l1.5-2h6l1.5 2h2A2.5 2.5 0 0 1 21 8.5v9a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/><circle cx="12" cy="13" r="4"/></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h16M6 15l4-4 3 3 5-6"/></svg>',
    briefcase: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3 12h18"/></svg>',
    scale: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v16M7 20h10M5 7h14M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/></svg>',
    coin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v9M9.5 10a2.5 2 0 0 1 2.5-1.5h.5a2 2 0 0 1 0 4h-1a2 2 0 0 0 0 4h.5a2.5 2 0 0 0 2.5-1.5"/></svg>',
  };
  RSE.icons = I;

  function monogram(host, name) {
    const letters = String(name || "?").replace(/[@|·•,]/g, " ").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
    const m = el("span", "rse-mono", host); m.textContent = letters || "?";
    return m;
  }
  RSE.monogram = monogram;

  /** Neutral labelled media slot (no material supplied). Never draws a person. */
  function slot(host, label, sub) {
    const s = el("div", "rse-slot", host, I.camera);
    el("div", "l1", s).textContent = label || "фото";
    if (sub) el("div", "l2", s).textContent = sub;
    return s;
  }
  /** Fill a media box from props: {src} image · {node} element (e.g. framework <video>) · else labelled slot. */
  function media(box, p) {
    if (p.node) { box.appendChild(p.node); return p.node; }
    if (p.src) { const im = el("img", null, box); im.src = p.src; im.alt = ""; if (p.pos) im.style.objectPosition = p.pos; return im; }
    return slot(box, p.label, p.sub);
  }
  RSE.mediaFill = media;

  /* ------------------------------------------------------------------ *
   * Page + persistent chrome
   * ------------------------------------------------------------------ */

  /**
   * The page root. Everything of Style E lives inside it.
   * @param {HTMLElement} container stage/clip element (1080×1920)
   * @param {{refMargin?:boolean}} props refMargin → reference 64 px margins (A/B checks only; layouts.md wants 90)
   * @returns {HTMLElement} page with `.beats` (content beats) and `.capl` (caption layer)
   */
  RSE.page = function (container, props = {}, tl, at = 0) {
    const p = el("div", "rse" + (props.refMargin ? " rse-refmargin" : ""), container);
    p.beats = el("div", "rse-beats", p);
    p.capl = el("div", "rse-capl", p);
    return p;
  };

  /**
   * Channel header (static from frame 0, never animates out): round-cornered logo 88 px, name 37/700, handle 24, rubric pill.
   * Identity comes from the brief — never hardcode a creator.
   * @param {HTMLElement} page RSE.page
   * @param {{logo?:string, logoNode?:HTMLElement, name:string, handle?:string, rubric?:string, enterAt?:number}} props
   */
  RSE.header = function (page, props, tl, at = 0) {
    if (!props || !props.name) throw new Error("RSE.header: name is required (from brief.cta / brief.brand)");
    const h = el("div", "rse-head", page);
    const lg = el("div", "rse-logo", h);
    if (props.logoNode) lg.appendChild(props.logoNode);
    else if (props.logo) { const im = el("img", null, lg); im.src = props.logo; im.alt = ""; }
    else monogram(lg, props.name);
    el("div", "rse-name", h).textContent = props.name;
    if (props.handle) el("div", "rse-handle", h).textContent = props.handle;
    if (props.rubric) { const pl = el("div", "rse-pill", h, "<i></i>"); pl.appendChild(document.createTextNode(props.rubric)); h.pill = pl; }
    if (props.enterAt != null && tl) enter(tl, h, props.enterAt, { y: 0, scale: 1 });
    return h;
  };

  /**
   * Chapter tabs (segmented progress under the header): 6 px bars, 8 px gaps, labels 20 px.
   * A step fills its segment with the gold gradient (scaleX 0→1, 0.6 s power3.out) and makes its label black;
   * earlier segments stay gold (story-progress semantics).
   * @param {HTMLElement} page
   * @param {{items:string[], steps:{at:number,index:number}[]}} props
   */
  RSE.tabs = function (page, props, tl) {
    const w = el("div", "rse-tabs", page);
    const tabs = props.items.map((t) => {
      const d = el("div", "rse-tab", w);
      const bar = el("div", "bar", d); const fill = el("div", "fill", bar);
      const lbl = el("div", "lbl", d); lbl.appendChild(document.createTextNode(t));
      const b = el("b", null, lbl); b.textContent = t; b.style.left = "0"; b.style.top = "0";
      return { d, fill, b };
    });
    let prev = null;
    (props.steps || []).forEach((s) => {
      const t = tabs[s.index]; if (!t) return;
      ft(tl, t.fill, { scaleX: 0 }, { scaleX: 1, duration: RSE.M.tab.dur, ease: RSE.M.tab.ease }, s.at);
      ft(tl, t.b, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power1.out" }, s.at);
      if (prev) ft(tl, prev.b, { opacity: 1 }, { opacity: 0, duration: 0.25, ease: "power1.out" }, s.at);
      prev = t;
    });
    w.tabs = tabs;
    return w;
  };

  /* ------------------------------------------------------------------ *
   * Text
   * ------------------------------------------------------------------ */

  function lineHTML(line, accent) {
    const ac = (accent || []).map((a) => a.toLowerCase());
    let html = esc(line);
    ac.forEach((a) => {
      const i = line.toLowerCase().indexOf(a);
      if (i >= 0) html = esc(line.slice(0, i)) + `<span class="ac">${esc(line.slice(i, i + a.length))}</span>` + esc(line.slice(i + a.length));
    });
    return html;
  }

  /**
   * Source kicker + headline (left-aligned). Kicker 30/600 brown-gold; headline 80/700 −0.035em, ≤ 2 lines,
   * accent phrases in the gold gradient. Both blur in as blocks (kicker at `at`, headline at at+0.08) — the reference
   * does not reveal headlines word by word; the word-level sync lives in the caption track.
   * @param {HTMLElement} host flow container
   * @param {{kicker?:string, lines:string[], accent?:string[], size?:number, maxW?:number}} props
   */
  RSE.title = function (host, props, tl, at) {
    const w = el("div", "rse-title", host);
    if (props.kicker) { w.kicker = el("div", "rse-kicker", w); w.kicker.textContent = props.kicker; enter(tl, w.kicker, at, { y: 12 }); }
    const h = el("div", "rse-headline", w);
    if (!props.kicker) h.style.marginTop = "0";
    if (props.size) h.style.fontSize = props.size + "px";
    (props.lines || []).forEach((ln) => { el("span", "ln", h, lineHTML(ln, props.accent)); });
    // shrink-to-fit: no line may exceed the column (build-time measurement)
    const maxW = props.maxW || host.clientWidth || 900;
    const widest = Math.max(...[...h.children].map((c) => c.getBoundingClientRect().width));
    if (widest > maxW) h.style.fontSize = Math.floor(parseFloat(getComputedStyle(h).fontSize) * maxW / widest) + "px";
    w.headline = h;
    enter(tl, h, at + (props.kicker ? RSE.M.stagger : 0), { y: 16 });
    return w;
  };

  /* ------------------------------------------------------------------ *
   * Components (all in-flow; `mt` = margin-top px)
   * ------------------------------------------------------------------ */

  function card(host, cls, props) {
    const c = el("div", "rse-card" + (cls ? " " + cls : ""), host);
    if (props.mt != null) c.style.marginTop = props.mt + "px";
    if (props.height) c.style.height = props.height + "px";
    if (props.width) c.style.width = props.width + (typeof props.width === "number" ? "px" : "");
    return c;
  }

  /**
   * News cover card: photo (or labelled slot) + dark bottom gradient + spaced uppercase kicker, white 84/700 title with
   * gold accent, gold dash + sub line. Photo eases from scale 1.06 → 1 while the card blurs in; texts rise after.
   * @param {{src?:string,node?:HTMLElement,label?:string,sub?:string,kicker?:string,lines:string[],accent?:string[],subline?:string,height?:number,textAt?:number,subAt?:number}} props
   */
  RSE.cover = function (host, props, tl, at) {
    const c = el("div", "rse-cover", host);
    c.style.height = (props.height || 1012) + "px";
    if (props.mt != null) c.style.marginTop = props.mt + "px";
    const ph = el("div", "ph", c); media(ph, props);
    el("div", "shade", c);
    const tx = el("div", "tx", c);
    if (props.kicker) el("div", "ck", tx).textContent = props.kicker;
    const tt = el("div", "tt", tx); (props.lines || []).forEach((ln) => el("span", "ln", tt, lineHTML(ln, props.accent)));
    let sb = null;
    if (props.subline) { sb = el("div", "sb", tx, "<i></i>"); sb.appendChild(document.createTextNode(props.subline)); }
    enter(tl, c, at, { y: 0, scale: 0.97, blur: 18, dur: 0.4 });
    tl.fromTo(ph, { scale: 1.06 }, { scale: 1, duration: 1.6, ease: "power2.out" }, at);
    const ta = props.textAt ?? at + 0.15;
    [...tx.children].forEach((n, i) => { if (n !== sb) enter(tl, n, ta + i * 0.07, { y: 18, scale: 1 }); });
    if (sb) enter(tl, sb, props.subAt ?? ta + 0.5, { y: 12, scale: 1 });
    c.text = tx;
    return c;
  };

  /**
   * Photo / video card (B-roll, screenshot, post image). Labelled neutral slot without material.
   * @param {{src?:string,node?:HTMLElement,label?:string,sub?:string,height?:number,width?:number|string,radius?:number}} props
   */
  RSE.photo = function (host, props, tl, at) {
    const c = el("div", "rse-cover", host);
    c.style.height = (props.height || 560) + "px";
    if (props.width) c.style.width = props.width + (typeof props.width === "number" ? "px" : "");
    if (props.mt != null) c.style.marginTop = props.mt + "px";
    if (props.radius) c.style.borderRadius = props.radius + "px";
    const ph = el("div", "ph", c); media(ph, props);
    enter(tl, c, at, { y: 0, scale: 0.97, blur: 18, dur: 0.36 });
    tl.fromTo(ph, { scale: 1.05 }, { scale: 1, duration: 1.4, ease: "power2.out" }, at);
    return c;
  };

  /**
   * Social stats chips (likes / comments / reposts / shares) in a column; each chip blurs in on its time and its value
   * counts up from 0 (0.9 s power3.out). Icon: first chip on a gold disc, the rest on white discs (as the reference).
   * @param {{items:{icon:'heart'|'comment'|'repost'|'share'|'views', value:number, dec?:number, suffix?:string, label:string, at?:number}[], rowH?:number, gap?:number, width?:number|string, stagger?:number}} props
   */
  RSE.stats = function (host, props, tl, at) {
    const col = el("div", "rse-stats", host);
    col.style.display = "flex"; col.style.flexDirection = "column"; col.style.gap = (props.gap ?? 22) + "px";
    if (props.width) col.style.width = props.width + (typeof props.width === "number" ? "px" : "");
    if (props.mt != null) col.style.marginTop = props.mt + "px";
    col.chips = props.items.map((it, i) => {
      const c = card(col, null, { height: props.rowH || 172 }); c.style.padding = "0";
      const s = el("div", "rse-stat", c);
      el("div", "ic" + (i === 0 ? " gold" : ""), s, I[it.icon] || I.heart);
      const tx = el("div", null, s); const v = el("div", "v", tx); el("div", "k", tx).textContent = it.label;
      const t = it.at ?? at + i * (props.stagger ?? 0.18);
      enter(tl, c, t);
      count(tl, v, t + 0.1, { to: it.value, dec: it.dec || 0, suffix: it.suffix || "" });
      return c;
    });
    return col;
  };

  /**
   * Numbered chips row (ranked categories: ① Халықаралық қатынастар ② Аударма ісі). Height 170, 2–3 per row.
   * @param {{items:{text:string, at?:number}[], height?:number}} props
   */
  RSE.chips = function (host, props, tl, at) {
    const row = el("div", "rse-chips", host);
    row.style.display = "flex"; row.style.gap = "22px";
    if (props.mt != null) row.style.marginTop = props.mt + "px";
    row.items = props.items.map((it, i) => {
      const c = card(row, null, { height: props.height || 170 }); c.style.padding = "0"; c.style.flex = "1 1 0";
      const ch = el("div", "rse-chip", c);
      el("div", "rse-num", ch).textContent = String(i + 1);
      el("div", null, ch, esc(it.text).replace(/\n/g, "<br>"));
      enter(tl, c, it.at ?? at + i * 0.25);
      return c;
    });
    return row;
  };

  /**
   * Data card: grey label, gold-gradient count-up number + grey "/ max", gold progress bar filling with the count,
   * optional bold note under the bar. Measured: number digits 176 px (240 px font), bar 24 px, card r32.
   * @param {{label?:string, value:number, from?:number, max?:number, maxText?:string, dec?:number, suffix?:string, note?:string, countAt?:number, dur?:number, size?:number, height?:number}} props
   */
  RSE.dataCard = function (host, props, tl, at) {
    const c = card(host, "rse-data", props);
    if (props.label) el("div", "rse-label", c).textContent = props.label;
    const big = el("div", "rse-big", c); big.style.marginTop = "18px";
    if (props.size) big.style.fontSize = props.size + "px";
    const n = el("span", "n", big);
    if (props.max != null || props.maxText) el("span", "of", big).textContent = "/ " + (props.maxText || fmt(props.max));
    // reserve the final width so the "/ max" never moves while counting
    n.textContent = fmt(Math.max(props.value, props.from || 0), props.dec || 0) + (props.suffix || "");
    n.style.minWidth = n.getBoundingClientRect().width + "px";
    // fit: the number + "/ max" must stay inside the card (build-time)
    const inner = (host.clientWidth || 900) - 2 * 40 - 60, bw = big.lastChild.getBoundingClientRect().right - big.getBoundingClientRect().left;
    if (bw > inner) { const fs = parseFloat(getComputedStyle(big).fontSize) * inner / bw; big.style.fontSize = Math.floor(fs) + "px"; n.style.minWidth = ""; n.style.minWidth = n.getBoundingClientRect().width + "px"; }
    let fill = null;
    if (props.bar !== false) {
      const bar = el("div", "rse-bar", c); bar.style.marginTop = "34px";
      fill = el("div", "fill", bar);
    }
    if (props.note) { const nt = el("div", "rse-note", c); nt.style.marginTop = "26px"; nt.textContent = props.note; }
    enter(tl, c, at);
    const ca = props.countAt ?? at + 0.2, dur = props.dur ?? RSE.M.count.dur;
    count(tl, n, ca, { from: props.from || 0, to: props.value, dec: props.dec || 0, suffix: props.suffix || "", dur });
    if (fill) {
      const max = props.max || props.value || 1;
      tl.fromTo(fill, { scaleX: (props.from || 0) / max }, { scaleX: props.value / max, duration: dur, ease: RSE.M.count.ease, immediateRender: true }, ca);
    }
    c.number = n; c.fill = fill;
    return c;
  };

  /**
   * Percent rows: one card per row — title (38/600, ≤ 2 lines) left, gold-gradient % count-up right (132 px),
   * gold bar under it and a grey note. Count + bar run together, slow power2.out (≈3.6 s), decimals with a comma.
   * @param {{rows:{title:string, value:number, dec?:number, note?:string, at?:number, dur?:number}[], gap?:number}} props
   */
  RSE.percentRows = function (host, props, tl, at) {
    const col = el("div", "rse-pcts", host);
    col.style.display = "flex"; col.style.flexDirection = "column"; col.style.gap = (props.gap ?? 22) + "px";
    if (props.mt != null) col.style.marginTop = props.mt + "px";
    col.rows = props.rows.map((r, i) => {
      const c = card(col, null, {});
      const top = el("div", "rse-pct", c);
      el("div", "t", top, esc(r.title).replace(/\n/g, "<br>"));
      const v = el("div", "v", top);
      v.textContent = fmt(r.value, r.dec || 0) + "%"; v.style.minWidth = v.getBoundingClientRect().width + "px"; v.style.textAlign = "right";
      const bar = el("div", "rse-bar", c); bar.style.marginTop = "28px"; const fill = el("div", "fill", bar);
      if (r.note) { const nt = el("div", "rse-label", c); nt.style.marginTop = "18px"; nt.textContent = r.note; }
      const t = r.at ?? at + i * 0.6, dur = r.dur ?? RSE.M.pct.dur;
      enter(tl, c, t);
      count(tl, v, t + 0.15, { to: r.value, dec: r.dec || 0, suffix: "%", dur, ease: RSE.M.pct.ease });
      tl.fromTo(fill, { scaleX: 0 }, { scaleX: r.value / 100, duration: dur, ease: RSE.M.pct.ease }, t + 0.15);
      return c;
    });
    return col;
  };

  /**
   * "?/m" question data card that resolves to a count: gold "?" → number (blur swap), grey "/m", kicker + question
   * text with gold accent words. Pair with RSE.dotRow (same `fillAt`) for the reference "8/12" beat.
   * @param {{value:number, max:number, kicker?:string, text:string, accent?:string[], swapAt:number, height?:number}} props
   */
  RSE.questionCard = function (host, props, tl, at) {
    const c = card(host, "rse-qcard", props);
    c.style.display = "flex"; c.style.alignItems = "center"; c.style.gap = "34px";
    const big = el("div", "rse-big", c); big.style.fontSize = (props.size || 260) + "px"; big.style.position = "relative"; big.style.flex = "none";
    const n = el("span", "n", big); n.textContent = "?";
    const q = el("span", "n", big); q.textContent = String(props.value); q.style.position = "absolute"; q.style.left = "0"; q.style.top = "0";
    el("span", "of", big).textContent = "/" + props.max;
    const tx = el("div", null, c);
    if (props.kicker) { const k = el("div", "rse-label", tx); k.textContent = props.kicker; k.style.marginBottom = "10px"; }
    const t = el("div", null, tx, lineHTML(props.text, props.accent));
    t.style.font = "700 40px/50px var(--rse-font)"; t.style.letterSpacing = "-0.02em"; t.style.color = "var(--rse-ink-2)";
    t.querySelectorAll(".ac").forEach((a) => a.classList.add("rse-gold-text"));
    enter(tl, c, at);
    tl.fromTo(q, { opacity: 0 }, { opacity: 0, duration: 0.01 }, at);
    ft(tl, n, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(14px)", duration: 0.2, ease: "power1.in" }, props.swapAt);
    ft(tl, q, { opacity: 0, filter: "blur(14px)", scale: 0.9 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power2.out" }, props.swapAt + 0.12);
    return c;
  };

  /**
   * Dot row "n of m": m grey discs pop in left→right (≈0.08 s stagger), then the first n turn gold with a white check
   * one by one from `fillAt`; legend under it. Plain discs — the library never draws figures or faces.
   * @param {{m:number, n:number, fillAt:number, stagger?:number, fillStagger?:number, legend?:[string,string], size?:number}} props
   */
  RSE.dotRow = function (host, props, tl, at) {
    const c = card(host, "rse-dotcard", props);
    const row = el("div", "rse-dots", c);
    const size = props.size || 60;
    const dots = [];
    for (let i = 0; i < props.m; i++) {
      const d = el("div", "rse-dot", row, I.check); d.style.width = d.style.height = size + "px";
      dots.push(d);
      tl.fromTo(d, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2)" }, at + 0.15 + i * (props.stagger ?? 0.08));
    }
    dots.slice(0, props.n).forEach((d, i) => {
      const t = props.fillAt + i * (props.fillStagger ?? 0.09);
      ft(tl, d, { backgroundColor: "#E4E4E8" }, { backgroundColor: "#D4902A", duration: 0.18, ease: "power1.out" }, t);
      ft(tl, d.firstChild, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }, t + 0.04);
    });
    if (props.legend) {
      const lg = el("div", "rse-legend", c);
      lg.innerHTML = `<span><i style="background:var(--rse-gold-2)"></i>${esc(props.legend[0])}</span><span class="o"><i style="background:#E4E4E8"></i>${esc(props.legend[1] || "")}</span>`;
      enter(tl, lg, props.fillAt + props.n * (props.fillStagger ?? 0.09), { y: 8, scale: 1 });
    }
    enter(tl, c, at);
    c.dots = dots;
    return c;
  };

  /**
   * Question beat: big gold "?" (290 px Heavy, gold vertical gradient) pops with blur, question line (66/700) under it.
   * @param {{text:string, accent?:string[], qAt?:number, textAt?:number}} props
   */
  RSE.question = function (host, props, tl, at) {
    const w = el("div", "rse-question", host);
    const q = el("div", "rse-q", w, '<span class="m">?</span>');
    const t = el("div", "rse-qt", w, lineHTML(props.text, props.accent));
    t.querySelectorAll(".ac").forEach((a) => a.classList.add("rse-gold-text"));
    tl.fromTo(q, { opacity: 0, scale: 0.7, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "back.out(1.6)" }, props.qAt ?? at);
    enter(tl, t, props.textAt ?? at + 0.35, { y: 16, scale: 1 });
    return w;
  };

  /**
   * Official post / quote card: avatar (logo src or monogram), handle, meta, body quote with gold accent, footer counts.
   * @param {{avatar?:string, monoName?:string, name:string, meta?:string, text:string, accent?:string[], likes?:number, comments?:number, countAt?:number}} props
   */
  RSE.post = function (host, props, tl, at) {
    const c = card(host, "rse-post", props);
    const hd = el("div", "hd", c);
    const av = el("div", "av", hd);
    if (props.avatar) { const im = el("img", null, av); im.src = props.avatar; im.alt = ""; } else monogram(av, props.monoName || props.name);
    const who = el("div", null, hd); el("div", "who", who).textContent = props.name; if (props.meta) el("div", "when", who).textContent = props.meta;
    const body = el("div", "body", c, lineHTML(props.text, props.accent));
    enter(tl, c, at);
    enter(tl, body, at + 0.18, { y: 12, scale: 1 });
    if (props.likes != null || props.comments != null) {
      const f = el("div", "ft", c);
      if (props.likes != null) { const s = el("span", null, f, I.heart); const v = el("b", null, s); count(tl, v, props.countAt ?? at + 0.4, { to: props.likes }); }
      if (props.comments != null) { const s = el("span", null, f, I.comment); const v = el("b", null, s); count(tl, v, props.countAt ?? at + 0.4, { to: props.comments }); }
    }
    return c;
  };

  /**
   * Compare row in a card: left value (static) → gold arrow → right value counting up (e.g. 1 800+ → 2 500+).
   * @param {{left:{k:string, v:number, suffix?:string, from?:number}, right:{k:string, v:number, suffix?:string, from?:number, at?:number}}} props
   */
  RSE.compare = function (host, props, tl, at) {
    const c = card(host, "rse-cmpcard", props);
    const row = el("div", "rse-cmp", c);
    const L = el("div", "side", row); el("div", "k", L).textContent = props.left.k; const lv = el("div", "v", L);
    const arr = el("div", "arr", row, I.arrow);
    const R = el("div", "side", row); el("div", "k", R).textContent = props.right.k; const rv = el("div", "v g", R);
    enter(tl, c, at);
    count(tl, lv, at + 0.15, { from: props.left.from ?? 0, to: props.left.v, suffix: props.left.suffix || "", dur: 1.2 });
    const ra = props.right.at ?? at + 1.4;
    tl.fromTo([arr, R], { opacity: 0, x: -24, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.3, ease: "power2.out", stagger: 0.1 }, ra);
    count(tl, rv, ra + 0.15, { from: props.right.from ?? props.left.v * 0.7, to: props.right.v, suffix: props.right.suffix || "", dur: 1.0 });
    return c;
  };

  /**
   * Line chart card: faint horizontal guides, gold curve(s) drawing L→R (stroke-dash), optional grey dashed series,
   * legend. Points are 0..1 (y up). Reference draw: 1.0 s (Сандар нені көрсетеді) … 5 s (slow trend).
   * @param {{title?:string, series:{points:number[], label?:string, dashed?:boolean, color?:string, at?:number, dur?:number}[], height?:number, chartH?:number}} props
   */
  RSE.chart = function (host, props, tl, at) {
    const c = card(host, "rse-chart", props);
    if (props.title) el("div", "rse-label", c).textContent = props.title;
    const W = (host.clientWidth || 900) - 80, H = props.chartH || 300;
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg"); svg.setAttribute("width", W); svg.setAttribute("height", H); svg.style.marginTop = "26px";
    c.appendChild(svg);
    const gid = "rseg" + Math.round(at * 1000) + "_" + (props.series.length);
    svg.innerHTML = `<defs><linearGradient id="${gid}" x1="0" x2="1"><stop offset="0" stop-color="#E89E0C"/><stop offset=".55" stop-color="#C9822E"/><stop offset="1" stop-color="#A8672C"/></linearGradient></defs>` +
      [0.2, 0.45, 0.7, 0.95].map((g) => `<line x1="0" x2="${W}" y1="${H * g}" y2="${H * g}" stroke="#E7E7E9" stroke-width="2"/>`).join("");
    const lg = el("div", "lg", c); lg.style.marginTop = "22px";
    props.series.forEach((s, si) => {
      const pts = s.points.map((v, i) => [10 + (W - 20) * i / (s.points.length - 1), H * 0.95 - v * H * 0.85]);
      let d = `M${pts[0][0]},${pts[0][1]}`;
      for (let i = 1; i < pts.length; i++) { // Catmull-Rom → cubic Bézier (smooth trend line, no steps)
        const p0 = pts[Math.max(0, i - 2)], p1 = pts[i - 1], p2 = pts[i], p3 = pts[Math.min(pts.length - 1, i + 1)];
        d += ` C${p1[0] + (p2[0] - p0[0]) / 6},${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6},${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]},${p2[1]}`;
      }
      const path = document.createElementNS(ns, "path");
      path.setAttribute("d", d); path.setAttribute("fill", "none"); path.setAttribute("stroke-linecap", "round");
      path.setAttribute("stroke", s.dashed ? "#C4C4C9" : (s.color || `url(#${gid})`)); path.setAttribute("stroke-width", s.dashed ? 4 : 7);
      svg.appendChild(path);
      const len = path.getTotalLength ? path.getTotalLength() : W * 1.2;
      const t = s.at ?? at + 0.3 + si * 0.8, dur = s.dur ?? 1.0;
      if (s.dashed) {
        // dotted line revealed by a clip that grows (dash pattern itself must stay)
        path.setAttribute("stroke-dasharray", "2 12");
        const cp = document.createElementNS(ns, "clipPath"); const cid = gid + "c" + si; cp.setAttribute("id", cid);
        const r = document.createElementNS(ns, "rect"); r.setAttribute("x", 0); r.setAttribute("y", -20); r.setAttribute("height", H + 40); r.setAttribute("width", W);
        cp.appendChild(r); svg.querySelector("defs").appendChild(cp); path.setAttribute("clip-path", `url(#${cid})`);
        tl.fromTo(r, { attr: { width: 0 } }, { attr: { width: W }, duration: dur, ease: "power1.inOut" }, t);
      } else {
        path.style.strokeDasharray = len; tl.fromTo(path, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: dur, ease: "power1.inOut" }, t);
      }
      if (s.label) {
        const it = el("span", null, lg, `<i style="background:${s.dashed ? "#C4C4C9" : "var(--rse-gold)"}"></i>${esc(s.label)}`);
        enter(tl, it, t, { y: 0, scale: 1, blur: 8, dur: 0.25 });
      }
    });
    enter(tl, c, at);
    return c;
  };

  /**
   * Toggle list card (gold iOS switches): rows {kicker, title, on, flips:[{at,on}]}; a flip slides the knob 0.3 s
   * power2.inOut, fades the gold track and greys / blackens the row title.
   * @param {{rows:{kicker?:string, title:string, on?:boolean, flips?:{at:number,on:boolean}[]}[]}} props
   */
  RSE.toggles = function (host, props, tl, at) {
    const c = card(host, "rse-tgs", props);
    props.rows.forEach((r, i) => {
      const row = el("div", "rse-tg", c); if (i) { row.style.marginTop = "34px"; row.style.paddingTop = "30px"; row.style.borderTop = "2px solid #EAEAEC"; }
      const tx = el("div", null, row); if (r.kicker) el("div", "k", tx).textContent = r.kicker; const tt = el("div", "t", tx); tt.textContent = r.title;
      const sw = el("div", "rse-sw", row); const on = el("div", "on", sw); const kn = el("div", "kn", sw);
      const set = (state, t, inst) => {
        const to = state ? { x: 38 } : { x: 0 };
        if (inst) { gsap.set(kn, to); gsap.set(on, { opacity: state ? 1 : 0 }); gsap.set(tt, { color: state ? "#1C1C1E" : "#A6A6AB" }); return; }
        ft(tl, kn, { x: state ? 0 : 38 }, Object.assign({ duration: 0.3, ease: "power2.inOut" }, to), t);
        ft(tl, on, { opacity: state ? 0 : 1 }, { opacity: state ? 1 : 0, duration: 0.3, ease: "power2.inOut" }, t);
        ft(tl, tt, { color: state ? "#A6A6AB" : "#1C1C1E" }, { color: state ? "#1C1C1E" : "#A6A6AB", duration: 0.3, ease: "power1.out" }, t);
      };
      set(!!r.on, 0, true);
      (r.flips || []).forEach((f) => set(f.on, f.at));
    });
    enter(tl, c, at);
    return c;
  };

  /**
   * Poll card ("Сіздің пікіріңіз"): white option rows with radio rings + a comment input row with the channel avatar.
   * `pick` fills one radio at `pickAt`. Options arrive with the card (no empty container).
   * @param {{options:string[], pick?:number, pickAt?:number, placeholder?:string, avatar?:string, name?:string}} props
   */
  RSE.poll = function (host, props, tl, at) {
    const col = el("div", "rse-poll", host); if (props.mt != null) col.style.marginTop = props.mt + "px";
    const c = card(col, null, {}); c.style.padding = "28px";
    props.options.forEach((o, i) => {
      const op = el("div", "rse-opt", c, "<i><b></b></i>"); op.appendChild(document.createTextNode(o)); if (i) op.style.marginTop = "18px";
      enter(tl, op, at + 0.12 + i * 0.12, { y: 10, scale: 1 });
      if (props.pick === i && props.pickAt != null) ft(tl, op.querySelector("b"), { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }, props.pickAt);
    });
    enter(tl, c, at);
    if (props.placeholder) {
      const c2 = card(col, null, { mt: 22 }); c2.style.padding = "24px 28px";
      const r = el("div", "rse-input", c2); const av = el("div", "rse-logo", r); av.style.position = "relative"; av.style.width = av.style.height = "64px"; av.style.borderRadius = "50%";
      if (props.avatar) { const im = el("img", null, av); im.src = props.avatar; } else { const m = monogram(av, props.name); m.style.fontSize = "24px"; }
      el("div", "f", r).textContent = props.placeholder;
      enter(tl, c2, at + 0.3);
    }
    return col;
  };

  /**
   * 2×2 category tiles: line icon top-left, gold ↑ badge top-right, title + gold sub; each tile on its spoken word.
   * @param {{items:{icon?:string, title:string, sub?:string, at?:number}[], height?:number}} props
   */
  RSE.tiles = function (host, props, tl, at) {
    const g = el("div", "rse-tiles", host); if (props.mt != null) g.style.marginTop = props.mt + "px";
    props.items.forEach((it, i) => {
      const c = card(g, "rse-tile", { height: props.height || 300 }); c.style.padding = "34px";
      el("div", "ic", c, I[it.icon] || I.chart);
      el("div", "up", c, I.up);
      el("div", "tt", c).textContent = it.title;
      if (it.sub) el("div", "sb", c).textContent = it.sub;
      enter(tl, c, it.at ?? at + i * 0.3);
    });
    return g;
  };

  /* ------------------------------------------------------------------ *
   * Bottom caption track — literal VO, uppercase Inter Tight 800 48 px, ≤ 2 centred lines at y 1430
   * ------------------------------------------------------------------ */

  /**
   * Caption track. Each phrase is laid out at its FINAL position (balanced 1–2 lines, centred, ≤ column width); every word
   * reveals left→right letter by letter (opacity 0→1 + blur 6→0 per char, stagger spread over the spoken word, ≤ 0.45 s),
   * i.e. a soft wipe that follows the voice. A phrase disappears in ONE frame when the next phrase starts (no exit motion).
   * @param {HTMLElement} page RSE.page
   * @param {{phrases:({words:{w:string,t:number,e?:number}[]}|{text:string, at:number, stagger?:number})[], end?:number, y?:number}} props
   *        '/' inside `text` forces the line break; `end` hides the last phrase (default: stays).
   */
  RSE.caption = function (page, props, tl) {
    const box = el("div", "rse-cap", page.capl || page);
    if (props.y != null) box.style.top = props.y + "px";
    const maxW = box.clientWidth || 900;
    const phrases = props.phrases.map((p) => {
      if (p.words) return { words: p.words.map((o) => Object.assign({}, o)), br: p.br };
      const toks = p.text.split(/[ \t\n]+/).filter(Boolean); /* NBSP keeps "1 240" one word */ const words = []; let br = null; let k = 0;
      toks.forEach((tk) => { if (tk === "/") { br = words.length; return; } words.push({ w: tk, t: +(p.at + k * (p.stagger ?? 0.42)).toFixed(3) }); k++; });
      return { words, br };
    });
    const nodes = phrases.map((p, pi) => {
      const ph = el("div", "ph", box);
      const mk = (ws) => { const r = el("span", "row", ph); ws.forEach((w, i) => { const s = el("span", "wd", r); s.textContent = (i ? " " : "") + w.w.toUpperCase(); }); return r; };
      // balanced split: single row if it fits ≤ 62 % of the column, else the break minimising the longer row
      let br = p.br;
      if (br == null) {
        const probe = mk(p.words); const full = probe.getBoundingClientRect().width; const ws = [...probe.children].map((s) => s.getBoundingClientRect().width); probe.remove();
        if (full <= maxW * 0.62 || p.words.length < 2) br = p.words.length;
        else { let best = 1, bw = 1e9; for (let k = 1; k < ws.length; k++) { const a = ws.slice(0, k).reduce((x, y) => x + y, 0), b = full - a; const m = Math.max(a, b) + (b > a ? 1 : 0); if (m < bw) { bw = m; best = k; } } br = best; }
      }
      const rows = br >= p.words.length ? [p.words] : [p.words.slice(0, br), p.words.slice(br)];
      ph.innerHTML = "";
      const spans = [];
      rows.forEach((rw) => { const r = el("span", "row", ph); rw.forEach((w, i) => { const s = el("span", "wd", r); const txt = (i ? " " : "") + w.w.toUpperCase(); s.innerHTML = Array.from(txt).map((ch) => `<span class="c">${ch === " " ? " " : esc(ch)}</span>`).join(""); spans.push(s); }); });
      rows.flat().forEach((w, i) => {
        const nextT = (rows.flat()[i + 1] || {}).t ?? ((phrases[pi + 1] || {}).words || [{ t: w.t + 0.5 }])[0].t;
        const dur = Math.min(0.45, Math.max(0.16, (w.e ?? nextT) - w.t));
        const cs = spans[i].querySelectorAll(".c");
        tl.fromTo(cs, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power1.out", stagger: dur / Math.max(1, cs.length) }, w.t);
      });
      const shrink = Math.max(...[...ph.children].map((r) => r.getBoundingClientRect().width));
      if (shrink > maxW) ph.style.fontSize = Math.floor(48 * maxW / shrink) + "px";
      return ph;
    });
    nodes.forEach((ph, i) => {
      const nxt = phrases[i + 1];
      const end = nxt ? nxt.words[0].t - 0.02 : props.end;
      if (end != null) tl.set(ph, { autoAlpha: 0 }, end);
    });
    box.phrases = nodes;
    return box;
  };

  /* ------------------------------------------------------------------ *
   * Beats, transitions, layouts
   * ------------------------------------------------------------------ */

  /** A content beat (hidden until `at`). Returns the beat element; put layouts in it. */
  RSE.beat = function (page, props = {}, tl, at = 0) {
    const b = el("div", "rse-beat", page.beats || page);
    if (at > 0) { tl.set(b, { autoAlpha: 0 }, 0); tl.set(b, { autoAlpha: 1 }, at); }
    return b;
  };

  RSE.tx = {
    /**
     * Beat swap (the reference's only transition): the whole outgoing beat blurs 0→20 px and fades (0.21 s power1.in),
     * the page stays empty ≈0.17 s, then the next beat's elements blur in (kicker → headline → cards).
     * Header, tabs and caption track are NOT affected. Returns the time the next beat should start (`at` + 0.38).
     */
    blur(tl, out, inBeat, at, o = {}) {
      const m = RSE.M.exit;
      ft(tl, out, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: `blur(${m.blur}px)`, duration: o.dur ?? m.dur, ease: m.ease }, at);
      tl.set(out, { visibility: "hidden" }, at + (o.dur ?? m.dur) + 0.01);
      return at + (o.dur ?? m.dur) + (o.gap ?? RSE.M.gap);
    },
    /** Dissolve inside a beat (swap one component for another without emptying the page): 0.25 s crossfade + blur. */
    swap(tl, outEl, inEl, at) {
      ft(tl, outEl, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(12px)", duration: 0.22, ease: "power1.in" }, at);
      enter(tl, inEl, at + 0.12);
    },
  };

  /* Layouts (layouts.md catalogue). Each: RSE.layout.<id>(page, spec, tl, at) → beat (beat.block, beat.parts, beat.metrics).
   * The content block (kicker → last card) is measured and anchored at the reference top y 338 (or centred on spec.cy),
   * (spec.anchor overrides 338), clamped to y 300…1380 so the caption tier (1430–1542) stays clear; block ∪ caption centres at ≈ 936–940 (layouts.md §1). */
  const RHYTHM = { titleToVisual: 84, gap: 22 };
  RSE.layout = { RHYTHM };

  function block(page, spec, tl, at) {
    const beat = RSE.beat(page, {}, tl, spec.showAt ?? at);
    const b = el("div", "rse-m", beat);
    beat.block = b; beat.parts = {};
    return beat;
  }
  function finish(beat, spec) {
    const b = beat.block;
    const h = b.getBoundingClientRect().height;
    // default: anchor at the reference top (kicker line box y 338 → block + caption tier 1430–1542 centre ≤ 940);
    // spec.cy centres the block instead (statement).
    let top = spec.cy != null ? Math.round(spec.cy - h / 2) : (typeof spec.anchor === "number" ? spec.anchor : 338);
    top = Math.max(spec.minTop ?? 300, Math.min(top, (spec.maxBottom ?? 1380) - h));
    b.style.top = top + "px";
    beat.metrics = { top, bottom: top + h, height: h, centre: top + h / 2 };
    if (h < 600 && !spec.allowSmall && typeof console !== "undefined") console.warn(`RSE.layout: block ${Math.round(h)} px < 600 px (layouts.md §1)`);
    return beat;
  }
  function vis(host, v, tl, at, mt) {
    if (!v) return null;
    let node;
    if (typeof v === "function") node = v(host, tl, at);
    else { const fn = RSE[v.type]; if (!fn) throw new Error("RSE.layout: unknown visual type " + v.type); node = fn(host, Object.assign({}, v, { mt: v.mt ?? mt }), tl, v.at ?? at); }
    if (node && mt != null && v.mt == null && typeof v === "function") node.style.marginTop = mt + "px";
    return node;
  }
  function title(beat, spec, tl, at) {
    if (!spec.lines && !spec.headline) return null;
    const t = RSE.title(beat.block, { kicker: spec.kicker, lines: spec.lines || spec.headline, accent: spec.accent, size: spec.size }, tl, spec.titleAt ?? at);
    beat.parts.title = t; return t;
  }
  function visuals(beat, spec, tl, at, first) {
    const list = spec.visuals || (spec.visual ? [spec.visual] : []);
    beat.parts.visuals = list.map((v, i) => vis(beat.block, v, tl, at + (spec.visualDelay ?? 0.16) + i * 0.12, i === 0 ? first : (spec.gap ?? RHYTHM.gap)));
    return beat.parts.visuals;
  }

  /** stack — kicker + headline + 1–3 components stacked (default). spec: {kicker, lines, accent, visual|visuals[], cy}. */
  RSE.layout.stack = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at); title(beat, spec, tl, at); visuals(beat, spec, tl, at, RHYTHM.titleToVisual); return finish(beat, spec);
  };
  /** hero — one big news cover card (title lives inside the photo). spec: {cover:{src|label, kicker, lines, accent, subline, height}}. */
  RSE.layout.hero = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at);
    if (spec.lines) title(beat, spec, tl, at);
    beat.parts.cover = RSE.cover(beat.block, Object.assign({ mt: spec.lines ? RHYTHM.titleToVisual : 0 }, spec.cover), tl, spec.cover.at ?? at);
    return finish(beat, spec);
  };
  /** media — headline + photo/video card, optionally with a stats column on the right (ref "Ресми пост" beat).
   *  spec: {kicker, lines, accent, photo:{src|node|label, height}, stats:{items}|null, photoW=0.6, below:visual}. */
  RSE.layout.media = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at); title(beat, spec, tl, at);
    const row = el("div", null, beat.block); row.style.display = "flex"; row.style.gap = RHYTHM.gap + "px"; row.style.marginTop = RHYTHM.titleToVisual + "px";
    const pw = spec.stats ? Math.round(900 * (spec.photoW || 0.6)) : null;
    beat.parts.photo = RSE.photo(row, Object.assign({ width: pw || "100%", height: 764 }, spec.photo), tl, (spec.photo || {}).at ?? at + 0.16);
    if (spec.stats) { beat.parts.stats = RSE.stats(row, Object.assign({ rowH: 172 }, spec.stats), tl, spec.stats.at ?? at + 0.5); beat.parts.stats.style.flex = "1 1 0"; }
    if (spec.below) beat.parts.below = vis(beat.block, spec.below, tl, at + 0.5, RHYTHM.gap);
    return finish(beat, spec);
  };
  /** number — headline + optional numbered chips + data card (count-up "x / max" + bar). spec: {kicker, lines, accent, chips:{items}, data:{…dataCard}}. */
  RSE.layout.number = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at); title(beat, spec, tl, at);
    let mt = RHYTHM.titleToVisual;
    if (spec.chips) { beat.parts.chips = RSE.chips(beat.block, Object.assign({ mt }, spec.chips), tl, spec.chips.at ?? at + 0.16); mt = RHYTHM.gap; }
    beat.parts.data = RSE.dataCard(beat.block, Object.assign({ mt }, spec.data), tl, spec.data.at ?? at + 0.4);
    return finish(beat, spec);
  };
  /** list — headline + rows building downward (percentRows by default; or tiles / toggles via spec.visual). */
  RSE.layout.list = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at); title(beat, spec, tl, at);
    if (spec.rows) beat.parts.rows = RSE.percentRows(beat.block, { rows: spec.rows, mt: RHYTHM.titleToVisual }, tl, at + 0.2);
    else visuals(beat, spec, tl, at, RHYTHM.titleToVisual);
    return finish(beat, spec);
  };
  /** compare — headline + (optional chart/photo) + compare card "A → B". spec: {kicker, lines, accent, top:visual, compare:{left,right}}. */
  RSE.layout.compare = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at); title(beat, spec, tl, at);
    let mt = RHYTHM.titleToVisual;
    if (spec.top) { beat.parts.top = vis(beat.block, spec.top, tl, at + 0.16, mt); mt = RHYTHM.gap; }
    beat.parts.compare = RSE.compare(beat.block, Object.assign({ mt }, spec.compare), tl, spec.compare.at ?? at + 0.5);
    return finish(beat, spec);
  };
  /** statement — the question beat: big gold "?" + one question line, nothing else (≤ 1 per 6 beats). */
  RSE.layout.statement = function (page, spec, tl, at) {
    const beat = block(page, Object.assign({ allowSmall: true }, spec), tl, at);
    beat.parts.question = RSE.question(beat.block, spec, tl, at);
    return finish(beat, Object.assign({ allowSmall: true, cy: 820 }, spec));
  };
  /** visual-top — component(s) first, kicker + headline under them (asymmetric variety beat). */
  RSE.layout.visualTop = function (page, spec, tl, at) {
    const beat = block(page, spec, tl, at);
    visuals(beat, Object.assign({}, spec, { visualDelay: 0 }), tl, at, 0);
    const t = title(beat, Object.assign({}, spec, { titleAt: spec.titleAt ?? at + 0.35 }), tl, at + 0.35);
    if (t) t.style.marginTop = RHYTHM.titleToVisual + "px";
    return finish(beat, spec);
  };
  RSE.layout["visual-top"] = RSE.layout.visualTop;

  /** QA: bbox of every beat block at the current seek ({top,bottom,height,centre}). */
  RSE.audit = function (page) {
    return [...(page.beats || page).querySelectorAll(".rse-m")].map((b) => { const r = b.getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), centre: Math.round(r.top + r.height / 2) }; });
  };

  window.RSE = RSE;
})();
