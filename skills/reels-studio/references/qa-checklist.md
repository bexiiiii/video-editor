# QA checklist

## Automatic (`scripts/qa.py`, must all pass)
- Duration = plan ±0.1 s · 1080×1920 · 30 fps · H.264 + AAC.
- Integrated loudness −14 ±1 LUFS, true peak ≤ −1 dBTP.
- No unintended black/frozen segments.
- Headline/caption reveal times within ±0.12 s of planned word times.
- Talking-head modes: caption track covers ≥ 98 % of spoken words in caption ranges; every caption word on screen −0.10…+0.05 s around its onset (`caption_coverage`, `caption_sync`).
- Centred layouts: content centre x within ±24 px of 540 (`centering`, warn); caption line centred (`caption_centering`).
- Audio checks from `scripts/qa_audio.py` (merged when present).

- Plan variety (`qa.py --plan-only` too): every scene has a layout, no layout twice in a row, one layout ≤ 30 %, component not reused within 3 scenes.

## Visual (QA agent eyeballs `qa/sheet.jpg` + per-scene snapshots)
Shared
- [ ] Content block centred in the live area; lower 40 % of the frame never empty while the top is crowded; no empty containers; nothing overlaps text.
- [ ] No drawn people/faces; no emoji/CSS blobs as hero visuals; scenes don't all share one structure.
- [ ] No pure #000/#FFF backgrounds; grid/dots barely visible, not dominant.
- [ ] Words never re-centre/bounce while revealing; nothing clipped at frame edges; safe zone: keep text out of top 8% and bottom 15% (Reels UI).
- [ ] Text has no exit animation except with its scene.
- [ ] Transitions land in speech pauses; every boundary (head ↔ motion too) is a visible transition, never a hard switch (step through ±0.3 s at 30 fps); the head footage keeps moving through the overlap.
- [ ] No element pops in: every entrance is eased ≥ 0.25 s (`lint_scenes.py` warnings resolved).
- [ ] Spelling correct in target language (uz Latin script: oʻ/gʻ apostrophes; kk Cyrillic: ә ғ қ ң ө ұ ү һ і).
Style A
- [ ] Headlines lowercase keywords (not subtitles), 2–4 words, ≤ 2 lines.
- [ ] Blur on every entrance and transition; motion blur on whips.
- [ ] One glossy 3D hero object per scene; no flat icons, no raw screenshots without frame treatment.
- [ ] No music, no SFX.
Style B
- [ ] Chrome visible (breadcrumb + page dots), active dot matches chapter.
- [ ] Headline one line, SF-like bold 108 px (shrunk if long), kicker thin grey.
- [ ] Only Apple system colours; soft shadows (no black drop shadows on dark).
- [ ] Previous content dims to ~50 % when focus moves.
- [ ] Music not under the hook; clicks only on interactions.
Talking head
- [ ] No leftover silences > 0.6 s, no filler words, no jump in audio level at cuts.
- [ ] Punch-ins alternate; overlays in chest band only; captions one line synced to words (assembler caption track: 1–4 words, lower third y 1250–1500, never over the face).
Style G (Editorial Selfie)
- [ ] Every stack = small lead words + ONE emphasis word (closer may have two); emphasis fitted (≤ 700 px, short words XL), lowercase, no punctuation; interlock tight (lead baseline → emphasis x-top ≈ 6 px), spread/tuck lines hug the emphasis edges.
- [ ] Treatments match meaning (value yellow · devotion pink glow · reflection serif · warning red · duty white); only glow-pink / glow-yellow glow; ≥ 3 treatments; red ≤ 30 % of stacks.
- [ ] Words reveal on their onset (never early), 3-frame fade + small rise; stacks swap hard; emphasis stacks readable ≥ 0.8 s.
- [ ] Stacks on the chest band (emphasis centre ≈ y 1335), never over the mouth/chin, never below y 1500.
- [ ] Inserts front-loaded (first ≈ 15 s); mint insert entered with a 1-frame white flash; head uncut, no punch-ins.
- [ ] **Sensitive content (religious topics):** no faces of prophets, companions or holy figures anywhere (light / silhouette only); no AI-generated calligraphy or Arabic of holy names (client file, client-verified); honorifics exactly as supplied; calm sound, no meme SFX; same care for any faith.
