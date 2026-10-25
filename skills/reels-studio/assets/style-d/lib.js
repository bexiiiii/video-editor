/* reels-studio · Style D "Talking Head × 3D Keyword" — global `RSD` (thin pack on top of RSA).
 *
 * Style D = Style A (assets/style-a, global RSA — the original pack, never edited from here) over the client's
 * talking-head footage: head segments carry A keyword headlines / grey captions / 3D heroes / A components in the
 * face-safe zones; 2–4 s full-screen A inserts sit between head segments; transitions = A blur-drift / whip.
 *
 * Contract (references/contracts.md):  RSD.<builder>(container, props, tl, at) → HTMLElement
 *   - absolute LOCAL seconds; seek-safe fromTo / sets only; deterministic; text never exits on its own.
 *   - Layers returned by RSD.layer / RSD.layout.* have RSA's layer shape {bg, content, inner, over, theme}
 *     so RSA.transition / transitionOut / transitionIn work unchanged between head and insert layers.
 * Requires (load order): GSAP → runtime.js (RS) → tokens-a.css + a.js (RSA) → tokens-d.css + d.js.
 * People: a human is ALWAYS real footage (`footage.node` = framework <video>, `footage.src` = photo) or, in an
 * assembled run, the head.mp4 clip underneath (`footage.transparent:true`). Otherwise a labelled neutral slot.
 * This library never draws figures or faces.
 */
