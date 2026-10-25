/* reels-studio shared runtime — deterministic, seek-safe helpers for HyperFrames + GSAP.
 * Every helper only ADDS tweens to a paused timeline at absolute local times; nothing reads the clock.
 * Text never exits on its own: helpers only build entrances.
 */
(function () {
  const RS = {};

  // Seeded PRNG (mulberry32) — use instead of Math.random.
  RS.rand = function (seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  RS.el = function (tag, cls, parent, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  };

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /**
   * Lay out words at their FINAL positions (spans), then reveal each at its time.
   * words: [{w, t}] (t = local reveal time) or a string + opts.at/opts.stagger.
   * opts: {blur=12, y=0, x=0, dur=0.3, ease='power3.out', from:{opacity:0}, highlight:[...], hlClass:'hl', dimAfter:null}
   */
  RS.words = function (el, words, tl, opts = {}) {
    if (typeof words === "string") {
      const at = opts.at || 0, st = opts.stagger ?? 0.08;
      words = words.split(/\s+/).filter(Boolean).map((w, i) => ({ w, t: at + i * st }));
    }
    const hl = new Set((opts.highlight || []).map((s) => s.toLowerCase()));
    el.innerHTML = words.map((o) => {
      const clean = o.w.replace(/[.,!?:;«»"]/g, "").toLowerCase();
      return `<span class="w${hl.has(clean) ? " " + (opts.hlClass || "hl") : ""}">${esc(o.w)}</span>`;
    }).join(" ");
    const spans = [...el.querySelectorAll(".w")];
    const blur = opts.blur ?? 12, dur = opts.dur ?? 0.3, ease = opts.ease || "power3.out";
    spans.forEach((s, i) => {
      tl.fromTo(s,
        { opacity: opts.fromOpacity ?? 0, y: opts.y ?? 0, x: opts.x ?? 0, filter: `blur(${blur}px)` },
        { opacity: 1, y: 0, x: 0, filter: "blur(0px)", duration: dur, ease }, words[i].t);
    });
    return spans;
  };

  /** Typewriter anchored at final layout: each char blurs in. cps = chars per second. */
  RS.type = function (el, text, tl, at, cps = 24, opts = {}) {
    el.innerHTML = [...text].map((c) => `<span class="c">${c === " " ? "&nbsp;" : esc(c)}</span>`).join("");
    const cs = el.querySelectorAll(".c");
    tl.fromTo(cs, { opacity: 0, filter: `blur(${opts.blur ?? 6}px)` },
      { opacity: 1, filter: "blur(0px)", duration: opts.dur ?? 0.12, stagger: 1 / cps, ease: "none" }, at);
    return cs;
  };

  /** Generic blur-in entrance for any element. */
  RS.blurIn = function (tl, el, at, o = {}) {
    tl.fromTo(el,
      { opacity: 0, filter: `blur(${o.blur ?? 14}px)`, x: o.x ?? 0, y: o.y ?? 24, scale: o.scale ?? 1, rotation: o.rotation ?? 0 },
      { opacity: 1, filter: "blur(0px)", x: 0, y: 0, scale: 1, rotation: 0, duration: o.dur ?? 0.4, ease: o.ease || "power3.out" }, at);
    return el;
  };

  /** Pop with overshoot (3D icons, badges). */
  RS.pop = function (tl, el, at, o = {}) {
    tl.fromTo(el, { opacity: 0, scale: o.from ?? 0.3, y: o.y ?? 40, filter: "blur(8px)" },
      { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: o.dur ?? 0.45, ease: o.ease || "back.out(1.7)" }, at);
    return el;
  };

  /**
   * Directional motion blur via an SVG filter attached to el. Animates stdDeviation alongside a move.
   * Returns the filter id. Use for whips / slide-ins.
   */
  let mbId = 0;
  RS.motionBlur = function (tl, el, at, dur, axis = "x", amount = 40) {
    const id = `rs-mb-${++mbId}`;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "0"); svg.setAttribute("height", "0"); svg.style.position = "absolute";
    svg.innerHTML = `<filter id="${id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="0 0"/></filter>`;
    document.body.appendChild(svg);
    el.style.filter = `url(#${id})`;
    const g = svg.querySelector("feGaussianBlur");
    const peak = axis === "x" ? `${amount} 0` : `0 ${amount}`;
    tl.fromTo(g, { attr: { stdDeviation: peak } }, { attr: { stdDeviation: "0 0" }, duration: dur, ease: "power2.out" }, at);
    return id;
  };

  /** Slot-machine number roll from `from` to `to`, formatted. */
  RS.numRoll = function (tl, el, at, from, to, dur = 0.9, fmt = (n) => Math.round(n).toLocaleString("ru-RU")) {
    const o = { v: from };
    el.textContent = fmt(from);
    tl.to(o, { v: to, duration: dur, ease: "power3.out", onUpdate: () => { el.textContent = fmt(o.v); } }, at);
    tl.fromTo(el, { filter: "blur(6px)" }, { filter: "blur(0px)", duration: dur, ease: "power3.out" }, at);
    return el;
  };

  /** Dim previous content when focus moves on (style B). */
  RS.dim = function (tl, el, at, to = 0.5, dur = 0.3) {
    tl.to(el, { opacity: to, duration: dur, ease: "power2.out" }, at);
  };

  window.RS = RS;
})();
