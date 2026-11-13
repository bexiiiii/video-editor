#!/usr/bin/env python3
"""Audio QA for a rendered reel (or audio/mix.wav): is the voice king, is the music audible?

checks(work, video) -> list of dicts shaped like qa.py's add():
  {name, ok, severity, value, expected, detail}
  audio_voice_level        speech-gated voice in the master −14 ± 2 LUFS                    fail
  audio_music_gap          voice − music under speech 7–16 dB (music_bed stem; else power   fail
                           subtraction from the master in speech vs pause blocks)
  audio_music_in_pauses    music short-term (3 s) loudness in pauses ≥ −30 LUFS             fail
  audio_sfx_present        ≥ 1 SFX placed when brief.audio_profile is energetic             fail
  audio_clipping           4x-oversampled peak ≤ −0.9 dBTP and no full-scale samples       fail
  audio_mix_report         mix.py's own checks (audio/mix_report.json)                    warn
Speech mask: audio/transcript.json word timings (final timeline), else an energy VAD on voice.wav.
Profile "reference" with music disabled skips the music checks (info).

CLI: qa_audio.py --work work/<slug> [--video renders/final.mp4] [--json]   (exit 1 on any fail)
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "providers"))
import audio_meter as am  # noqa: E402

SR = am.SR
VOICE_TARGET, VOICE_TOL = -14.0, 2.0
GAP = (7.0, 16.0)
PAUSE_MIN_LUFS = -30.0


def _r(v):
    return round(float(v), 1) if v is not None and math.isfinite(float(v)) else None


def checks(work: Path, video: Path | None = None) -> list[dict]:
    work = Path(work)
    out: list[dict] = []

    def add(name, ok, severity, value=None, expected=None, detail=None):
        out.append({"name": name, "ok": bool(ok), "severity": "info" if ok else severity,
                    "value": value, "expected": expected, "detail": detail})

    src = Path(video) if video else work / "audio" / "mix.wav"
    if not src.is_file():
        add("audio_present", False, "fail", None, "audio", f"{src} not found")
        return out
    try:
        x = am.decode(src, 2)
    except Exception as e:  # noqa: BLE001  (no audio stream / undecodable)
        add("audio_present", False, "fail", None, "audio stream", f"cannot decode audio: {e}")
        return out
    total = x.shape[1] / SR
    n10 = int(math.ceil(total / 0.01))
    brief_p, plan_p = work / "brief.json", work / "plan" / "scenes.json"
    brief = json.loads(brief_p.read_text(encoding="utf-8")) if brief_p.is_file() else {}
    plan = json.loads(plan_p.read_text(encoding="utf-8")) if plan_p.is_file() else {}
    profile = brief.get("audio_profile", "energetic")
    voice_p = work / "audio" / "voice.wav"
    voice = am.decode(voice_p, 1) if voice_p.is_file() else x
    speech, src_mask = am.speech_mask(work, voice, total)
    speech = am.fit_mask(speech, n10)
    pauses = ~speech
    pauses[: 50] = False                       # first 0.5 s and last 1.5 s (fades) are not "pauses"
    pauses[max(0, n10 - 150):] = False

    # ---- music stem (written by mix.py at final level)
    bed_p = work / "audio" / "music_bed.wav"
    bed = am.decode(bed_p, 2) if bed_p.is_file() else None
    if bed is not None and bed.shape[1] != x.shape[1]:
        bed = np.pad(bed, ((0, 0), (0, max(0, x.shape[1] - bed.shape[1]))))[:, : x.shape[1]]
    music_cfg = (plan.get("audio") or {}).get("music") or {}
    music_expected = bool(music_cfg.get("enabled", bed is not None or profile == "energetic"))

    mix_speech = am.masked(x, speech)
    if bed is not None:
        m_speech = am.masked(bed, speech, gate=False)
        p_mix = 10 ** (mix_speech / 10) - (10 ** (m_speech / 10) if math.isfinite(m_speech) else 0)
        voice_final = 10 * math.log10(p_mix) if p_mix > 0 else mix_speech
        how = "master minus music_bed stem"
    else:
        m_speech, voice_final, how = None, mix_speech, "master, speech blocks (music not separated)"
    add("audio_voice_level", abs(voice_final - VOICE_TARGET) <= VOICE_TOL, "fail", _r(voice_final),
        f"{VOICE_TARGET:g} ± {VOICE_TOL:g} LUFS (speech-gated)", f"{how}; mask: {src_mask}")

    if not music_expected and bed is None:
        add("audio_music_gap", True, "info", None, "n/a", f"music off (profile {profile})")
        add("audio_music_in_pauses", True, "info", None, "n/a", f"music off (profile {profile})")
    else:
        if bed is not None and m_speech is not None and math.isfinite(m_speech):
            gap = voice_final - m_speech
            detail = f"music under speech {m_speech:.1f} LUFS (stem)"
        else:
            # no stem: estimate music under speech from the pause level (bed rises ~5 dB in pauses)
            mix_pause = am.masked(x, pauses, gate=False)
            gap = voice_final - (mix_pause - 5.0) if math.isfinite(mix_pause) else float("nan")
            detail = f"estimated from master pause level {am.fmt(mix_pause)} LUFS − 5 dB (no music_bed.wav)"
        add("audio_music_gap", math.isfinite(gap) and GAP[0] <= gap <= GAP[1], "fail", _r(gap),
            f"{GAP[0]:g}–{GAP[1]:g} dB below voice under speech", detail)
        sig = bed if bed is not None else x
        st = am.short_term_curve(sig)                       # value i ~ window centred at i*0.1 + 1.5 s
        centres = (np.arange(len(st)) * 0.1 + 1.5) / 0.01
        in_pause = np.array([pauses[min(n10 - 1, int(c))] for c in centres], bool) if len(st) else np.zeros(0, bool)
        if in_pause.any():
            vals = st[in_pause]
            p10, med = float(np.percentile(vals, 10)), float(np.median(vals))
            add("audio_music_in_pauses", p10 >= PAUSE_MIN_LUFS, "fail", _r(p10), f"≥ {PAUSE_MIN_LUFS:g} LUFS short-term",
                f"short-term in pauses: p10 {p10:.1f}, median {med:.1f}, min {float(vals.min()):.1f} LUFS "
                f"({'music stem' if bed is not None else 'master'})")
        else:
            add("audio_music_in_pauses", True, "info", None, f"≥ {PAUSE_MIN_LUFS:g} LUFS", "no pauses to measure")

    # ---- SFX
    cues = sum(len(s.get("sfx") or []) for s in plan.get("scenes", []))
    rep_p = work / "audio" / "mix_report.json"
    rep = json.loads(rep_p.read_text(encoding="utf-8")) if rep_p.is_file() else {}
    placed = rep.get("sfx_count", cues)
    if profile == "energetic":
        add("audio_sfx_present", placed > 0, "fail", placed, "≥ 1 SFX (energetic profile)",
            f"{cues} cues in scenes.json; run sfx_plan.py" if not placed else f"{cues} cues in scenes.json")
    else:
        add("audio_sfx_present", True, "info", placed, "any (reference profile)")

    # ---- clipping
    tp = am.true_peak_db(x)
    full = int((np.abs(x) >= 0.9999).sum())
    add("audio_clipping", tp <= -0.9 and full == 0, "fail", _r(tp), "≤ −1 dBTP, 0 full-scale samples",
        f"{full} full-scale samples")

    if rep:
        add("audio_mix_report", bool(rep.get("ok", True)), "warn", rep.get("gap_speech_db"),
            "mix.py checks pass", "; ".join(rep.get("problems") or []) or None)
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--video", type=Path, help="default: renders/final.mp4 if present, else audio/mix.wav")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    video = a.video
    if video is None and (a.work / "renders" / "final.mp4").is_file():
        video = a.work / "renders" / "final.mp4"
    res = checks(a.work, video)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for c in res:
            mark = "PASS" if c["ok"] else c["severity"].upper()
            print(f"[{mark:4s}] {c['name']:22s} {c['value']!s:>7}  expected {c['expected']}"
                  + (f"  — {c['detail']}" if c.get("detail") else ""))
    sys.exit(1 if any(not c["ok"] and c["severity"] == "fail" for c in res) else 0)


if __name__ == "__main__":
    main()