(function () {
  "use strict";
  const RS = window.RS, RSA = window.RSA;
  if (!RS || !RSA) throw new Error("RSD needs runtime.js (RS) and style-a lib.js (RSA) loaded first");
  const RSD = { version: "2.0.0" };
  const el = RS.el;

  /** Face-safe zones over footage (face upper third, eyes ≈ 38 % = y 730). Headline centres stay out of y 230–1250 … */
  const ZONE = {
    lower: { head: 1340, caption: 1528, scrim: "lower", band: [1250, 1575] }, // A bottom tier (≈70 %)
    upper: { head: 390, caption: 548, scrim: "upper", band: [230, 600] },      // only when the face sits low
  };
  /** Where a component sits next to the face (centre px). Size 35–45 % of frame width when sharing with the head. */
  const SIDE = {
    below: { x: 540, y: 1045 },     // under the chin, above the lower-third headline
    right: { x: 820, y: 1000 },     // beside the torso (face centre x ≈ 540)
    left: { x: 260, y: 1000 },
  };
  RSD.ZONE = ZONE; RSD.SIDE = SIDE;
  const HERO_SHARED = 400;          // ≈ 37 % of 1080 (35–45 % when sharing the frame with the head)
  const HERO_INSERT = 500;          // A insert hero: 46–60 % of frame width (layouts.md §1; Dej ≈ 520)

  /** Fonts used by A (headlines are not measured, but snapshots/renders need them loaded before the first frame). */
  RSD.ready = function () {
    const f = document.fonts;
    if (!f || !f.load) return Promise.resolve();
    const specs = ["400 42px 'Google Sans Flex'", "500 74px 'Google Sans Flex'", "600 74px 'Google Sans Flex'", "600 74px 'Google Sans'", "500 106px 'Google Sans'"];
    return Promise.all(specs.map((s) => f.load(s).catch(() => null))).then(() => f.ready);
  };

  const CAMERA = `<svg viewBox="0 0 48 36"><rect x="2" y="7" width="32" height="24" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M34 15l11-6v18l-11-6z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>`;

  /* ================================================================== *
   * FOOTAGE BASE + CAMERA
   * ================================================================== */

  /**
   * Talking-head base layer. Real footage via `node` (framework-owned <video>, authored statically) or `src`
   * (photo); `transparent:true` in assembled runs (the head.mp4 clip lies underneath). Otherwise a labelled
   * neutral slot that marks the assumed face area and the eye line (38 %).
   * Punch-ins: hard scale sets on cuts, 1.0 ↔ 1.12 about the eyes (`punches:[{at, scale}]`). No lens effects.
   * @param {{node?:HTMLElement, src?:string, fit?:string, transparent?:boolean, label?:string, sub?:string,
   *          face?:'upper'|'lower', punches?:Array<{at:number, scale?:number}>}} props
   * @returns {HTMLElement} head (`.cam`)
   */
  RSD.headBase = function (container, props = {}, tl, at) {
    const head = el("div", "rsd-head" + (props.transparent ? " transparent" : ""), container);
    const cam = el("div", "rsd-cam", head);
    if (props.node || props.src) {
      const m = props.node || el("img");
      if (!props.node) { m.src = props.src; m.alt = ""; }
      m.classList.add("rsd-media"); m.style.objectFit = props.fit || "cover";
      cam.appendChild(m); head.media = m;
    } else if (!props.transparent) {
      const s = el("div", "rsd-slot", cam);
      const low = props.face === "lower";
      const b = el("div", "box", s);
      Object.assign(b.style, { left: "230px", width: "620px", top: (low ? 760 : 300) + "px", height: (low ? 760 : 820) + "px" });
      el("div", null, b, CAMERA);
      el("div", "lb", b).textContent = props.label || "ваше видео";
      el("div", "sb", b).textContent = props.sub || "talking head · 9:16";
      const eyes = el("div", "eyes", s); eyes.style.top = (low ? 1060 : 730) + "px";
      el("span", null, eyes).textContent = "линия глаз ≈ " + (low ? "55" : "38") + " %";
      head.slot = s;
    }
    (props.punches || []).forEach((p) => tl.set(cam, { scale: p.scale ?? 1.12 }, p.at));
    head.cam = cam;
    return head;
  };

  /** Readability scrim behind text over footage: soft dark gradient (lower or upper), no boxes. */
  RSD.scrim = function (container, props = {}) {
    const s = el("div", "rsd-scrim " + (props.where || "lower"), container);
    if (props.opacity != null) s.style.opacity = props.opacity;
    return s;
  };

  /**
   * Head layer with RSA's layer shape: `.bg` = footage + scrim, `.content/.inner` = A text & components,
   * `.over` = shared elements. Theme ink is A dark (white headline) — over footage A uses its halo exception.
   * @param {{footage?:object, zone?:'lower'|'upper', scrim?:boolean}} props
   */
  RSD.headLayer = function (container, props = {}, tl, at) {
    const zone = props.zone || "lower";
    const root = el("div", "rsa-layer rsa-theme-dark rsd-on-footage", container);
    root.bg = el("div", "rsa-bg", root);
    root.head = RSD.headBase(root.bg, Object.assign({ face: zone === "upper" ? "lower" : "upper" }, props.footage || {}), tl, at);
    if (props.scrim !== false) root.scrim = RSD.scrim(root.bg, { where: ZONE[zone].scrim });
    root.content = el("div", "rsa-content", root);
    root.inner = el("div", "rsa-inner", root.content);
    root.over = el("div", "rsa-over", root);
    root.theme = "head"; root.zone = zone;
    return root;
  };

  /** Full-screen A insert layer = RSA.layer (themes: dark, light, curtain, space, navy, green, maroon, teal, emerald, orange, lavender). */
  RSD.insertLayer = function (container, props = {}, tl, at) { return RSA.layer(container, props, tl, at); };

  /* ================================================================== *
   * TEXT OVER FOOTAGE (A headline + A caption in the face-safe zone)
   * ================================================================== */

  /**
   * A keyword headline (lowercase, 2–4 words, ≤ 2 lines, A size/weight, per-word blur-rise) placed in the zone.
   * @param {{text, words?, zone?:'lower'|'upper', y?:number, pills?:string[], size?:number}} props  (RSA.headline props)
   */
  RSD.headline = function (container, props, tl, at) {
    const z = ZONE[props.zone || "lower"];
    return RSA.headline(container, Object.assign({ halo: true }, props, { y: props.y ?? z.head }), tl, at);
  };
  /** A grey typewriter caption under the zone headline. */
  RSD.caption = function (container, props, tl, at) {
    const z = ZONE[props.zone || "lower"];
    return RSA.caption(container, Object.assign({}, props, { y: props.y ?? z.caption }), tl, at);
  };

  /**
   * One A component beside / below the face. `type` = any RSA builder (hero, numberRoll, glassPill, chip, pill,
   * selection, card, iconRow, stack …); x/y default to SIDE[side]; heroes default to 400 px (≈ 37 % width).
   * @param {{type:string, side?:'below'|'right'|'left', at?:number} & object} spec
   */
  RSD.component = function (container, spec, tl, at) {
    const pos = SIDE[spec.side || "below"];
    const p = Object.assign({ x: pos.x, y: pos.y }, spec);
    if (spec.type === "hero" && p.size == null) p.size = HERO_SHARED;
    const fn = RSA[spec.type];
    if (!fn) throw new Error(`RSD.component: unknown RSA builder "${spec.type}"`);
    return fn(container, p, tl, spec.at ?? at);
  };

  /** CTA = A bookmark ending ("сохрани" + title + caption); identity from props (brief.cta) only. */
  RSD.cta = function (container, props, tl, at) {
    if (!props || !props.name) throw new Error("RSD.cta: name comes from brief.cta — none given");
    return RSA.bookmarkCTA(container, { headline: props.headline || "сохрани", title: props.name, caption: props.handle || props.caption, layout: props.layout, src: props.src, size: props.size }, tl, at);
  };

  /* ================================================================== *
   * TRANSITIONS — A's own (head ↔ insert, insert ↔ insert)
   * ================================================================== */
  const tx = (RSD.tx = {});
  /** RSA.transition between any two RSD/RSA layers. type: 'blur-drift' (default) | 'whip' | 'zoom' | 'lum' | 'cut'. */
  tx.go = function (tl, from, to, tc, o = {}) { RSA.transition(tl, from, to, tc, o); };
  tx.blurDrift = function (tl, from, to, tc, dir) { RSA.transition(tl, from, to, tc, { type: "blur-drift", dir: dir || "down" }); };
  tx.whip = function (tl, from, to, tc, dir) { RSA.transition(tl, from, to, tc, { type: "whip", dir: dir || "up" }); };
  /** Clip window [start, end] a layer needs around its transitions (RSA.transitionWindow). */
  RSD.window = function (tcIn, tcOut, typeIn, typeOut) {
    return { start: tcIn == null ? 0 : RSA.transitionWindow(tcIn, typeIn).start, end: RSA.transitionWindow(tcOut, typeOut).end };
  };

  /* ================================================================== *
   * LAYOUTS — RSD.layout.<id>(container, spec, tl, at) → layer (RSA layer shape) with `.parts`
   * container = the scene clip. Each builds its own layer so transitions can run between them.
   * ================================================================== */
  const layout = (RSD.layout = {});

  /**
   * `head` — full-frame talking head + A keyword headline (+ optional grey caption) in the face-safe zone.
   * @param {{footage?, zone?:'lower'|'upper', headline:{text,words?,at?,pills?}, caption?:{text,at?}}} spec
   */
  layout.head = function (container, spec, tl, at) {
    const L = RSD.headLayer(container, { footage: spec.footage, zone: spec.zone }, tl, at);
    const zone = spec.zone || "lower", parts = {};
    if (spec.headline) parts.headline = RSD.headline(L.inner, Object.assign({ zone }, spec.headline), tl, spec.headline.at ?? at);
    if (spec.caption) parts.caption = RSD.caption(L.inner, Object.assign({ zone }, spec.caption), tl, spec.caption.at ?? at + 0.8);
    L.parts = parts; L.layout = "head";
    return L;
  };

  /**
   * `head-side` — talking head + ONE A component beside/below the face + zone headline.
   * @param {{footage?, zone?, headline, caption?, component:{type, side?, at?, …RSA props}}} spec
   */
  layout.headSide = layout["head-side"] = function (container, spec, tl, at) {
    const L = layout.head(container, Object.assign({}, spec, { caption: null }), tl, at);
    L.parts.component = RSD.component(L.inner, spec.component, tl, at);
    if (spec.caption) L.parts.caption = RSD.caption(L.inner, Object.assign({ zone: spec.zone || "lower" }, spec.caption), tl, spec.caption.at ?? at + 0.8);
    L.layout = "head-side";
    return L;
  };

  /**
   * `insert-hero` — full-screen A scene: A background, headline (top tier, y 545), 3D hero (y 1000), caption (y 1460).
   * @param {{theme?, drift?, headline, hero:{src|emoji|blob, entry?, size?, at?}, caption?}} spec
   */
  layout.insertHero = layout["insert-hero"] = function (container, spec, tl, at) {
    const L = RSD.insertLayer(container, { theme: spec.theme || "dark", drift: spec.drift ?? 3 }, tl, at);
    const parts = {};
    if (spec.headline) parts.headline = RSA.headline(L.inner, spec.headline, tl, spec.headline.at ?? at + 0.1);
    if (spec.hero) parts.hero = RSA.hero(L.inner, Object.assign({ size: HERO_INSERT, y: 1000 }, spec.hero), tl, spec.hero.at ?? at + 0.15);
    if (spec.caption) parts.caption = RSA.caption(L.inner, spec.caption, tl, spec.caption.at ?? at + 0.9);
    L.parts = parts; L.layout = "insert-hero";
    return L;
  };

  /**
   * `insert-number` — A hero number roll (106 px) with headline above, optional keyword pill / selection below, caption.
   * @param {{theme?, headline, number:{value, unit?, at?, y?}, pill?:{text,at?}, selection?:{text,at?,selectAt?}, caption?}} spec
   */
  layout.insertNumber = layout["insert-number"] = function (container, spec, tl, at) {
    const L = RSD.insertLayer(container, { theme: spec.theme || "light", drift: spec.drift ?? 3 }, tl, at);
    const parts = {};
    if (spec.headline) parts.headline = RSA.headline(L.inner, spec.headline, tl, spec.headline.at ?? at + 0.1);
    parts.number = RSA.numberRoll(L.inner, Object.assign({ y: 930 }, spec.number), tl, spec.number.at ?? at + 0.5);
    if (spec.pill) parts.pill = RSA.pill(L.inner, Object.assign({ y: 1090 }, spec.pill), tl, spec.pill.at ?? at + 0.9);
    if (spec.selection) parts.selection = RSA.selection(L.inner, Object.assign({ y: 1190 }, spec.selection), tl, spec.selection.at ?? at + 0.9);
    if (spec.bar) parts.bar = RSA.progressBar(L.inner, Object.assign({ y: 1240 }, spec.bar), tl, spec.bar.at ?? at + 0.7);
    if (spec.caption) parts.caption = RSA.caption(L.inner, spec.caption, tl, spec.caption.at ?? at + 1.3);
    L.parts = parts; L.layout = "insert-number";
    return L;
  };

  /**
   * `insert-media` — A glass card(s) / screenshot (no device frame) under a headline, optional chip, caption.
   * @param {{theme?, headline, cards?:Array<RSA.card props + at>, screenshot?:RSA.screenshot props + at, chip?:{text,x?,y?,at?}, connector?:{from,to,at}, caption?}} spec
   */
  layout.insertMedia = layout["insert-media"] = function (container, spec, tl, at) {
    const L = RSD.insertLayer(container, { theme: spec.theme || "navy", drift: spec.drift ?? 3 }, tl, at);
    const parts = {};
    if (spec.headline) parts.headline = RSA.headline(L.inner, spec.headline, tl, spec.headline.at ?? at + 0.05);
    if (spec.screenshot) parts.screenshot = RSA.screenshot(L.inner, spec.screenshot, tl, spec.screenshot.at ?? at + 0.2);
    parts.cards = (spec.cards || []).map((c, i) => RSA.card(L.inner, c, tl, c.at ?? at + 0.3 + i * 0.7));
    if (spec.connector) parts.connector = RSA.connector(L.inner, spec.connector, tl, spec.connector.at ?? at + 0.75);
    if (spec.chip) parts.chip = RSA.chip(L.inner, spec.chip, tl, spec.chip.at ?? at + 1.4);
    if (spec.caption) parts.caption = RSA.caption(L.inner, spec.caption, tl, spec.caption.at ?? at + 1.1);
    L.parts = parts; L.layout = "insert-media";
    return L;
  };

  /**
   * `statement` — breath insert: A headline centred (y 900) with an inline keyword pill (A pill wipe), optional caption.
   * Max 1 per 6 scenes.
   */
  layout.statement = function (container, spec, tl, at) {
    const L = RSD.insertLayer(container, { theme: spec.theme || "dark", drift: spec.drift ?? 3 }, tl, at);
    const parts = {};
    parts.headline = RSA.headline(L.inner, Object.assign({ y: 900 }, spec.headline), tl, spec.headline.at ?? at + 0.1);
    if (spec.caption) parts.caption = RSA.caption(L.inner, Object.assign({ y: 1100 }, spec.caption), tl, spec.caption.at ?? at + 1.0);
    L.parts = parts; L.layout = "statement";
    return L;
  };

  /**
   * `cta` — A bookmark ending on an insert (lavender by default): bookmark rises, "сохрани", name types, handle types.
   * @param {{theme?, name:string, handle?:string, headline?:string}} spec
   */
  layout.cta = function (container, spec, tl, at) {
    const L = RSD.insertLayer(container, { theme: spec.theme || "lavender", drift: spec.drift ?? 3 }, tl, at);
    L.parts = { bookmark: RSD.cta(L.inner, spec, tl, at + 0.05) };
    L.layout = "cta";
    return L;
  };

  window.RSD = RSD;
})();
