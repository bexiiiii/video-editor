# QA checklist

## Automatic (`scripts/qa.py`, must all pass)
- Duration = plan ±0.1 s · 1080×1920 · 30 fps · H.264 + AAC.
- Integrated loudness −14 ±1 LUFS, true peak ≤ −1 dBTP.
- No unintended black/frozen segments.
- Headline/caption reveal times within ±0.12 s of planned word times.

## Visual (QA agent eyeballs `qa/sheet.jpg` + per-scene snapshots)
Shared
- [ ] No pure #000/#FFF backgrounds; grid/dots barely visible, not dominant.
- [ ] Words never re-centre/bounce while revealing; nothing clipped at frame edges; safe zone: keep text out of top 8% and bottom 15% (Reels UI).
- [ ] Text has no exit animation except with its scene.
- [ ] Transitions land in speech pauses.
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
- [ ] Punch-ins alternate; overlays in chest band only; captions one line synced to words.
