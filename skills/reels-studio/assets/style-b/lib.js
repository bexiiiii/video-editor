/* reels-studio · Style B "iOS Keynote" component library — global `RSB`.
 *
 * Contract (references/contracts.md):  RSB.<component>(container, props, tl, at) → HTMLElement
 *   - builds DOM inside `container`, adds tweens to the paused GSAP timeline `tl`, starting at `at`
 *     (seconds, LOCAL composition time — all other times in props are absolute local times too);
 *   - every tween is seek-safe: entrances are fromTo (immediateRender) and every later state change
 *     is fromTo(immediateRender:false) with explicit start values (helper `ft`). No clocks, no
 *     Math.random (RS.rand), nothing exits on its own unless the spec says so.
 *   - layout is final before any reveal; measuring happens at BUILD time, so build after fonts load:
 *       await RSB.ready();  …build…;  window.__timelines[id] = tl;
 * Requires: GSAP 3, ../shared/runtime.js (global RS), tokens.css.
 * Numbers come from references/teardowns/style-b/*.md (cited per component).
 */
(function () {
  "use strict";
  const RS = window.RS;
  if (!RS) throw new Error("RSB needs shared/runtime.js (RS) loaded first");
  const RSB = { version: "1.1.0" };
  const el = RS.el;

  /* ------------------------------------------------------------------ *
   * Internal helpers
   * ------------------------------------------------------------------ */

  /** State change tween: explicit from/to, never renders before its start. */
  function ft(tl, target, from, to, at) {
    return tl.fromTo(target, from, Object.assign({ immediateRender: false }, to), at);
  }
  RSB.ft = ft;

  /** Absolute placement from props: {x,y} (left/top px), {center:true} centres horizontally, {z}.
   *  {flow:true} keeps the node in normal flow (position:relative, x/y ignored) — used by RSB.layout.* slots. */
  function place(node, p) {
    if (p.flow) {
      node.style.position = "relative";
    } else if (p.x != null || p.y != null || p.center) {
      node.style.position = "absolute";
      if (p.center) { node.style.left = "0"; node.style.right = "0"; node.style.marginLeft = "auto"; node.style.marginRight = "auto"; node.style.width = node.style.width || "max-content"; }
      else if (p.x != null) node.style.left = p.x + "px";
      if (p.y != null) node.style.top = p.y + "px";
    }
    if (p.z != null) node.style.zIndex = p.z;
    if (p.style && typeof p.style === "object") Object.assign(node.style, p.style);
    return node;
  }

  /** Normalise a word spec into [{w,t}]: string | [{w,t}] | {text, at, stagger}. */
  function words(spec, at, stagger) {
    if (spec == null) return [];
    if (Array.isArray(spec)) return spec;
    if (typeof spec === "object") return words(spec.words || spec.text, spec.at ?? at, spec.stagger ?? stagger);
    const st = stagger ?? 0.12;
    return String(spec).split(/\s+/).filter(Boolean).map((w, i) => ({ w, t: at + i * st }));
  }
  RSB.words = words;

  /** Teardown word reveal: blur 11→0, opacity 0→1 (≈.5 on frame 1 with power3.out), x +22→0, 0.14 s. */
  const WORD = { blur: 11, x: 22, dur: 0.14, ease: "power3.out" };
  function revealWords(target, ws, tl, o = {}) {
    return RS.words(target, ws, tl, Object.assign({ fromOpacity: 0, blur: WORD.blur, x: WORD.x, dur: WORD.dur, ease: WORD.ease }, o));
  }
  RSB.revealWords = revealWords;

  /** Component entrance (cards, pills): fade + rise + blur, 0.4 s power3.out (DeZREMAtvBf §5A). */
  function enter(tl, node, at, o = {}) {
    return tl.fromTo(node,
      { opacity: 0, y: o.y ?? 20, x: o.x ?? 0, scale: o.scale ?? 0.98, filter: `blur(${o.blur ?? 8}px)` },
      { opacity: 1, y: 0, x: 0, scale: 1, filter: "blur(0px)", duration: o.dur ?? 0.4, ease: o.ease || "power3.out" }, at);
  }
  RSB.enter = enter;

  /** Capsule pop: blurred blob sharpens, scale .8→1, back.out(1.6), 0.25 s (DeZREMAtvBf §5E). */
  function pop(tl, node, at, o = {}) {
    return tl.fromTo(node,
      { opacity: 0, scale: o.from ?? 0.8, filter: `blur(${o.blur ?? 6}px)` },
      { opacity: 1, scale: 1, filter: "blur(0px)", duration: o.dur ?? 0.25, ease: o.ease || "back.out(1.6)" }, at);
  }
  RSB.pop = pop;

  const CHECK_SVG = (stroke = "#fff", w = 3.2) =>
    `<svg viewBox="0 0 24 24"><path d="M5 12.5l4.6 4.6L19 7.7" fill="none" stroke="${stroke}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const BOOKMARK_SVG = (c) => `<svg viewBox="0 0 22 28"><path d="M2 3a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v23l-9-6-9 6z" fill="${c}"/></svg>`;

  /** Initials avatar ("Link HR" → "LH") — the fallback when no real photo is supplied. Never a drawn/emoji face. */
  function monogram(host, name) {
    const letters = String(name || "?").replace(/[@|·,]/g, " ").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
    const m = el("span", "rsb-mono", host); m.textContent = letters || "?";
    return m;
  }
  RSB.monogram = monogram;

  /** Wait for the fonts the library uses (call before building; measuring depends on it). */
  RSB.ready = function () {
    const f = document.fonts;
    if (!f || !f.load) return Promise.resolve();
    const specs = ["300 51px Inter", "400 40px Inter", "500 40px Inter", "600 40px Inter", "700 108px Inter", "800 64px Inter"];
    return Promise.all(specs.map((s) => f.load(s).catch(() => null))).then(() => f.ready);
  };

  /** Shrink a one-line element until its natural width ≤ maxW (min minPx). Build-time only. */
  function fitOneLine(line, inner, maxW, maxPx, minPx) {
    let px = maxPx;
    line.style.fontSize = px + "px";
    const w = inner.getBoundingClientRect().width;
    if (w > maxW) { px = Math.max(minPx, Math.floor(maxPx * maxW / w)); line.style.fontSize = px + "px"; }
    return px;
  }
  RSB.fitOneLine = fitOneLine;

  /* ------------------------------------------------------------------ *
   * Theme palette mirrored from tokens.css for values the chrome animates
   * ------------------------------------------------------------------ */
  const PAL = {
    light: { crumb: "#7F7D81", dot: "#8A8A8C", on: "#007AFF" },
    dark: { crumb: "#8E8E93", dot: "#8A8A8C", on: "#007AFF" },
    dark2: { crumb: "#98989A", dot: "#8A8A8C", on: "#007AFF" },
    dark3: { crumb: "#98989A", dot: "#8A8A8C", on: "#007AFF" },
    blue: { crumb: "#FFFFFF", dot: "rgba(255,255,255,0.55)", on: "#FFFFFF" },
    paper: { crumb: "#7F7D81", dot: "#8A8A8C", on: "#007AFF" },
  };
  RSB.PALETTE = PAL;

  /**
   * Brand palette (scripts/brand.py → lib/brand.js sets window.RS_BRAND before the libs load). Every lookup falls
   * back to the stock Apple value, so without a brand the output is identical. Semantic system colours (green =
   * ok, red = error, orange, yellow, grey) and Instagram's #0095F6 are never branded. See references/branding.md.
   */
  const brand = (k, d) => {
    const p = window.RS_BRAND && window.RS_BRAND.palette && window.RS_BRAND.palette.b;
    return p && p[k] != null ? p[k] : d;
  };
  ["light", "paper"].forEach((k) => { PAL[k].on = brand("dotOn", PAL[k].on); });
  ["dark", "dark2", "dark3"].forEach((k) => { PAL[k].on = brand("dotOnDark", PAL[k].on); });

  /* ================================================================== *
   * PAGE / BACKGROUND
   * ================================================================== */

  /**
   * Theme page (background + grid/rings + optional grain + content layer).
   * @param {HTMLElement} container
   * @param {{theme?:'light'|'dark'|'dark2'|'dark3'|'blue'|'paper', grain?:boolean, visible?:boolean}} props
   *   light/dark*: 130px grid (x=20+130k, y=50+130k, 2px); blue: concentric rings r=161n @ (540,980);
   *   dark2 gets grain by default. visible:false → starts at opacity 0 (a transition reveals it).
   * @returns {HTMLElement} page; `page.content` is where components go.
   */
  RSB.page = function (container, props = {}, tl, at) {
    const theme = props.theme || "light";
    const page = el("div", `rsb rsb-page theme-${theme}`, container);
    if (theme === "blue") el("div", "rsb-rings", page);
    else if (theme !== "paper") el("div", "rsb-grid", page);
    if (props.grain ?? theme === "dark2") el("div", "rsb-grain", page);
    page.content = el("div", "rsb-content", page);
    page.dataset.theme = theme;
    if (props.visible === false) page.style.opacity = "0";
    return page;
  };

  /* ================================================================== *
   * CHROME — breadcrumb + iOS page dots (always on)
   * ================================================================== */

  /**
   * Persistent chrome: 2-line breadcrumb at x=150 (series semibold / topic regular, 26px, 34px pitch)
   * and page dots (8px, 22px pitch, right edge x=930, centre y=212); active dot = 24×8 pill.
   * Each step animates together with the page dissolve (0.45 s power2.inOut).
   * @param {{series:string, topic:string, dots:number, theme?:string, active?:number, hidden?:boolean,
   *          steps?:Array<{at:number, active?:number, theme?:string, hidden?:boolean}>}} props
   */
  RSB.chrome = function (container, props, tl, at = 0) {
    const root = el("div", "rsb rsb-chrome", container);
    const crumb = el("div", "rsb-crumb", root);
    el("b", null, crumb).textContent = props.series || "";
    el("span", null, crumb).textContent = props.topic || "";
    const dotsWrap = el("div", "rsb-dots", root);
    const n = props.dots || 4;
    const dots = Array.from({ length: n }, () => el("i", null, dotsWrap));
    const dur = props.dur ?? 0.45;

    const stateOf = (s) => {
      const p = PAL[s.theme] || PAL.light;
      return { crumb: p.crumb, op: s.hidden ? 0 : 1, dots: dots.map((_, i) => i === s.active ? { width: 24, backgroundColor: p.on } : { width: 8, backgroundColor: p.dot }) };
    };
    let cur = { theme: props.theme || "light", active: props.active ?? -1, hidden: !!props.hidden };
    let s0 = stateOf(cur);
    crumb.style.color = s0.crumb; root.style.opacity = s0.op;
    dots.forEach((d, i) => { d.style.width = s0.dots[i].width + "px"; d.style.backgroundColor = s0.dots[i].backgroundColor; });

    (props.steps || []).forEach((st) => {
      const next = { theme: st.theme ?? cur.theme, active: st.active ?? cur.active, hidden: st.hidden ?? false };
      const a = stateOf(cur), b = stateOf(next);
      const o = { duration: dur, ease: "power2.inOut" };
      if (a.crumb !== b.crumb) ft(tl, crumb, { color: a.crumb }, Object.assign({ color: b.crumb }, o), st.at);
      if (a.op !== b.op) ft(tl, root, { opacity: a.op }, Object.assign({ opacity: b.op }, o), st.at);
      dots.forEach((d, i) => {
        const da = a.dots[i], db = b.dots[i];
        if (da.width !== db.width || da.backgroundColor !== db.backgroundColor) ft(tl, d, { width: da.width, backgroundColor: da.backgroundColor }, Object.assign({ width: db.width, backgroundColor: db.backgroundColor }, o), st.at);
      });
      cur = next;
    });
    root.crumb = crumb; root.dots = dots;
    return root;
  };

  /* ================================================================== *
   * TYPE STACK — kicker / headline / sub / second
   * ================================================================== */

  /**
   * One centred text line with literal word reveal (pre-laid-out, never re-centres).
   * @param {{cls?:'kicker'|'headline'|'sub'|'second'|'callout', words?:Array<{w,t}>, text?:string, at?:number,
   *          stagger?:number, highlight?:string[], hlClass?:string, fit?:boolean, maxPx?:number, minPx?:number,
   *          maxW?:number, emoji?:{e:string, at:number}, color?:string, mt?:number, x?:number, blur?:number}} props
   *   headline: 108px Bold, one line, shrink-to-fit ≤790px (min 72px).
   * @returns {HTMLElement} line; `line.inner` is the inline-block that wraps the words (for selection/strike).
   */
  RSB.line = function (container, props, tl, at = 0) {
    const cls = props.cls || "kicker";
    const line = el("div", `rsb-line rsb-${cls}`, container);
    if (props.mt != null) line.style.marginTop = props.mt + "px";
    if (props.color) line.style.color = props.color;
    const inner = el("span", "in", line);
    inner.style.display = "inline-block"; inner.style.position = "relative";
    const ws = words(props.words || props.text, props.at ?? at, props.stagger);
    const spans = revealWords(inner, ws, tl, { highlight: props.highlight, hlClass: props.hlClass || "hl-blue", x: props.x ?? WORD.x, blur: props.blur ?? WORD.blur });
    if (props.emoji) {
      const e = el("span", "emo emo-sup", inner, props.emoji.e);
      pop(tl, e, props.emoji.at, { from: 0.5, dur: 0.3 });
    }
    const fit = props.fit ?? (cls === "headline" || cls === "second");
    if (fit) {
      const maxPx = props.maxPx ?? (cls === "headline" ? 108 : 60);
      fitOneLine(line, inner, props.maxW ?? 790, maxPx, props.minPx ?? (cls === "headline" ? 72 : 44));
    }
    line.inner = inner; line.spans = spans;
    return line;
  };

  /**
   * Centred stack in the content column (x 145–935): [step capsule] → kicker → headline → sub → second.
   * Spacing reproduces DeZREMAtvBf/DeRXnpgtYe6: kicker→headline baselines ≈130px, headline→sub ≈95px.
   * @param {{top?:number, step?:{text,at,kind?}, kicker?:object, headline?:object, sub?:object, second?:object,
   *          gap?:{kh?:number, hs?:number}}} props  each line = props for RSB.line (words/text/at/highlight/emoji…)
   * @returns {HTMLElement} column; `.parts` = {step, kicker, headline, sub, second}; append slots with RSB.slot().
   */
  RSB.stack = function (container, props, tl, at = 0) {
    const col = place(el("div", "rsb-col", container), { y: props.top ?? 359 });
    const parts = {};
    const g = Object.assign({ sk: 58, kh: 34, hs: 34, ss: 34 }, props.gap || {});
    if (props.step) {
      const holder = el("div", null, col); holder.style.marginBottom = g.sk + "px";
      parts.step = RSB.capsule(holder, Object.assign({ kind: "step" }, props.step), tl, props.step.at ?? at);
    }
    if (props.kicker) parts.kicker = RSB.line(col, Object.assign({ cls: "kicker" }, props.kicker), tl, at);
    if (props.headline) parts.headline = RSB.line(col, Object.assign({ cls: "headline", mt: props.kicker ? g.kh : 0 }, props.headline), tl, at);
    if (props.sub) parts.sub = RSB.line(col, Object.assign({ cls: "sub", mt: g.hs }, props.sub), tl, at);
    if (props.second) parts.second = RSB.line(col, Object.assign({ cls: "second", mt: g.ss }, props.second), tl, at);
    col.parts = parts;
    return col;
  };

  /** Flow slot inside a stack/column for components (margin-top px). */
  RSB.slot = function (parent, mt = 80) {
    const s = el("div", "rsb-slot", parent);
    s.style.marginTop = mt + "px"; s.style.position = "relative"; s.style.display = "flex"; s.style.flexDirection = "column"; s.style.alignItems = "center";
    return s;
  };

  /**
   * Dim previous content when focus moves on (≈50 %, 0.3 s power1.out; DeZREMAtvBf 14.8 s).
   * @param {HTMLElement|HTMLElement[]} container  element(s) to dim
   * @param {{to?:number, dur?:number, from?:number}} props
   */
  RSB.dim = function (container, props = {}, tl, at) {
    const list = Array.isArray(container) ? container : [container];
    list.forEach((n) => ft(tl, n, { opacity: props.from ?? 1 }, { opacity: props.to ?? 0.5, duration: props.dur ?? 0.3, ease: "power1.out" }, at));
    return list[0];
  };

  /* ================================================================== *
   * CARDS
   * ================================================================== */

  /**
   * Light/dark card (790 wide, radius 40/44, 1px hairline, shadow below only; DeZREMAtvBf §5A/B).
   * Enter: opacity, y+20, scale .98, blur 8 → 0.4 s. Height grows 0.3 s power2.out when a new line starts.
   * @param {{meta?:{left?:string, right?:{text,kind,at}}, head?:{emoji?:string, text?:string|object},
   *          lines?:Array<{words|text, at, cls?:'quote'|'note', highlight?:string[]}>,
   *          rows?:Array<{text:string, at:number, capsule?:{text,kind,at}}>, slot?:boolean, width?:number,
   *          allowEmpty?:boolean, x?,y?,center?,flow?}} props
   *   No empty cards: if the first text starts > 0.35 s after `at`, the card enters 0.25 s before it (allowEmpty opts out).
   * @returns {HTMLElement} card; `.lines`, `.rows`, `.slotEl` (free area under the lines), `.badge`.
   */
  RSB.card = function (container, props = {}, tl, at) {
    const card = place(el("div", "rsb-card", container), props);
    if (props.width) card.style.width = props.width + "px";
    // never show an empty card (layouts.md §1): if the first text arrives > 0.35 s after `at`,
    // the card enters 0.25 s before that text instead.
    const firstT = [
      props.head ? words(props.head.words || props.head.text, props.head.at ?? at + 0.2, props.head.stagger)[0] : null,
      ...(props.lines || []).map((ln) => words(ln.words || ln.text, ln.at, ln.stagger)[0]),
      ...(props.rows || []).map((r) => words(r.words || r.text, r.at, r.stagger)[0]),
    ].filter((w) => w && w.t != null).map((w) => w.t);
    if (props.allowEmpty !== true && firstT.length && Math.min(...firstT) - at > 0.35) at = Math.min(...firstT) - 0.25;
    enter(tl, card, at);
    if (props.meta) {
      const m = el("div", "meta", card);
      el("span", null, m).textContent = props.meta.left || "";
      if (props.meta.right) card.badge = RSB.capsule(m, Object.assign({ kind: "redtext" }, props.meta.right), tl, props.meta.right.at);
    }
    if (props.head) {
      const h = el("div", "quote", card); h.style.display = "flex"; h.style.alignItems = "center"; h.style.gap = "16px";
      if (props.head.emoji) { const e = el("span", "emo", h, props.head.emoji); e.style.fontSize = "44px"; pop(tl, e, props.head.at ?? at, { from: 0.5 }); }
      const t = el("span", null, h); t.style.flex = "1";
      revealWords(t, words(props.head.words || props.head.text, props.head.at ?? at + 0.2, props.head.stagger), tl);
      if (props.head.right) { card.badge = RSB[props.head.right.type || "capsule"](h, props.head.right, tl, props.head.right.at); }
    }
    const lines = (props.lines || []).map((ln) => {
      const p = el("div", ln.cls || "quote", card);
      revealWords(p, words(ln.words || ln.text, ln.at, ln.stagger), tl, { highlight: ln.highlight, hlClass: "hl-blue" });
      return p;
    });
    const rows = (props.rows || []).map((r) => {
      const row = el("div", "row", card);
      const t = el("span", null, row); revealWords(t, words(r.words || r.text, r.at, r.stagger), tl);
      if (r.capsule) RSB.capsule(row, Object.assign({ kind: "green" }, r.capsule), tl, r.capsule.at);
      return row;
    });
    if (props.slot) { card.slotEl = el("div", "slot", card); }
    // auto-grow: measure card height with lines[0..i] visible, then tween between them
    if (lines.length > 1 && props.grow !== false) {
      const hs = lines.map((_, i) => { lines.forEach((l, j) => (l.style.display = j <= i ? "" : "none")); return card.offsetHeight; });
      lines.forEach((l) => (l.style.display = ""));
      card.style.height = hs[0] + "px";
      for (let i = 1; i < lines.length; i++) {
        const t0 = words(props.lines[i].words || props.lines[i].text, props.lines[i].at)[0].t;
        ft(tl, card, { height: hs[i - 1] }, { height: hs[i], duration: 0.3, ease: "power2.out" }, t0 - 0.05);
      }
    }
    card.lines = lines; card.rows = rows;
    return card;
  };

  /**
   * Section/quote card (DeRXnpgtYe6 "Maslahat 1/5"): 798 wide, radius 44, header 117px with tinted emoji
   * circle (accent @25%), title 33 Semibold, counter right; quote 48/70 Semibold left-aligned (emphasis
   * words in accent); bottom progress bar 10px that fills LINEARLY over the section (barFrom→barTo).
   * @param {{emoji:string, title:string, count?:string, accent?:string, quote:object|string, emphasis?:string[],
   *          barFrom?:number, barTo?:number, x?,y?,center?}} props
   */
  RSB.quoteCard = function (container, props, tl, at) {
    const accent = props.accent || "#34C759";
    const card = place(el("div", "rsb-qcard", container), props);
    card.style.setProperty("--acc", accent);
    enter(tl, card, at, { y: 34, dur: 0.3, ease: "expo.out" });
    const hd = el("div", "hd", card);
    RSB.emojiCircle(hd, { emoji: props.emoji, size: 70, tint: accent }, tl, at + 0.1);
    el("span", null, hd).textContent = props.title;
    if (props.count) el("span", "cnt", hd).textContent = props.count;
    const bd = el("div", "bd", card);
    const q = typeof props.quote === "object" && !Array.isArray(props.quote) ? props.quote : { text: props.quote, at: at + 0.35 };
    const spans = revealWords(bd, words(q.words || q.text, q.at ?? at + 0.35, q.stagger ?? 0.16), tl, { highlight: props.emphasis, hlClass: "em" });
    spans.forEach((s) => { if (s.classList.contains("em")) s.style.color = accent; });
    const bar = el("div", "bar", card); const fill = el("i", null, bar); fill.style.background = accent;
    tl.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: Math.max(0.1, (props.barTo ?? at + 3.5) - (props.barFrom ?? at)), ease: "none" }, props.barFrom ?? at);
    card.bar = fill;
    return card;
  };

  /**
   * Emoji in a tinted circle (accent at 25 % over the card colour; DeRXnpgtYe6).
   * @param {{emoji:string, size?:number, tint?:string, alpha?:number, bg?:string, x?,y?}} props
   */
  RSB.emojiCircle = function (container, props, tl, at) {
    const s = props.size || 70;
    const c = place(el("span", "rsb-ecircle", container), props);
    c.style.width = c.style.height = s + "px";
    c.style.background = props.bg || `color-mix(in srgb, ${props.tint || "#34C759"} ${Math.round((props.alpha ?? 0.25) * 100)}%, transparent)`;
    const e = el("span", "emo", c, props.emoji); e.style.fontSize = Math.round(s * 0.57) + "px";
    pop(tl, c, at, { from: 0.6, dur: 0.3 });
    return c;
  };

  /* ================================================================== *
   * CAPSULES / BADGES
   * ================================================================== */

  /**
   * Capsule / badge with Apple system colours. Pops (scale .8→1 + blur 6, back.out(1.6), 0.25 s).
   * kinds: green ("Bildi") · redtext ("Hammasi aytildi") · red ("SERIAL") · orange (timer) · blue · grey ·
   *        outline (on blue, "Masalan") · step ("1-qadam", theme-aware) · ok / bad (✓/✕ result, dark).
   * @param {{text:string, kind?:string, icon?:string, dot?:string, x?,y?,center?}} props
   */
  RSB.capsule = function (container, props, tl, at) {
    const kind = props.kind || "green";
    const c = place(el("span", `rsb-capsule ${kind}`, container), props);
    if (kind === "ok" || kind === "bad") el("span", "ic", c, kind === "ok" ? "✓" : "✕");
    if (props.dot) { const d = el("span", "dot", c); d.style.background = props.dot; }
    if (props.icon) el("span", "emo", c, props.icon);
    el("span", "tx", c).textContent = props.text;
    if (kind === "step" || kind === "outline") enter(tl, c, at, { y: 10, dur: 0.3, blur: 8 });
    else pop(tl, c, at);
    return c;
  };

  /**
   * Blue ✓ badge (48px, white ring) that pops on a selected tile corner, back.out(2) 0.25 s,
   * conventionally ≈0.8 s after selection (De1roE4t7Lf §5).
   * @param {{x?:number, y?:number, size?:number, color?:string, ring?:string}} props
   */
  RSB.checkBadge = function (container, props = {}, tl, at) {
    const b = place(el("div", "rsb-check", container), Object.assign({ x: 0, y: 0 }, props));
    const s = props.size || 48;
    b.style.width = b.style.height = s + "px";
    if (props.color) b.style.background = props.color;
    if (props.ring === false) b.style.boxShadow = "none"; else if (props.ring) b.style.boxShadow = `0 0 0 4px ${props.ring}`;
    b.innerHTML = CHECK_SVG();
    tl.fromTo(b, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, at);
    const path = b.querySelector("path");
    tl.fromTo(path, { strokeDasharray: 24, strokeDashoffset: 24 }, { strokeDashoffset: 0, duration: 0.2, ease: "power2.out" }, at + 0.08);
    return b;
  };

  /* ================================================================== *
   * WIDGETS
   * ================================================================== */

  /**
   * Audio-player pill 608×112 (DeZREMAtvBf §5D): rises (y+12, blur 6, 0.3 s), red bar scaleX 0→1 in
   * 0.22 s power2.inOut at at+0.28, time label fades 0.12 s at at+0.52.
   * @param {{time?:string, fillAt?:number, fillDur?:number, fillTo?:number, color?:string, scale?:number, x?,y?,center?,flow?}} props
   *   scale = layout-affecting size-up (CSS zoom), e.g. 1.3 → 790 px wide in RSB.layout.stack
   */
  RSB.player = function (container, props = {}, tl, at) {
    const p = place(el("div", "rsb-player", container), props);
    if (props.scale && props.scale !== 1) { p.style.zoom = props.scale; } // layout-affecting size-up (e.g. 1.3 → 790 px wide)
    el("div", "play", p);
    const tr = el("div", "track", p);
    const fill = el("div", "fill", tr); if (props.color) fill.style.background = props.color;
    const time = el("div", "time", p); time.textContent = props.time || "0:30 / 0:30";
    tl.fromTo(p, { opacity: 0, y: 12, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }, at);
    const fa = props.fillAt ?? at + 0.28, fd = props.fillDur ?? 0.22;
    tl.fromTo(fill, { scaleX: 0 }, { scaleX: props.fillTo ?? 1, duration: fd, ease: "power2.inOut" }, fa);
    tl.fromTo(time, { opacity: 0 }, { opacity: 1, duration: 0.12 }, fa + fd + 0.1);
    return p;
  };

  /**
   * Open-loop progress ring (DeZREMAtvBf §5G): Ø560, stroke 12 #0A7AFF round caps, grey track #E5E5EA,
   * draws clockwise from 10 o'clock over 0.9 s power2.inOut and STOPS at 80 %. With stop:1 + check:true it
   * is the green "closed loop" (Ø230, stroke 8, #34C759, filled check pops after closing).
   * @param {{size?:number, stroke?:number, color?:string, track?:string, stop?:number, dur?:number, startDeg?:number,
   *          label?:object, labelSize?:number, check?:boolean, x?,y?,center?}} props label = RSB.line props
   */
  RSB.ring = function (container, props = {}, tl, at) {
    const size = props.size || 560, sw = props.stroke || 12, r = (size - sw) / 2, C = 2 * Math.PI * r;
    const color = props.color || brand("ring", "#0A7AFF"), stop = props.stop ?? 0.8, dur = props.dur ?? 0.9;
    const w = place(el("div", "rsb-ring", container), props);
    w.style.width = w.style.height = size + "px";
    const rot = (props.startDeg ?? -60) - 90; // 0deg = 12 o'clock; 10 o'clock = -60deg
    w.innerHTML = `<svg viewBox="0 0 ${size} ${size}"><g transform="rotate(${rot} ${size / 2} ${size / 2})">
      <circle class="trk" cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${props.track || "#E5E5EA"}" stroke-width="${sw}"/>
      <circle class="arc" cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C}"/></g></svg>`;
    const trk = w.querySelector(".trk"), arc = w.querySelector(".arc");
    tl.fromTo(trk, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power1.out" }, at);
    tl.fromTo(arc, { strokeDashoffset: C }, { strokeDashoffset: C * (1 - stop), duration: dur, ease: "power2.inOut" }, at);
    if (props.label) {
      const lab = RSB.line(w, Object.assign({ cls: "headline", maxPx: props.labelSize || Math.round(size * 0.14), maxW: size * 0.78, minPx: 30 }, props.label), tl, at + dur);
      lab.style.position = "relative"; lab.style.width = "auto";
      w.label = lab;
    }
    if (props.check) {
      const b = RSB.checkBadge(w, { size: Math.round(size * 0.42), color, ring: false, x: size * 0.29, y: size * 0.29 }, tl, at + dur + 0.05);
      b.style.left = b.style.top = ""; b.style.position = "relative";
      w.check = b;
    }
    w.arc = arc;
    return w;
  };

  /**
   * Countdown timer capsule (orange #FF9F0A "00:59:59", De/ZREMAtvBf 20.0 s) that ticks down once per second.
   * @param {{from?:string|number, ticks?:number, kind?:string, x?,y?,center?}} props  from = "hh:mm:ss" or seconds;
   *        ticks = seconds to count down after the pop (default 5).
   */
  RSB.countdown = function (container, props = {}, tl, at) {
    const toSec = (v) => typeof v === "number" ? v : String(v).split(":").reduce((a, b) => a * 60 + Number(b), 0);
    const fmt = (s) => [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60].map((n) => String(n).padStart(2, "0")).join(":");
    const s0 = toSec(props.from ?? "00:59:59"), n = props.ticks ?? 5;
    const cap = RSB.capsule(container, Object.assign({ kind: props.kind || "orange", text: fmt(s0) }, props), tl, at);
    const tx = cap.querySelector(".tx");
    const o = { v: 0 };
    tl.fromTo(o, { v: 0 }, { v: n, duration: n, ease: "none", immediateRender: false, onUpdate: () => { tx.textContent = fmt(s0 - Math.floor(o.v)); } }, at + 0.3);
    return cap;
  };

  /**
   * Number counter with ease-out and vertical motion blur on the digits (DeRXnpgtYe6 0→30 in .75 s
   * power3.out; DelZA2dtAE6 budget 191 360→300 000 in ~1 s with blurred digits).
   * @param {{from?:number, to:number, dur?:number, ease?:string, size?:number, color?:string, sep?:string,
   *          suffix?:{text:string, size?:number, color?:string}, blur?:number, x?,y?,center?}} props
   */
  RSB.counter = function (container, props, tl, at) {
    const wrap = place(el("div", null, container), props);
    wrap.style.display = "inline-flex"; wrap.style.alignItems = "baseline";
    const num = el("span", "rsb-num", wrap);
    num.style.fontSize = (props.size || 120) + "px"; num.style.lineHeight = "1";
    if (props.color) num.style.color = props.color;
    const sep = props.sep ?? " ";
    const fmt = (v) => String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    const from = props.from ?? 0, dur = props.dur ?? 0.75;
    num.textContent = fmt(props.to); // final width reserved (tabular figures)
    num.style.minWidth = num.getBoundingClientRect().width + "px";
    num.style.textAlign = "right";
    num.textContent = fmt(from);
    if (props.suffix) { const s = el("span", null, wrap); s.textContent = props.suffix.text; s.style.fontSize = (props.suffix.size || 56) + "px"; s.style.fontWeight = "300"; s.style.color = props.suffix.color || "#8E8E93"; s.style.letterSpacing = "-0.02em"; }
    enter(tl, wrap, at - 0.15, { dur: 0.3 });
    const o = { v: from };
    tl.fromTo(o, { v: from }, { v: props.to, duration: dur, ease: props.ease || "power3.out", immediateRender: false, onUpdate: () => { num.textContent = fmt(o.v); } }, at);
    if (props.blur !== 0) RS.motionBlur(tl, num, at, dur, "y", props.blur ?? 6);
    wrap.num = num;
    return wrap;
  };

  /**
   * Calendar / day grid (De1roE4t7Lf "Har kuni — bir qism"): 6×5 glass squircles 82px r22 gap 30 that pop in,
   * then fill 1..N sequentially (≈55 ms per cell) into white tiles with #4A6FA5 numerals.
   * @param {{cols?:number, rows?:number, count?:number, fillAt?:number, stagger?:number, fillBg?:string,
   *          fillInk?:string, x?,y?,center?}} props
   */
  RSB.calendar = function (container, props = {}, tl, at) {
    const cols = props.cols || 6, rows = props.rows || 5, n = props.count ?? cols * rows;
    const g = place(el("div", "rsb-cal", container), props);
    g.style.gridTemplateColumns = `repeat(${cols}, 82px)`;
    const cells = Array.from({ length: cols * rows }, (_, i) => { const c = el("i", null, g); if (i < n) { const b = el("b", null, c); b.textContent = String(i + 1); b.style.color = props.fillInk || "#4A6FA5"; } return c; });
    tl.fromTo(cells, { opacity: 0, scale: 0.85, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out", stagger: 0.012 }, at);
    const fa = props.fillAt ?? at + 0.35, st = props.stagger ?? 0.055;
    const cs = getComputedStyle(cells[0]);
    cells.slice(0, n).forEach((c, i) => {
      ft(tl, c, { backgroundColor: cs.backgroundColor, borderColor: cs.borderTopColor },
        { backgroundColor: props.fillBg || "#FFFFFF", borderColor: props.fillBg || "#FFFFFF", duration: 0.14, ease: "power1.out" }, fa + i * st);
      ft(tl, c.firstChild, { opacity: 0 }, { opacity: 1, duration: 0.14, ease: "power1.out" }, fa + i * st);
    });
    g.cells = cells;
    return g;
  };

  /**
   * Colour grid fill (DeRXnpgtYe6 payoff): cols×rows tiles 98×99 r22 pitch 114, filled COLUMN by column
   * in Apple colours, starting with `startCol` (the example's column). Tiles are numbered column-major in display
   * order (column 1 = 1–5 …) and the number appears when its tile fills.
   * @param {{cols?:number, rows?:number, colors?:string[], startCol?:number, tileStagger?:number, colGap?:number,
   *          numbers?:boolean, x?,y?,center?}} props
   */
  RSB.colorGrid = function (container, props = {}, tl, at) {
    const cols = props.cols || 6, rows = props.rows || 5;
    const colors = props.colors || [brand("grid0", "#007AFF"), "#34C759", "#FF9500", "#FF3B30", "#FFCC00", "#FFFFFF"];
    const g = place(el("div", "rsb-cgrid", container), props);
    g.style.gridTemplateColumns = `repeat(${cols}, 98px)`;
    const tiles = [];
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) { const t = el("i", null, g); t.dataset.c = c; t.dataset.r = r; tiles.push(t); }
    tl.fromTo(tiles, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power3.out", stagger: 0.01 }, at);
    const empty = getComputedStyle(tiles[0]).backgroundColor;
    const order = Array.from({ length: cols }, (_, i) => (i + (props.startCol || 0)) % cols);
    const t0 = at + 0.45, ts = props.tileStagger ?? 0.06, cg = props.colGap ?? 0.32;
        order.forEach((c, k) => {
      for (let r = 0; r < rows; r++) {
        const t = tiles[r * cols + c];
        const bg = colors[c % colors.length];
        const ink = /^#?f{3,6}$/i.test(bg.replace("#", "")) || bg === "#FFCC00" ? "#000000" : "#FFFFFF";
        const at2 = t0 + k * cg + r * ts;
        ft(tl, t, { backgroundColor: empty }, { backgroundColor: bg, duration: 0.2, ease: "power1.out" }, at2);
        if (props.numbers !== false) {
          const b = el("b", null, t); b.textContent = String(c * rows + r + 1); b.style.color = ink; // column-major in display order
          ft(tl, b, { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power1.out" }, at2);
        }
      }
    });
    g.tiles = tiles;
    return g;
  };

  /* ================================================================== *
   * TEXT DEVICES
   * ================================================================== */

  /**
   * iOS text-selection highlight (DelZA2dtAE6 signature): start caret+knob (17px #007AFF dot, 3px caret
   * rising above cap height) → box rgba(0,122,255,.25) sweeps L→R in 5 frames (0.2 s) → end caret+knob
   * fades in 0.3 s later. Stays until the scene exits.
   * @param {HTMLElement} container  a line's `.inner` (inline-block wrapping the words)
   * @param {{pad?:number}} props
   */
  RSB.selection = function (container, props = {}, tl, at) {
    const pad = props.pad ?? 14;
    const s = el("div", "rsb-sel", container);
    // em units follow the line's font-size: box from ~6px above cap-height to just below the baseline
    Object.assign(s.style, { left: -pad + "px", right: -pad + "px", top: "0.10em", bottom: "0.02em", fontSize: "inherit" });
    const box = el("div", "box", s);
    const c1 = el("div", "caret", s); Object.assign(c1.style, { left: "-1.5px", top: "-0.16em", bottom: "0" });
    el("div", "knob", c1).style.top = "-8px";
    const c2 = el("div", "caret", s); Object.assign(c2.style, { right: "-1.5px", top: "0", bottom: "-0.12em" });
    el("div", "knob", c2).style.bottom = "-8px";
    tl.fromTo(c1, { opacity: 0, scaleY: 0.6 }, { opacity: 1, scaleY: 1, duration: 0.12, ease: "power2.out" }, at);
    tl.fromTo(box, { scaleX: 0 }, { scaleX: 1, duration: 0.2, ease: "power2.inOut" }, at + 0.02);
    tl.fromTo(c2, { opacity: 0 }, { opacity: 1, duration: 0.16, ease: "power1.out" }, at + 0.32);
    return s;
  };

  /**
   * Strike-through correction (DelZA2dtAE6 "👀 ko'rishlar"): 3px line draws L→R 0.25 s power2.out across the
   * word(s) while they dim to 45 %.
   * @param {HTMLElement} container  a line's `.inner`
   * @param {{color?:string, dim?:number, thickness?:number}} props
   */
  RSB.strike = function (container, props = {}, tl, at) {
    const line = el("div", "rsb-strike", container);
    Object.assign(line.style, { left: "-6px", right: "-6px", top: "57%", height: (props.thickness || 3) + "px", background: props.color || "#555" });
    tl.fromTo(line, { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, at);
    [...container.querySelectorAll(".w")].forEach((w) => ft(tl, w, { opacity: 1 }, { opacity: props.dim ?? 0.45, duration: 0.25 }, at));
    return line;
  };

  /* ================================================================== *
   * iOS CONTROLS
   * ================================================================== */

  /**
   * Segmented control (DelZA2dtAE6): pill track, white thumb with blue label slides between segments
   * (0.4 s power3.inOut). Enters with fade+rise.
   * @param {{items:string[], active?:number, steps?:Array<{at:number, active:number}>, x?,y?,center?}} props
   */
  RSB.segmented = function (container, props, tl, at) {
    const seg = place(el("div", "rsb-seg", container), props);
    const thumb = el("div", "thumb", seg);
    const spans = props.items.map((t) => { const s = el("span", null, seg); s.textContent = t; return s; });
    const geo = spans.map((s) => ({ x: s.offsetLeft, w: s.offsetWidth }));
    const ink = getComputedStyle(spans[0]).color, on = brand("segOn", "#007AFF");
    let cur = props.active ?? -1;
    thumb.style.width = (cur >= 0 ? geo[cur].w : geo[0].w) + "px";
    if (cur >= 0) { thumb.style.transform = `translateX(${geo[cur].x}px)`; spans[cur].style.color = on; } else thumb.style.opacity = "0";
    enter(tl, seg, at, { y: 16, dur: 0.35 });
    (props.steps || []).forEach((st) => {
      const a = cur, b = st.active, o = { duration: 0.4, ease: "power3.inOut" };
      if (a < 0) tl.fromTo(thumb, { opacity: 0, x: geo[b].x, width: geo[b].w, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.25, ease: "power2.out", immediateRender: false }, st.at);
      else ft(tl, thumb, { x: geo[a].x, width: geo[a].w }, Object.assign({ x: geo[b].x, width: geo[b].w }, o), st.at);
      if (a >= 0) ft(tl, spans[a], { color: on }, { color: ink, duration: 0.3 }, st.at);
      ft(tl, spans[b], { color: ink }, { color: on, duration: 0.3 }, st.at + 0.1);
      cur = b;
    });
    seg.thumb = thumb; seg.items = spans;
    return seg;
  };

  /**
   * iOS notification banner (DeZREMAtvBf §5C): white r36 714×152, 78px blue app squircle, title 32 Semibold,
   * "hozir" 24 grey, then text or 2 skeleton bars. Drops from y−20 with blur, grey→white, 0.35 s.
   * @param {{icon?:string, iconBg?:string, title:string, time?:string, text?:string, skeleton?:number,
   *          width?:number, from?:'top'|'bottom', x?,y?,center?}} props
   */
  RSB.notification = function (container, props, tl, at) {
    const n = place(el("div", "rsb-notif", container), props);
    if (props.width) n.style.width = props.width + "px";
    const app = el("div", "app", n);
    if (props.iconBg) app.style.background = props.iconBg;
    if (props.icon) el("span", "emo", app, props.icon);
    else app.innerHTML = `<svg width="46" height="42" viewBox="0 0 46 42"><path d="M23 3C11.4 3 3 10.2 3 19c0 4.9 2.6 9.2 6.8 12.1L8 39l8.6-4.7c2 .5 4.2.8 6.4.8 11.6 0 20-7.2 20-16S34.6 3 23 3z" fill="#fff"/></svg>`;
    const tx = el("div", "txt", n);
    const t = el("div", "t", tx); el("span", null, t).textContent = props.title; el("small", null, t).textContent = props.time ?? "hozir";
    if (props.text) el("div", "l", tx).textContent = props.text;
    for (let i = 0; i < (props.skeleton ?? (props.text ? 0 : 2)); i++) { const s = el("div", "sk", tx); s.style.width = i ? "62%" : "92%"; }
    const fromTop = props.from !== "bottom";
    tl.fromTo(n, { opacity: 0, y: fromTop ? -20 : 40, scale: 0.97, filter: "blur(8px)", backgroundColor: "#D9D9DE" },
      { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", backgroundColor: "#FFFFFF", duration: 0.35, ease: "expo.out" }, at);
    return n;
  };

  /**
   * iMessage typing bubble "•••" (blue #007AFF 120×64 on light, De1roE4t7Lf/DeRXnpgtYe6). Pops, then the dots
   * pulse with a finite, deterministic repeat for `dur` seconds.
   * @param {{color?:string, dur?:number, x?,y?,center?}} props
   */
  RSB.typing = function (container, props = {}, tl, at) {
    const b = place(el("div", "rsb-typing", container), props);
    if (props.color) b.style.background = props.color;
    const dots = [0, 1, 2].map(() => el("i", null, b));
    pop(tl, b, at, { from: 0.6, dur: 0.3 });
    const cyc = 0.6, reps = Math.max(0, Math.floor((props.dur ?? 2) / cyc) - 1);
    dots.forEach((d, i) => tl.fromTo(d, { opacity: 0.4, y: 0 }, { opacity: 1, y: -6, duration: cyc / 2, ease: "sine.inOut", yoyo: true, repeat: reps * 2 + 1 }, at + 0.25 + i * 0.15));
    return b;
  };

  /**
   * Chat bubble (grey iMessage #E9E9EB, 30px; DeRXnpgtYe6). Pops.
   * @param {{text:string, bg?:string, color?:string, x?,y?,center?}} props
   */
  RSB.bubble = function (container, props, tl, at) {
    const b = place(el("div", "rsb-bubble", container), props);
    b.textContent = props.text;
    if (props.bg) b.style.background = props.bg;
    if (props.color) b.style.color = props.color;
    tl.fromTo(b, { opacity: 0, scale: 0.7, y: 10, filter: "blur(6px)" }, { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "back.out(1.6)" }, at);
    b.style.transformOrigin = "0 100%";
    return b;
  };

  /**
   * Skeleton list rows → content (DelZA2dtAE6 1-qadam): rows enter with skeleton placeholders (grey tile +
   * 2 bars), each fills on its spoken word: skeleton blurs out 0.15 s, content blurs in from x+20 0.25 s expo.out.
   * @param {{rows:Array<{emoji:string, caption?:string, title:string, at:number}>, enterAt?:number, stagger?:number,
   *          height?:number, maxSkeleton?:number, x?,y?,center?}} props  a row's skeleton shows ≤ maxSkeleton (0.45 s) before its content
   */
  RSB.skeletonRows = function (container, props, tl, at) {
    const list = place(el("div", "rsb-rows", container), props);
    const rows = props.rows.map((r, i) => {
      const row = el("div", "rsb-lrow", list);
      if (props.height) row.style.height = props.height + "px";
      const sk = el("div", null, row);
      el("div", "sk-ico", sk);
      const bars = el("div", null, sk); bars.style.flex = "1";
      const b1 = el("div", "sk", bars); b1.style.width = "28%";
      const b2 = el("div", "sk", bars); b2.style.width = "64%"; b2.style.marginTop = "18px";
      const ct = el("div", null, row);
      el("div", "ico emo", ct, r.emoji);
      const tx = el("div", null, ct);
      if (r.caption) el("div", "cap", tx).textContent = r.caption;
      el("div", "ttl", tx).textContent = r.title;
      // skeleton is visible at most `maxSkeleton` (0.45 s) before its content — no long-lived empty rows
      const t0 = (props.enterAt ?? at) + i * (props.stagger ?? 0.08);
      enter(tl, row, Math.max(t0, r.at - (props.maxSkeleton ?? 0.45)), { y: 30, dur: 0.35 });
      ft(tl, sk, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(6px)", duration: 0.15 }, r.at);
      tl.fromTo(ct, { opacity: 0, x: 20, filter: "blur(8px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.25, ease: "expo.out" }, r.at + 0.05);
      return row;
    });
    list.rows = rows;
    return list;
  };

  /* ================================================================== *
   * CURSORS
   * ================================================================== */
  const GLOVE = `<svg width="96" height="120" viewBox="0 0 32 40"><path d="M11 2.2c1.7 0 3 1.3 3 3v8.3l.9-.1c1.4 0 2.5.7 3 1.8.5-.3 1-.4 1.6-.4 1.4 0 2.5.8 2.9 2 .4-.2.9-.3 1.4-.3 1.7 0 3 1.3 3 3v6.1c0 5.6-3.7 9.6-9 9.6h-2.6c-3.2 0-5.2-1.4-7-3.8L3.9 23c-.9-1.2-.7-2.9.5-3.8 1.1-.8 2.7-.7 3.6.3l.1.1V5.2c-.1-1.7 1.2-3 2.9-3z" fill="#fff" stroke="#000" stroke-width="1.6" stroke-linejoin="round"/><path d="M14 13.5v6M17.9 15v5M22.3 17v4" stroke="#000" stroke-width="1.3" stroke-linecap="round"/></svg>`;
  const ARROW = (c) => `<svg width="34" height="40" viewBox="0 0 17 20"><path d="M1 1v16.2l4.3-4.1 2.8 6 2.6-1.2-2.7-5.8h5.9z" fill="${c}" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>`;

  /**
   * Cursor that travels and taps (Dd1b9kEA-KL white glove, ~120px, 6px outline; or a coloured arrow).
   * Appears at path[0] (fade+blur), moves between points 6–8 frames power2.inOut, taps scale .85 over
   * 2 frames and back over 3 frames with an optional white ripple at the fingertip.
   * @param {{kind?:'glove'|'arrow', color?:string, path:Array<{x:number,y:number,at:number,dur?:number}>,
   *          taps?:number[], ripple?:boolean, rippleColor?:string}} props  x/y = hotspot in container px
   */
  RSB.cursor = function (container, props, tl, at) {
    const kind = props.kind || "glove";
    const c = el("div", "rsb-cursor", container, kind === "glove" ? GLOVE : ARROW(props.color || brand("cursor", "#0A7AFF")));
    const hot = kind === "glove" ? { x: 33, y: 7 } : { x: 2, y: 2 }; // fingertip / arrow tip offset
    c.style.transformOrigin = `${hot.x}px ${hot.y}px`;
    const P = props.path;
    const pos = (p) => ({ x: p.x - hot.x, y: p.y - hot.y });
    tl.fromTo(c, Object.assign({ opacity: 0, filter: "blur(6px)", scale: 1 }, pos({ x: P[0].x + 40, y: P[0].y + 60 })),
      Object.assign({ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }, pos(P[0])), P[0].at ?? at);
    for (let i = 1; i < P.length; i++) ft(tl, c, pos(P[i - 1]), Object.assign({ duration: P[i].dur ?? 0.27, ease: "power2.inOut" }, pos(P[i])), P[i].at);
    (props.taps || []).forEach((t) => {
      ft(tl, c, { scale: 1 }, { scale: 0.85, duration: 0.07, ease: "power2.in" }, t);
      ft(tl, c, { scale: 0.85 }, { scale: 1, duration: 0.11, ease: "power2.out" }, t + 0.07);
      if (props.ripple !== false) {
        // fingertip position at tap time = last path point at or before t
        const p = P.filter((q) => q.at <= t).pop() || P[0];
        RSB.ripple(container, { x: p.x, y: p.y, color: props.rippleColor }, tl, t + 0.04);
      }
    });
    return c;
  };

  /** Tap ripple: white 2–3px ring Ø90 that expands ×1.8 and fades (0.45 s). @param {{x,y,color?}} props */
  RSB.ripple = function (container, props, tl, at) {
    const r = place(el("div", "rsb-ripple", container), { x: props.x, y: props.y });
    if (props.color) r.style.borderColor = props.color;
    tl.fromTo(r, { opacity: 0.95, scale: 0.4 }, { opacity: 0, scale: 1.8, duration: 0.45, ease: "power2.out" }, at);
    return r;
  };

  /**
   * Figma multiplayer cursor + chat bubble (DeZREMAtvBf §5F): coloured arrow arrives first, then the bubble
   * (fill = cursor colour, white 34 Semibold, h68, full radius) pops scale .6→1 back.out(1.6) 0.3 s.
   * @param {{x:number, y:number, text:string, color?:string}} props  x/y = arrow tip
   */
  RSB.cursorBubble = function (container, props, tl, at) {
    const color = props.color || brand("bubble", "#0A7AFF");
    const g = place(el("div", null, container), { x: props.x, y: props.y });
    const cur = el("div", null, g, ARROW(color)); cur.style.position = "absolute"; cur.style.left = "-4px"; cur.style.top = "-4px";
    const b = el("div", "rsb-cbubble", g); b.textContent = props.text; b.style.background = color;
    if (!props.color && brand("bubbleInk", null)) b.style.color = brand("bubbleInk", null); b.style.left = "26px"; b.style.top = "30px";
    tl.fromTo(cur, { opacity: 0, x: -30, y: -24, filter: "blur(4px)" }, { opacity: 1, x: 0, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }, at);
    tl.fromTo(b, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)" }, at + 0.18);
    return g;
  };

  /* ================================================================== *
   * DEVICE / PROOF
   * ================================================================== */

  /**
   * iPhone 15 Pro mockup, deep-purple titanium (#3B2A3D, rim #6A4F6C), 565×1160 body, 24px bezel,
   * screen radius ~74, dynamic island, floor shadow. Holds an image, a <video> node (author the
   * framework-owned <video> statically in the HTML and pass it as `node`), or HTML.
   * enter 'rise': y+260, scale .85 → 1, 0.33 s expo.out (Dd1b9kEA-KL); 'pullout': scale 2→1 0.333 s expo.out
   * (Dd3Uz4Mgbn-). float: gentle 10–20px drift for `float` seconds.
   * Nothing supplied → labelled "ваше видео" footage slot on the screen. `flow:true` = in-flow (RSB.layout.media).
   * @param {{x?:number, y?:number, flow?:boolean, width?:number, src?:string, node?:HTMLElement, html?:string, label?:string,
   *          enter?:'rise'|'pullout'|'fade', floor?:boolean, float?:number}} props
   * @returns {HTMLElement} phone; `.screen` for overlays.
   */
  RSB.iphone = function (container, props = {}, tl, at) {
    const k = (props.width || 565) / 565;
    const holder = place(el("div", null, container), { flow: props.flow, x: props.x ?? Math.round((1080 - 565 * k) / 2), y: props.y ?? 380 });
    holder.style.width = 565 * k + "px"; holder.style.height = 1160 * k + "px";
    const scaler = el("div", null, holder); scaler.style.transformOrigin = "0 0"; scaler.style.transform = `scale(${k})`; scaler.style.position = "relative"; scaler.style.width = "565px"; scaler.style.height = "1160px";
    let floor = null;
    if (props.floor !== false) { floor = el("div", "rsb-floor", scaler); floor.style.left = "-37px"; floor.style.top = "1190px"; }
    const phone = el("div", "rsb-phone", scaler);
    [[-6, 250, 70], [-6, 350, 110], [565, 300, 160]].forEach(([x, y, h]) => { const b = el("div", "btn", phone); b.style.left = x + "px"; b.style.top = y + "px"; b.style.height = h + "px"; });
    const screen = el("div", "screen", phone);
    el("div", "island", screen);
    if (props.node) screen.appendChild(props.node);
    else if (props.src) { const img = el("img", null, screen); img.src = props.src; img.alt = ""; }
    else if (props.html) { const h = el("div", null, screen); h.style.position = "absolute"; h.style.inset = "0"; h.innerHTML = props.html; }
    else RSB.footage(screen, { compact: true, label: props.label }); // nothing supplied → labelled neutral slot, never a drawing
    const mode = props.enter || "rise";
    if (mode === "rise") {
      tl.fromTo(phone, { y: 260, scale: 0.85, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 0.33, ease: "expo.out" }, at);
      if (floor) tl.fromTo(floor, { opacity: 0, scaleX: 0.6 }, { opacity: 1, scaleX: 1, duration: 0.33, ease: "expo.out" }, at);
    } else if (mode === "pullout") {
      tl.fromTo(phone, { scale: 2 }, { scale: 1, duration: 0.333, ease: "expo.out" }, at);
      if (floor) tl.fromTo(floor, { opacity: 0 }, { opacity: 1, duration: 0.3 }, at + 0.2);
    } else enter(tl, phone, at);
    if (props.float) {
      const cyc = 2.4, reps = Math.max(0, Math.floor(props.float / (cyc / 2)) - 1);
      ft(tl, holder, { y: 0 }, { y: -14, duration: cyc / 2, ease: "sine.inOut", yoyo: true, repeat: reps }, at + 0.4);
    }
    holder.phone = phone; holder.screen = screen;
    return holder;
  };

  /**
   * CTA follow pill (Dd1b9kEA-KL / Dd3Uz4Mgbn-): B&W avatar tile pops (0→1.15→1, 5 frames) → pill unrolls right
   * (206→619, back.out(1.2) 0.3 s) with the blue #227DE5 button bar → name types word by word with a text cursor →
   * button pressed: scale .5 + #2B2B2B over 4 frames (subscribed chip). Off-white #EEEEEC, radius 70, white glow.
   * Identity comes from props (brief → name/handle/photo); never hard-code a creator. No `avatar` photo → initials
   * monogram (`monogram` or derived from name[0]) — never a drawn or emoji face.
   * @param {{x?:number, y?:number, flow?:boolean, avatar?:string, monogram?:string, avatarEmoji?:string, name:string[], button?:string,
   *          unrollAt?:number, typeAt?:number, pressAt?:number, width?:number}} props
   */
  RSB.ctaFollow = function (container, props, tl, at) {
    const W = props.width || 619;
    const pill = place(el("div", "rsb cta-wrap", container), { flow: props.flow, x: props.x ?? Math.round((1080 - W) / 2), y: props.y ?? 1184 });
    if (props.flow) { pill.style.width = W + "px"; pill.style.height = "206px"; }
    const box = el("div", "rsb-cta", pill); box.style.position = "relative"; box.style.width = W + "px";
    const ava = el("div", "ava", box);
    if (props.avatar) { const i = el("img", null, ava); i.src = props.avatar; i.alt = ""; }
    else if (props.avatarEmoji) el("span", "emo", ava, props.avatarEmoji);
    else monogram(ava, props.monogram || (props.name || [])[0] || props.handle);
    const name = el("div", "name", box);
    const lines = (props.name || []).map((t) => el("div", null, name));
    const btn = el("div", "btn", box); const bt = el("span", null, btn); bt.textContent = props.button || "Obuna bo'ling";
    const caret = el("span", null, name); Object.assign(caret.style, { position: "absolute", width: "3px", height: "40px", background: brand("cta", "#227DE5"), left: "0", top: "2px" });
    const ua = props.unrollAt ?? at + 0.65, ta = props.typeAt ?? ua + 0.3, pa = props.pressAt ?? ta + 1.3;
    // 1. avatar tile pop (box clipped to the avatar square)
    tl.fromTo(box, { width: 206, scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "back.out(2.2)" }, at);
    // 2. unroll
    ft(tl, box, { width: 206 }, { width: W, duration: 0.3, ease: "back.out(1.2)" }, ua);
    tl.fromTo(btn, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.25, ease: "power3.out" }, ua + 0.12);
    // 3. type name word by word
    let t = ta, lastSpan = null;
    lines.forEach((ln, i) => {
      const ws = props.name[i].split(/\s+/).map((w) => ({ w, t: (t += 0.12) - 0.12 }));
      const spans = RS.words(ln, ws, tl, { fromOpacity: 0, blur: 4, x: 0, dur: 0.06, ease: "none" });
      lastSpan = spans[spans.length - 1] || lastSpan;
      t += 0.08;
    });
    tl.fromTo(caret, { opacity: 0 }, { opacity: 1, duration: 0.01 }, ta);
    ft(tl, caret, { opacity: 1 }, { opacity: 0, duration: 0.01 }, t + 0.3);
    // caret follows the typed text: place at end of name block
    caret.style.left = "auto"; caret.style.right = "-8px"; caret.style.top = "auto"; caret.style.bottom = "4px";
    // 4. press → dark chip
    ft(tl, btn, { scale: 1, backgroundColor: brand("cta", "#227DE5") }, { scale: 0.5, backgroundColor: "#2B2B2B", duration: 0.17, ease: "power2.in" }, pa);
    ft(tl, bt, { opacity: 1 }, { opacity: 0, duration: 0.1 }, pa);
    pill.box = box; pill.button = btn;
    return pill;
  };

  /**
   * Fake Instagram profile card (De1roE4t7Lf CTA): white r44 780 wide; gradient story ring avatar, handle +
   * verified, uppercase bio; stats count up (posts, followers) over 0.6 s; "Obuna bo'lish" button fades in;
   * tap ripple → button turns grey "Obuna bo'ldingiz", green ✓ pops, followers tick +1.
   * No `avatar` photo → initials monogram. `flow:true` = in-flow (layout slots); the chip sits inside the card.
   * @param {{x?:number, y?:number, flow?:boolean, avatar?:string, monogram?:string, avatarEmoji?:string, handle:string, verified?:boolean, bio?:string,
   *          posts?:[number,number], followers?:[number,number], following?:string|number, button?:string, done?:string,
   *          buttonAt?:number, tapAt?:number, chip?:{text:string, icon?:string, at:number}}} props
   */
  RSB.igProfile = function (container, props, tl, at) {
    const card = place(el("div", "rsb rsb-ig", container), { flow: props.flow, x: props.x ?? 150, y: props.y ?? 1045 });
    const top = el("div", "top", card);
    const ring = el("div", "ring", top); const av = el("div", null, ring);
    if (props.avatar) { const i = el("img", null, av); i.src = props.avatar; i.alt = ""; Object.assign(i.style, { width: "100%", height: "100%", objectFit: "cover" }); }
    else if (props.avatarEmoji) el("span", "emo", av, props.avatarEmoji);
    else monogram(av, props.monogram || props.bio || props.handle);
    const info = el("div", null, top);
    const h = el("div", "handle", info); el("span", null, h).textContent = props.handle;
    if (props.verified !== false) el("span", "verified", h, "✓");
    if (props.bio) el("div", "bio", info).textContent = props.bio;
    const stats = el("div", "stats", info);
    const stat = (v, label) => { const d = el("div", null, stats); const b = el("b", null, d); b.textContent = String(v); el("span", null, d).textContent = label; return b; };
    const P = props.posts || [12, 22], F = props.followers || [0, 473];
    const pb = stat(P[0], "posts"), fb = stat(F[0], "followers"); stat(props.following ?? 1, "following");
    const follow = el("div", "follow", card);
    const f1 = el("span", null, follow); f1.textContent = props.button || "Obuna bo'lish";
    const f2 = el("span", null, follow); f2.textContent = props.done || "Obuna bo'ldingiz"; f2.style.color = "#000";
    enter(tl, card, at, { y: 40, dur: 0.35 });
    const cnt = (b, a, z, t, d) => { const o = { v: a }; tl.fromTo(o, { v: a }, { v: z, duration: d, ease: "power2.out", immediateRender: false, onUpdate: () => { b.textContent = String(Math.round(o.v)); } }, t); };
    cnt(pb, P[0], P[1], at + 0.3, 0.6); cnt(fb, F[0], F[1], at + 0.3, 0.6);
    const ba = props.buttonAt ?? at + 1.0, ta = props.tapAt ?? ba + 1.4;
    tl.fromTo(follow, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, ba);
    tl.fromTo(f2, { opacity: 0 }, { opacity: 0, duration: 0.01 }, at); // hidden until tap
    RSB.ripple(follow, { x: 345, y: 42, color: "rgba(255,255,255,.95)" }, tl, ta);
    ft(tl, follow, { backgroundColor: "#0095F6", scale: 1 }, { backgroundColor: "#EFEFEF", duration: 0.2, ease: "power1.out" }, ta + 0.05);
    ft(tl, follow, { scale: 1 }, { scale: 0.97, duration: 0.07, yoyo: true, repeat: 1 }, ta);
    ft(tl, f1, { opacity: 1 }, { opacity: 0, duration: 0.12 }, ta + 0.05);
    ft(tl, f2, { opacity: 0 }, { opacity: 1, duration: 0.15 }, ta + 0.12);
    cnt(fb, F[1], F[1] + 1, ta + 0.15, 0.01);
    const chk = RSB.checkBadge(follow, { x: 690 - 24, y: -14, size: 40, color: "#34C759", ring: "#fff" }, tl, ta + 0.2);
    follow.style.overflow = "visible";
    if (props.chip) {
      const chip = RSB.capsule(card, { text: props.chip.text, icon: props.chip.icon, kind: "grey", x: 60, y: -64 }, tl, props.chip.at);
      Object.assign(chip.style, { background: "#FFFFFF", color: "#000", boxShadow: "0 6px 16px rgba(0,0,0,.18)" });
      card.chip = chip;
    }
    card.follow = follow; card.check = chk;
    return card;
  };

  /**
   * "Saqlash" → "Saqlandi" pill (DelZA2dtAE6 CTA): appears frosted grey → white; on tap a white ring ripple
   * expands and the pill turns #007AFF "Saqlandi" (filled bookmark).
   * @param {{x?:number, y?:number, flow?:boolean, text?:string, done?:string, tapAt?:number}} props
   */
  RSB.savePill = function (container, props, tl, at) {
    const p = place(el("div", "rsb rsb-save", container), { flow: props.flow, x: props.x ?? 165, y: props.y ?? 1418 });
    const off = el("div", "off", p, BOOKMARK_SVG("none") + `<span>${props.text || "Saqlash"}</span>`);
    off.querySelector("path").setAttribute("stroke", "#000"); off.querySelector("path").setAttribute("stroke-width", "2.4");
    const on = el("div", "on", p, BOOKMARK_SVG("#fff") + `<span>${props.done || "Saqlandi"}</span>`);
    tl.fromTo(p, { opacity: 0, scale: 0.9, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }, at);
    tl.fromTo(off, { backgroundColor: "rgba(200,200,205,0.6)" }, { backgroundColor: "#FFFFFF", duration: 0.4, ease: "power1.out" }, at);
    tl.fromTo(on, { opacity: 0 }, { opacity: 0, duration: 0.01 }, at);
    const ta = props.tapAt ?? at + 1;
    ft(tl, p, { scale: 1 }, { scale: 0.94, duration: 0.07, yoyo: true, repeat: 1, ease: "power2.inOut" }, ta);
    ft(tl, on, { opacity: 0 }, { opacity: 1, duration: 0.15 }, ta + 0.05);
    ft(tl, off, { opacity: 1 }, { opacity: 0, duration: 0.15 }, ta + 0.05);
    RSB.ripple(p, { x: p.offsetWidth / 2, y: 32 }, tl, ta); // ripple lives in the pill → correct in flow and absolute modes
    return p;
  };

  /* ================================================================== *
   * TALKING-HEAD HELPERS
   * ================================================================== */

  /**
   * Talking-head caption line (Dd1b9kEA-KL / Dd3Uz4Mgbn-): one centred line ≤32 chars in the chest band
   * (y 880–1460), 62px weight 500, tracking −0.05em. Words are pre-placed; each goes grey→full colour with a
   * 5px blur and optional x-settle over 0.21 s. Phrases swap in ONE frame (no exit animation).
   * @param {{y?:number, size?:number, color?:string, from?:string, settle?:number,
   *          phrases:Array<{words?:Array<{w,t}>, text?:string, at?:number, stagger?:number}>}} props
   */
  RSB.caption = function (container, props, tl, at) {
    const cap = place(el("div", "rsb rsb-caption", container), { y: props.y ?? 1398 });
    if (props.size) cap.style.fontSize = props.size + "px";
    const col = props.color || "#FFFFFF", from = props.from || "#9A9A9A";
    const phs = props.phrases.map((ph) => {
      const d = el("div", "ph", cap);
      const ws = words(ph.words || ph.text, ph.at ?? at, ph.stagger ?? 0.22);
      const spans = RS.words(d, ws, tl, { fromOpacity: 0, blur: 5, x: props.settle ?? 0, dur: 0.21, ease: "power3.out" });
      spans.forEach((s, i) => tl.fromTo(s, { color: from }, { color: col, duration: 0.21, ease: "power2.out", immediateRender: false }, ws[i].t));
      return { d, t0: ws[0].t };
    });
    for (let i = 0; i < phs.length - 1; i++) tl.set(phs[i].d, { opacity: 0 }, phs[i + 1].t0);
    return cap;
  };

  /**
   * Uppercase title sticker + emoji (De1roE4t7Lf hook): white #FBFBFB r24 780 wide at x 135, ~64px Heavy uppercase,
   * line pitch 65, emoji 🍿 ≈110px overlapping the top-right corner. Frosted → sharp in 0.2 s.
   * Font shrinks (64→44) until the text fits `maxLines` (2).
   * @param {{text:string, emoji?:string, y?:number, size?:number, maxLines?:number}} props
   */
  RSB.sticker = function (container, props, tl, at) {
    const s = place(el("div", "rsb rsb-sticker", container), { y: props.y ?? 1050 });
    const txt = el("span", null, s); txt.textContent = props.text;
    // fit to maxLines (default 2) — Inter Heavy caps run ~6 % wider than SF Pro Heavy
    const maxLines = props.maxLines ?? 2;
    for (let fs = props.size || 64; fs >= 44; fs -= 2) {
      s.style.fontSize = fs + "px";
      if (Math.round(txt.getBoundingClientRect().height / fs) <= maxLines) break;
    }
    const e = props.emoji !== "" ? el("span", "emo", s, props.emoji || "🍿") : null;
    tl.fromTo(s, { opacity: 0, filter: "blur(8px)", scale: 0.98 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.2, ease: "power2.out" }, at);
    if (e) tl.fromTo(e, { opacity: 0, scale: 0.4, rotation: -10 }, { opacity: 1, scale: 1, rotation: 8, duration: 0.35, ease: "back.out(2)" }, at + 0.12);
    return s;
  };

  /** Lens edge blur overlay for footage (sharp ellipse over face/torso, blurred edges). */
  RSB.lens = function (container, props = {}) {
    const l = el("div", "rsb-lens", container);
    if (props.blur) l.style.backdropFilter = l.style.webkitBackdropFilter = `blur(${props.blur}px)`;
    return l;
  };

  /* ================================================================== *
   * FOOTAGE — real talking-head video / photo, or a labelled neutral slot
   * ================================================================== */
  const CAMERA_SVG = `<svg viewBox="0 0 48 36" width="64" height="48"><rect x="2" y="7" width="32" height="24" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M34 15l11-6v18l-11-6z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;

  /**
   * Talking-head footage layer. A human on screen is ALWAYS real material (layouts.md §4): pass `node` (a
   * framework-owned <video> authored statically in the HTML — HyperFrames owns playback) or `src` (photo/still).
   * Without a source it renders a clearly labelled neutral "footage slot": dark frosted rounded rectangle with a
   * camera icon and the label "ваше видео" — never a drawn figure.
   * @param {HTMLElement} container  usually `page.content`
   * @param {{node?:HTMLElement, src?:string, fit?:'cover'|'contain', lens?:number|boolean,
   *          slot?:{x:number,y:number,w:number,h:number}, label?:string, sub?:string, compact?:boolean}} props
   *   slot = where the placeholder rectangle sits (default: face+torso area x 140, y 300, 800×1000);
   *   lens = edge-blur px for real footage (Dd1b9kEA-KL §1); compact = small inline slot (inside a phone/screenshot).
   * @returns {HTMLElement} layer; `.media` (video/img) or `.slot` (placeholder).
   */
  RSB.footage = function (container, props = {}, tl, at) {
    const f = el("div", "rsb rsb-footage" + (props.compact ? " compact" : ""), container);
    if (props.node || props.src) {
      const m = props.node || el("img", null, null);
      if (!props.node) { m.src = props.src; m.alt = ""; }
      f.appendChild(m); m.classList.add("media"); m.style.objectFit = props.fit || "cover";
      f.media = m;
      if (props.lens) RSB.lens(f, { blur: props.lens === true ? 14 : props.lens });
    } else {
      f.classList.add("empty");
      const s = el("div", "slot", f);
      if (!props.compact) {
        const r = Object.assign({ x: 140, y: 300, w: 800, h: 1000 }, props.slot || {});
        Object.assign(s.style, { left: r.x + "px", top: r.y + "px", width: r.w + "px", height: r.h + "px" });
      }
      el("div", "ic", s, CAMERA_SVG);
      el("div", "lb", s).textContent = props.label || "ваше видео";
      if (!props.compact) el("div", "sb", s).textContent = props.sub || "talking head · 9:16";
      f.slot = s;
    }
    if (tl && at != null) tl.fromTo(f, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power1.out" }, at);
    return f;
  };

  /* ================================================================== *
   * LIST ROWS / COMPARE / SCREENSHOT (used by the layouts, usable alone)
   * ================================================================== */

  /**
   * Rows that build downward (DelZA2dtAE6 "1-qadam", DeZREMAtvBf 39.5 s timeline). Each row appears WITH its
   * content on its word (`at`): rise y+30 + blur 8 → 0.35 s power3.out. Optional skeleton morph: the row shows
   * grey skeleton bars for `skeleton` seconds (≤ 0.45) before the content blurs in.
   * @param {{rows:Array<{emoji?:string, num?:string|number, caption?:string, title:string, at:number,
   *          right?:{type?:'capsule'|'check', text?:string, kind?:string, at?:number}}>,
   *          variant?:'cards'|'timeline', width?:number, rowH?:number, gap?:number, skeleton?:number, x?,y?,center?,flow?}} props
   * @returns {HTMLElement} list; `.rows` = row elements.
   */
  RSB.listRows = function (container, props, tl, at) {
    const tlStyle = (props.variant || props.style) === "timeline";
    const list = place(el("div", "rsb-list" + (tlStyle ? " timeline" : ""), container), props);
    const W = props.width || (tlStyle ? 700 : 790), H = props.rowH || 168, G = props.gap ?? 30;
    list.style.gap = G + "px";
    let rail = null;
    if (tlStyle) { rail = el("div", "rail", list); rail.style.top = H / 2 + "px"; rail.style.bottom = H / 2 + "px"; }
    const rows = props.rows.map((r, i) => {
      const row = el("div", "rsb-lrow", list);
      row.style.width = W + "px"; row.style.height = H + "px";
      const ct = el("div", null, row);
      if (r.emoji) el("div", "ico emo", ct, r.emoji);
      else if (r.num != null) el("div", "ico num", ct).textContent = String(r.num);
      const tx = el("div", null, ct); tx.style.flex = "1";
      if (r.caption) el("div", "cap", tx).textContent = r.caption;
      el("div", "ttl", tx).textContent = r.title;
      let dot = null;
      if (tlStyle) { dot = el("div", "dot", row); dot.textContent = String(i + 1); }
      const sk = props.skeleton ? Math.min(0.45, props.skeleton) : 0;
      enter(tl, row, r.at - 0.1 - sk, { y: 30, dur: 0.35 });
      if (sk) {
        const s = el("div", "skel", row);
        el("div", "sk-ico", s); const bars = el("div", null, s); bars.style.flex = "1";
        el("div", "sk", bars).style.width = "30%"; const b2 = el("div", "sk", bars); b2.style.width = "62%"; b2.style.marginTop = "18px";
        ft(tl, s, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(6px)", duration: 0.15 }, r.at - 0.05);
        tl.fromTo(ct, { opacity: 0, x: 20, filter: "blur(8px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.25, ease: "expo.out" }, r.at);
      }
      if (dot) pop(tl, dot, r.at - 0.1, { from: 0.4 });
      if (r.right) {
        const ra = r.right.at ?? r.at + 0.35;
        if (r.right.type === "check") { const b = RSB.checkBadge(row, { size: 52, ring: false, color: r.right.color }, tl, ra); b.style.left = ""; b.style.right = "30px"; b.style.top = (H - 52) / 2 + "px"; }
        else { const c = RSB.capsule(ct, Object.assign({ kind: "green" }, r.right), tl, ra); c.style.flex = "none"; }
      }
      return row;
    });
    if (rail) tl.fromTo(rail, { scaleY: 0 }, { scaleY: 1, duration: Math.max(0.3, props.rows[props.rows.length - 1].at - props.rows[0].at), ease: "none" }, props.rows[0].at);
    list.rows = rows;
    return list;
  };

  /**
   * Two-way comparison (DeRXnpgtYe6 "Oldin/Keyin", DeZREMAtvBf 53.6 s ✓/✕): two tiles side by side (columns) or
   * stacked (rows). Each tile = tag capsule + quote + optional retention meter that fills. At `pickAt` the winner
   * gets a ✓ badge and lifts, the loser dims to 50 %.
   * @param {{mode?:'columns'|'stacked', left:Side, right:Side, pick?:'left'|'right', pickAt?:number, width?:number,
   *          x?,y?,center?,flow?}} props
   *   Side = {tag?:{text,kind}, emoji?:string, quote:string|{words|text,at}, meter?:{value:number(0–1), label?:string,
   *          color?:string}, at:number}
   * @returns {HTMLElement} wrapper; `.left`, `.right` tiles.
   */
  RSB.compare = function (container, props, tl, at) {
    const mode = props.mode || "columns";
    const w = place(el("div", "rsb-cmp " + mode, container), props);
    w.style.width = (props.width || 790) + "px";
    const tile = (s) => {
      const t = el("div", "side", w);
      enter(tl, t, s.at, { y: 40, dur: 0.4 });
      if (s.tag) RSB.capsule(t, Object.assign({ kind: "grey" }, s.tag), tl, s.at + 0.05);
      if (s.emoji) { const e = el("div", "emo big", t, s.emoji); pop(tl, e, s.at + 0.1, { from: 0.5, dur: 0.3 }); }
      const q = el("div", "q", t);
      const qs = typeof s.quote === "object" ? s.quote : { text: s.quote };
      revealWords(q, words(qs.words || qs.text, qs.at ?? s.at + 0.3, qs.stagger ?? 0.1), tl);
      if (s.meter) {
        const m = el("div", "meter", t); const bar = el("div", "bar", m); const fill = el("i", null, bar);
        fill.style.background = s.meter.color || "#34C759";
        const lab = el("div", "ml", m); lab.textContent = s.meter.label || Math.round(s.meter.value * 100) + "%";
        tl.fromTo(fill, { scaleX: 0 }, { scaleX: s.meter.value, duration: 0.7, ease: "power2.out" }, s.at + 0.5);
        tl.fromTo(lab, { opacity: 0 }, { opacity: 1, duration: 0.2 }, s.at + 0.7);
      }
      return t;
    };
    w.left = tile(props.left); w.right = tile(props.right);
    if (props.pick && props.pickAt != null) {
      const win = props.pick === "left" ? w.left : w.right, lose = props.pick === "left" ? w.right : w.left;
      ft(tl, lose, { opacity: 1 }, { opacity: 0.5, duration: 0.3 }, props.pickAt);
      ft(tl, win, { scale: 1 }, { scale: 1.03, duration: 0.3, ease: "back.out(2)" }, props.pickAt);
      const b = RSB.checkBadge(win, { size: 56 }, tl, props.pickAt + 0.1); b.style.left = ""; b.style.right = "-14px"; b.style.top = "-14px";
      w.check = b;
    }
    return w;
  };

  /**
   * Framed screenshot / screen recording without a device (proof shots): rounded card with hairline + shadow.
   * Pass `src` (image), `node` (static framework <video>) or `html`; nothing → labelled footage slot.
   * enter: rise y+80/scale .94 0.4 s expo.out; `tilt` = slight 3D tilt degrees (ref imperfection).
   * @param {{src?:string, node?:HTMLElement, html?:string, width?:number, height?:number, radius?:number,
   *          tilt?:number, label?:string, x?,y?,center?,flow?}} props
   * @returns {HTMLElement} frame; `.screen` for overlays.
   */
  RSB.screenshot = function (container, props = {}, tl, at) {
    const f = place(el("div", "rsb-shot", container), props);
    f.style.width = (props.width || 790) + "px"; f.style.height = (props.height || 1150) + "px";
    if (props.radius != null) f.style.borderRadius = props.radius + "px";
    const scr = el("div", "screen", f);
    if (props.node) scr.appendChild(props.node);
    else if (props.src) { const i = el("img", null, scr); i.src = props.src; i.alt = ""; }
    else if (props.html) scr.innerHTML = props.html;
    else RSB.footage(scr, { compact: true, label: props.label || "скриншот" });
    tl.fromTo(f, { opacity: 0, y: 80, scale: 0.94, rotationX: props.tilt ? props.tilt * 2 : 0, filter: "blur(8px)" },
      { opacity: 1, y: 0, scale: 1, rotationX: props.tilt || 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }, at);
    f.screen = scr;
    return f;
  };

  /* ================================================================== *
   * LAYOUTS — RSB.layout.<id>(container, props, tl, at) → block
   * references/layouts.md: live area y 230–1575 / x 90–990; the content block (union of everything in the
   * scene at its final state) is centred at y≈880 and fills ≥ 45 % (≥ 600 px) except `statement`.
   * Rhythm (same in every scene): kicker→headline 34 · headline→sub 26 · headline→visual 96 · visual→caption 76.
   *
   * Common props: kicker / headline / sub / second = RSB.line props ({words|text, at, highlight, emoji…}),
   *   step = capsule above the kicker ({text, at, kind}), cy = block centre (default 880),
   *   visual = component spec placed in a centred flow slot:
   *     • function (slot, tl) → HTMLElement  (build anything; absolute children are relative to the slot), or
   *     • {type:'card'|'player'|…, at, …props} → RSB[type](slot, props, tl, at)  (flow:true is added).
   * Returns the block (absolute, x 90–990) with `.slots` {step,kicker,headline,sub,visual,…}, `.metrics`
   * {top,bottom,height,centre,fill} and `.recentre()` (call if you add content afterwards).
   * ================================================================== */
  const LIVE = { top: 230, bottom: 1575, left: 90, right: 990, cy: 880, minFill: 600 };
  const RHYTHM = { sk: 46, kh: 34, hs: 26, hv: 96, vc: 76, cc: 14 };
  const layout = (RSB.layout = { LIVE, RHYTHM });

  function block(container, name, props) {
    const b = el("div", `rsb-block rsb-layout-${name}`, container);
    b.slots = {}; b.dataset.layout = name;
    b._props = props;
    return b;
  }
  function settle(b, props, opt = {}) {
    const lo = opt.minTop ?? props.minTop ?? 250, hi = opt.maxBottom ?? props.maxBottom ?? LIVE.bottom;
    const cy = props.cy ?? opt.cy ?? LIVE.cy;
    const h = b.offsetHeight;
    const top = Math.round(Math.max(lo, Math.min(cy - h / 2, hi - h)));
    b.style.top = top + "px";
    b.metrics = { top, bottom: top + h, height: h, centre: Math.round(top + h / 2), fill: +(h / (LIVE.bottom - LIVE.top)).toFixed(2) };
    b.dataset.top = top; b.dataset.height = h;
    if (!opt.noFill && h < LIVE.minFill && typeof console !== "undefined") console.warn(`[RSB.layout.${b.dataset.layout}] block is ${h}px tall (< ${LIVE.minFill}px = 45 % of the live area) — use bigger components or layout 'statement'`);
    b.recentre = () => settle(b, props, opt);
    return b;
  }
  function textLine(b, cls, spec, tl, at, mt) {
    if (!spec) return null;
    const s = typeof spec === "string" ? { text: spec } : spec;
    return RSB.line(b, Object.assign({ cls, mt }, s), tl, s.at ?? at);
  }
  function visualSlot(b, spec, tl, at, mt) {
    if (!spec) return null;
    const slot = RSB.slot(b, mt); slot.style.width = "100%";
    const out = typeof spec === "function" ? spec(slot, tl) : RSB[spec.type](slot, Object.assign({ flow: true }, spec), tl, spec.at ?? at);
    slot.component = out;
    return slot;
  }
  /** kicker/headline/sub/second group. Returns the gap the next element should use. */
  function textGroup(b, props, tl, at, first) {
    let mt = first ? 0 : RHYTHM.hv;
    const S = b.slots;
    if (props.step) {
      const h = el("div", null, b); h.style.marginTop = mt + "px";
      S.step = RSB.capsule(h, Object.assign({ kind: "step" }, props.step), tl, props.step.at ?? at);
      mt = RHYTHM.sk;
    }
    if (props.kicker) { S.kicker = textLine(b, "kicker", props.kicker, tl, at, mt); mt = RHYTHM.kh; }
    if (props.headline) { S.headline = textLine(b, "headline", props.headline, tl, at, mt); mt = RHYTHM.cc + 6; }
    if (props.sub) { S.sub = textLine(b, "sub", props.sub, tl, at, RHYTHM.hs); }
    if (props.second) { S.second = textLine(b, "second", props.second, tl, at, RHYTHM.hs); }
  }
  function captionGroup(b, props, tl, at) {
    const c = props.caption; if (!c) return;
    const spec = typeof c === "string" || c.words || c.text ? { kicker: c } : c;
    let mt = RHYTHM.vc;
    if (spec.kicker) { b.slots.captionKicker = textLine(b, "kicker", spec.kicker, tl, at, mt); mt = RHYTHM.cc; }
    if (spec.second) b.slots.caption = textLine(b, "second", spec.second, tl, at, mt);
    if (spec.headline) b.slots.caption = textLine(b, "headline", spec.headline, tl, at, mt);
  }

  /**
   * `stack` — [step] → kicker → headline → [sub] → visual → [caption], whole block centred (style B default).
   * @param {{step?, kicker?, headline?, sub?, second?, visual?, visuals?:Array, caption?:string|object|{kicker?,second?},
   *          cy?:number}} props   visuals = several components with 40 px gaps
   */
  layout.stack = function (container, props, tl, at) {
    const b = block(container, "stack", props);
    textGroup(b, props, tl, at, true);
    const vs = props.visuals || (props.visual ? [props.visual] : []);
    b.slots.visuals = vs.map((v, i) => visualSlot(b, v, tl, at, i ? (props.visualGap ?? 40) : RHYTHM.hv));
    b.slots.visual = b.slots.visuals[0] || null;
    captionGroup(b, props, tl, at);
    return settle(b, props);
  };

  /**
   * `visual-top` — big visual first (≤ 55 % height), then kicker + headline underneath (headline lands
   * y ≈ 1250–1450). Asymmetric: mass sits high.
   * @param {{visual, kicker?, headline?, sub?, cy?:number}} props
   */
  layout["visual-top"] = layout.visualTop = function (container, props, tl, at) {
    const b = block(container, "visual-top", props);
    b.slots.visual = visualSlot(b, props.visual, tl, at, 0);
    const g = el("div", null, b); g.style.height = RHYTHM.hv + "px"; g.style.flex = "none";
    textGroup(b, Object.assign({}, props, { step: null }), tl, at, true);
    return settle(b, props, { cy: props.cy ?? 900 });
  };

  /**
   * `number` — giant counter centre (font 400 px ≈ 290 px digits) with label above and below.
   * @param {{step?, kicker?, number:{from?:number,to:number,dur?:number,size?:number,suffix?:{text,size?},color?,at?},
   *          headline?, sub?, below?:visual spec (e.g. capsule row), cy?}} props
   */
  layout.number = function (container, props, tl, at) {
    const b = block(container, "number", props);
    textGroup(b, { step: props.step, kicker: props.kicker }, tl, at, true);
    const n = props.number;
    const slot = RSB.slot(b, props.kicker || props.step ? 10 : 0);
    const c = RSB.counter(slot, Object.assign({ size: 400, dur: 0.75, blur: 8 }, n, { suffix: n.suffix ? Object.assign({ size: 96 }, n.suffix) : undefined }), tl, n.at ?? at);
    c.style.lineHeight = "1"; c.num.style.lineHeight = "0.92";
    b.slots.number = c;
    if (props.headline) b.slots.headline = textLine(b, "headline", props.headline, tl, at, 6);
    if (props.sub) b.slots.sub = textLine(b, "sub", props.sub, tl, at, RHYTHM.cc);
    if (props.below) b.slots.below = visualSlot(b, props.below, tl, at, 64);
    return settle(b, props);
  };

  /**
   * `media` — iPhone mockup (≥ 60 % frame height: width 565 → 1160 px) or framed screenshot with a short line of
   * text above (default), below, or as an overlay pill. Proof / tutorials.
   * @param {{device?:'iphone'|'screenshot', src?, node?, html?, width?:number, height?:number, enter?:string,
   *          text?:RSB.line props, textCls?:'kicker'|'callout'|'sub', textPos?:'top'|'bottom', float?:number, cy?}} props
   * @returns block; `.slots.device` (iphone holder: `.screen`) for cursors/toggles.
   */
  layout.media = function (container, props, tl, at) {
    const b = block(container, "media", props);
    const top = props.textPos !== "bottom";
    const txt = () => props.text ? textLine(b, props.textCls || "kicker", props.text, tl, at, top ? 0 : 48) : null;
    if (top) b.slots.text = txt();
    const slot = RSB.slot(b, top && props.text ? 44 : 0); slot.style.width = "100%";
    const dev = props.device === "screenshot"
      ? RSB.screenshot(slot, Object.assign({ flow: true, width: 790, height: 1150 }, props), tl, props.deviceAt ?? at)
      : RSB.iphone(slot, Object.assign({ flow: true, width: 565 }, props, { floor: props.floor }), tl, props.deviceAt ?? at);
    b.slots.device = dev; b.slots.visual = slot;
    if (!top) b.slots.text = txt();
    return settle(b, props, { cy: props.cy ?? 905, minTop: 248 });
  };

  /**
   * `list` — kicker + headline + 3–4 rows building downward (RSB.listRows), centred column.
   * @param {{step?, kicker?, headline?, rows:Array, variant?:'cards'|'timeline', skeleton?:number, rowH?, gap?, caption?, cy?}} props
   */
  layout.list = function (container, props, tl, at) {
    const b = block(container, "list", props);
    textGroup(b, props, tl, at, true);
    b.slots.visual = visualSlot(b, (slot, tl2) => RSB.listRows(slot, { flow: true, rows: props.rows, variant: props.variant || props.style, skeleton: props.skeleton, rowH: props.rowH, gap: props.gap, width: props.width }, tl2, at), tl, at, props.headline || props.kicker ? RHYTHM.hv : 0);
    b.slots.rows = b.slots.visual.component.rows;
    captionGroup(b, props, tl, at);
    return settle(b, props);
  };

  /**
   * `compare` — two columns or two stacked states (before → after, A vs B) under a kicker/headline.
   * @param {{kicker?, headline?, mode?:'columns'|'stacked', left, right, pick?, pickAt?, caption?, cy?}} props see RSB.compare
   */
  layout.compare = function (container, props, tl, at) {
    const b = block(container, "compare", props);
    textGroup(b, props, tl, at, true);
    b.slots.visual = visualSlot(b, (slot, tl2) => RSB.compare(slot, Object.assign({ flow: true }, props), tl2, at), tl, at, RHYTHM.hv);
    b.slots.compare = b.slots.visual.component;
    captionGroup(b, props, tl, at);
    return settle(b, props);
  };

  /**
   * `statement` — breath scene: optional kicker + 2 big one-line headlines (≤ 120 px, fit ≤ 840 px), no visual.
   * Max 1 per 6 scenes.
   * @param {{kicker?, lines:Array<RSB.line props>, size?:number, cy?}} props
   */
  layout.statement = function (container, props, tl, at) {
    const b = block(container, "statement", props);
    if (props.kicker) b.slots.kicker = textLine(b, "kicker", props.kicker, tl, at, 0);
    b.slots.lines = (props.lines || []).map((ln, i) => textLine(b, "headline", Object.assign({ maxPx: props.size || 120, maxW: 840 }, typeof ln === "string" ? { text: ln } : ln), tl, at, i ? 4 : (props.kicker ? RHYTHM.kh : 0)));
    return settle(b, props, { noFill: true, cy: props.cy ?? 900 });
  };

  /**
   * `head` — full-frame talking head (REAL footage only: `footage.node`/`footage.src`; otherwise a labelled slot)
   * + optional title sticker and chest-band captions. Hide the chrome over footage.
   * @param {{footage?:object (RSB.footage props), sticker?:{text,emoji?,at?,y?}, caption?:{phrases,y?,size?}}} props
   */
  layout.head = function (container, props, tl, at) {
    const b = block(container, "head", props);
    b.style.top = "0"; b.style.left = "0"; b.style.width = "1080px"; b.style.height = "1920px";
    b.slots.footage = RSB.footage(b, Object.assign({ slot: { x: 140, y: 300, w: 800, h: 700 } }, props.footage || {}));
    if (props.sticker) b.slots.sticker = RSB.sticker(b, Object.assign({ y: 1060 }, props.sticker), tl, props.sticker.at ?? at);
    if (props.caption) b.slots.caption = RSB.caption(b, Object.assign({ y: 1350 }, props.caption), tl, at);
    b.metrics = { top: 0, bottom: 1920, height: 1920, centre: 960, fill: 1 };
    b.recentre = () => b;
    return b;
  };

  /**
   * `head-side` — talking head with ONE component group in the chest band (y 880–1460), centred in the band;
   * optional caption line under it. Face area (y ≈ 250–860) stays clear.
   * @param {{footage?:object, visual?, visuals?:Array, kicker?, headline?, caption?:{phrases,y?}, band?:[number,number]}} props
   */
  layout["head-side"] = layout.headSide = function (container, props, tl, at) {
    const root = el("div", "rsb-layout-head-side-root", container);
    Object.assign(root.style, { position: "absolute", inset: "0" });
    const foot = RSB.footage(root, Object.assign({ slot: { x: 190, y: 270, w: 700, h: 560 } }, props.footage || {}));
    const b = block(root, "head-side", props);
    const band = props.band || [880, 1460];
    textGroup(b, { kicker: props.kicker, headline: props.headline }, tl, at, true);
    const vs = props.visuals || (props.visual ? [props.visual] : []);
    b.slots.visuals = vs.map((v, i) => visualSlot(b, v, tl, at, i ? (props.visualGap ?? 40) : (props.kicker || props.headline ? 60 : 0)));
    b.slots.visual = b.slots.visuals[0] || null;
    settle(b, props, { cy: (band[0] + band[1]) / 2, minTop: band[0], maxBottom: band[1], noFill: true });
    if (props.caption) b.slots.caption = RSB.caption(root, Object.assign({ y: band[1] + 30, size: 54 }, props.caption), tl, at);
    b.slots.footage = foot; b.root = root;
    return b;
  };

  /* ================================================================== *
   * TRANSITIONS — RSB.tx.<name>(tl, outEl, inEl, at, opts)
   * Pages that a transition reveals should be created with {visible:false}.
   * ================================================================== */
  const tx = (RSB.tx = {});

  /**
   * Scene dissolve (DeRXnpgtYe6/DeZREMAtvBf): outgoing page scales 1→0.97, blurs 0→6px, fades over the
   * near-black stage; incoming fades in from at+0.06. 0.55 s power2.inOut (range 0.45–0.7).
   * Put RSB.chrome steps at the same `at`.
   * @param {{dur?:number, scale?:number, blur?:number, lift?:number}} o  lift = upward drift px (DelZA2dtAE6 variant)
   */
  tx.dissolve = function (tl, outEl, inEl, at, o = {}) {
    const d = o.dur ?? 0.55;
    ft(tl, outEl, { opacity: 1, scale: 1, y: 0, filter: "blur(0px)" }, { opacity: 0, scale: o.scale ?? 0.97, y: -(o.lift ?? 0), filter: `blur(${o.blur ?? 6}px)`, duration: d, ease: "power2.inOut" }, at);
    ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: d * 0.9, ease: "power2.out" }, at + 0.06);
  };

  /**
   * Portal / light-orb flash (De1roE4t7Lf): a white orb with bloom travels on an arc from a top corner toward
   * centre (0–0.35 s), grows exponentially (0.35–0.55), full white 0.55–0.65 (layers swap under the white),
   * then white fades into the new scene over 0.55 s. Pair with a sub-bass boom SFX at `at - 0.15`.
   * @param {HTMLElement} layer  overlay host above both pages (e.g. stage root)
   * @param {{from?:[number,number], to?:[number,number]}} o
   */
  tx.portal = function (tl, outEl, inEl, at, o = {}, layer) {
    const host = layer || outEl.parentNode;
    const orb = el("div", "rsb-orb", host), wo = el("div", "rsb-whiteout", host);
    const [fx, fy] = o.from || [880, 320], [tx2, ty] = o.to || [540, 960];
    const mx = (fx + tx2) / 2 + 60, my = (fy + ty) / 2 - 80; // arc control
    tl.fromTo(orb, { x: fx, y: fy, scale: 1, opacity: 0 }, { opacity: 1, duration: 0.08 }, at);
    ft(tl, orb, { x: fx, y: fy }, { keyframes: [{ x: mx, y: my, duration: 0.2, ease: "power1.in" }, { x: tx2, y: ty, duration: 0.2, ease: "power1.out" }] }, at);
    ft(tl, orb, { scale: 1 }, { scale: 32, duration: 0.25, ease: "expo.in" }, at + 0.33);
    tl.fromTo(wo, { opacity: 0 }, { opacity: 1, duration: 0.12, ease: "power2.in" }, at + 0.46);
    ft(tl, orb, { opacity: 1 }, { opacity: 0, duration: 0.01 }, at + 0.6);
    ft(tl, outEl, { opacity: 1 }, { opacity: 0, duration: 0.01 }, at + 0.6);
    ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: 0.01 }, at + 0.6);
    ft(tl, wo, { opacity: 1 }, { opacity: 0, duration: 0.55, ease: "power2.out" }, at + 0.65);
    return { orb, whiteout: wo };
  };

  let gid = 0;
  function glitchFilter(kind) {
    const id = `rsb-gl-${++gid}`;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.style.position = "absolute";
    const freq = kind === "block" ? "0.004 0.012" : "0.00001 0.022";
    svg.innerHTML = `<filter id="${id}" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="${freq}" numOctaves="1" seed="1" result="n"/>
      <feComponentTransfer in="n" result="m"><feFuncR type="discrete" tableValues="0.5 0.5 0.15 0.85 0.5 0.3 0.5 0.7 0.5 0.05 0.5"/><feFuncG type="linear" slope="0" intercept="0.5"/></feComponentTransfer>
      <feDisplacementMap in="SourceGraphic" in2="m" scale="0" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feColorMatrix in="d" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r"/>
      <feOffset in="r" dx="0" dy="0" result="ro"/>
      <feColorMatrix in="d" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0" result="gb"/>
      <feOffset in="gb" dx="0" dy="0" result="gbo"/>
      <feBlend in="ro" in2="gbo" mode="screen"/></filter>`;
    document.body.appendChild(svg);
    const q = (s) => svg.querySelectorAll(s);
    return { id, turb: q("feTurbulence")[0], disp: q("feDisplacementMap")[0], offR: q("feOffset")[0], offGB: q("feOffset")[1] };
  }

  /** Per-frame deterministic glitch frames on one element (zero-duration sets at frame boundaries). */
  function glitchFrames(tl, target, f, t0, frames, fps, rnd, amp, mode) {
    tl.set(target, { filter: `url(#${f.id})` }, t0);
    for (let i = 0; i < frames; i++) {
      const t = t0 + i / fps, env = Math.sin(Math.PI * (i + 0.5) / frames); // 0→1→0
      const sx = Math.round(amp.disp * env * (0.5 + rnd()));
      const dx = Math.round(amp.rgb * env * (rnd() > 0.5 ? 1 : -1) * (0.6 + rnd() * 0.4));
      const dy = mode === "ghost" ? Math.round((12 + rnd() * 28) * env) : 0;
      tl.set(f.turb, { attr: { seed: Math.floor(rnd() * 997) + 1 } }, t);
      tl.set(f.disp, { attr: { scale: sx } }, t);
      tl.set(f.offR, { attr: { dx: dx, dy: dy } }, t);
      tl.set(f.offGB, { attr: { dx: -dx, dy: -Math.round(dy * 0.5) } }, t);
    }
    tl.set(target, { filter: "none" }, t0 + frames / fps);
  }

  /**
   * Datamosh / pixel glitch (DelZA2dtAE6, Dd3Uz4Mgbn-): 6–9 frames. Horizontal slice displacement (bands 20–60px
   * shifted ±20–60px) + RGB split on the outgoing layer, hard swap at the middle frame, block smear on the
   * incoming layer, clean at the end. Deterministic via RS.rand(seed).
   * @param {{frames?:number, fps?:number, seed?:number, disp?:number, rgb?:number}} o
   */
  tx.datamosh = function (tl, outEl, inEl, at, o = {}) {
    const frames = o.frames ?? 8, fps = o.fps ?? 30, rnd = RS.rand(o.seed ?? 7);
    const half = Math.ceil(frames / 2), sw = at + half / fps;
    const fo = glitchFilter("slice"), fi = glitchFilter("block");
    glitchFrames(tl, outEl, fo, at, half, fps, rnd, { disp: o.disp ?? 110, rgb: o.rgb ?? 14 }, "slice");
    ft(tl, outEl, { opacity: 1 }, { opacity: 0, duration: 0.001 }, sw);
    ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: 0.001 }, sw);
    glitchFrames(tl, inEl, fi, sw, frames - half, fps, rnd, { disp: (o.disp ?? 110) * 1.4, rgb: o.rgb ?? 14 }, "block");
  };

  /**
   * RGB ghost glitch into the loop (DeRXnpgtYe6 end, 6 frames): frame duplicated at +12…+40px vertical offsets
   * with chromatic fringing, sharp, no blur; swap at the middle frame.
   * @param {{frames?:number, fps?:number, seed?:number}} o
   */
  tx.rgbGhost = function (tl, outEl, inEl, at, o = {}) {
    const frames = o.frames ?? 6, fps = o.fps ?? 30, rnd = RS.rand(o.seed ?? 11);
    const half = Math.ceil(frames / 2), sw = at + half / fps;
    const fo = glitchFilter("slice"), fi = glitchFilter("slice");
    glitchFrames(tl, outEl, fo, at, half, fps, rnd, { disp: 14, rgb: 22 }, "ghost");
    ft(tl, outEl, { opacity: 1 }, { opacity: 0, duration: 0.001 }, sw);
    ft(tl, inEl, { opacity: 0 }, { opacity: 1, duration: 0.001 }, sw);
    glitchFrames(tl, inEl, fi, sw, frames - half, fps, rnd, { disp: 14, rgb: 22 }, "ghost");
  };

  window.RSB = RSB;
})();
