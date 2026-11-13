#!/usr/bin/env python3
"""Loudness metering shared by cleanup.py, mix.py, music_search.py and qa_audio.py.

Pure numpy/scipy (no pyloudnorm): ITU-R BS.1770-4 K-weighting at 48 kHz, 400 ms blocks with
75 % overlap, absolute (−70 LUFS) and relative (−10 LU) gating. On top of the standard meter:

* **speech-gated loudness** — integrated loudness over the blocks where speech is active
  (mask from transcript word timings or an energy VAD). This is the number that tells whether
  a voice is "loud enough", independent of how many pauses the cut has.
* **masked loudness** — the same for an arbitrary mask (music under speech / music in pauses).
* **short-term curve** (3 s window) and **momentary curve** (400 ms) every 100 ms.
* band level (e.g. 2–4 kHz presence) over masked blocks.

CLI (debugging): audio_meter.py FILE [--transcript audio/transcript.json]
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
HOP = 0.1          # seconds between measurement points (curves + blocks)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


# --------------------------------------------------------------------------- io
def decode(path: Path, channels: int = 1, sr: int = SR) -> np.ndarray:
    """Any audio/video file -> float32 (channels, n)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-vn", "-ac", str(channels),
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, channels).T.copy()


def as2d(x: np.ndarray) -> np.ndarray:
    return x[None, :] if x.ndim == 1 else x


# --------------------------------------------------------------------------- meter core
def k_weight(x: np.ndarray) -> np.ndarray:
    x = as2d(np.asarray(x, np.float64))
    return signal.lfilter(*_K2, signal.lfilter(*_K1, x, axis=1), axis=1)


def _power_frames(x: np.ndarray, win: float) -> np.ndarray:
    """Mean-square (summed over channels) of K-weighted audio in windows of `win` s every HOP s.
    Frame i covers [i*HOP, i*HOP+win)."""
    z = k_weight(x) ** 2
    z = z.sum(axis=0)
    hop, w = int(HOP * SR), int(win * SR)
    if len(z) < w:
        return np.array([z.mean()]) if len(z) else np.zeros(0)
    c = np.concatenate([[0.0], np.cumsum(z)])
    starts = np.arange(0, len(z) - w + 1, hop)
    return (c[starts + w] - c[starts]) / w


def lufs_of_power(p: np.ndarray | float) -> np.ndarray | float:
    return -0.691 + 10 * np.log10(np.maximum(p, 1e-15))


def _gated(p: np.ndarray) -> float:
    if not len(p):
        return float("-inf")
    p = p[lufs_of_power(p) > -70]
    if not len(p):
        return float("-inf")
    rel = lufs_of_power(p.mean()) - 10
    p = p[lufs_of_power(p) > rel]
    return float(lufs_of_power(p.mean())) if len(p) else float("-inf")


def block_power(x: np.ndarray) -> np.ndarray:
    """400 ms gating blocks every 100 ms (75 % overlap) — BS.1770."""
    return _power_frames(x, 0.4)


def integrated(x: np.ndarray) -> float:
    return _gated(block_power(x))


def block_mask(mask: np.ndarray, n_blocks: int, win: float = 0.4, need: float = 0.6) -> np.ndarray:
    """Per-sample (or per-10ms) boolean mask -> per-block mask: block counts if >= `need` of it is True.
    `mask` is sampled every 10 ms."""
    m = np.asarray(mask, float)
    step, w = int(round(HOP / 0.01)), int(round(win / 0.01))
    out = np.zeros(n_blocks, bool)
    c = np.concatenate([[0.0], np.cumsum(m)])
    for i in range(n_blocks):
        s, e = i * step, min(len(m), i * step + w)
        if e > s:
            out[i] = (c[e] - c[s]) / (e - s) >= need
    return out


def masked(x: np.ndarray, mask10: np.ndarray, need: float = 0.6, gate: bool = True) -> float:
    """Loudness over blocks selected by a 10 ms mask. gate=False skips the relative gate (for beds)."""
    p = block_power(x)
    sel = block_mask(mask10, len(p), 0.4, need)
    p = p[sel]
    if not len(p):
        return float("-inf")
    if gate:
        return _gated(p)
    p = p[lufs_of_power(p) > -70]
    return float(lufs_of_power(p.mean())) if len(p) else float("-inf")


def short_term_curve(x: np.ndarray) -> np.ndarray:
    """3 s short-term loudness every 100 ms; value i is the window *centred* at i*HOP + 1.5 s."""
    return lufs_of_power(_power_frames(x, 3.0))


def momentary_curve(x: np.ndarray) -> np.ndarray:
    return lufs_of_power(_power_frames(x, 0.4))


def band_level(x: np.ndarray, lo: float, hi: float, mask10: np.ndarray | None = None) -> float:
    """Mean power (dB) of a band, over masked 10 ms frames when a mask is given."""
    y = as2d(x).mean(axis=0)
    sos = signal.butter(4, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos")
    e = _frames10(signal.sosfilt(sos, y) ** 2)
    if mask10 is not None:
        m = np.asarray(mask10, bool)[: len(e)]
        e = e[: len(m)][m]
    return float(10 * np.log10(e.mean() + 1e-15)) if len(e) else float("-inf")


def _frames10(e: np.ndarray) -> np.ndarray:
    hop = int(0.01 * SR)
    n = len(e) // hop
    return e[: n * hop].reshape(n, hop).mean(axis=1) if n else np.zeros(0)


def true_peak_db(x: np.ndarray) -> float:
    """4x-oversampled peak (BS.1770 true-peak approximation)."""
    x = as2d(x)
    peak = max(float(np.max(np.abs(signal.resample_poly(ch, 4, 1)))) for ch in x) if x.size else 0.0
    return 20 * math.log10(max(peak, 1e-9))


# --------------------------------------------------------------------------- speech masks (10 ms grid)
def vad_mask(x: np.ndarray, rel_db: float = -28.0, hang: float = 0.15) -> np.ndarray:
    """Energy VAD on the 300–4000 Hz band: frame is speech when within `rel_db` of the loud
    speech level (95th percentile) and above an absolute −55 dBFS floor; short holes filled."""
    y = as2d(x).mean(axis=0)
    sos = signal.butter(4, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos")
    e = _frames10(signal.sosfilt(sos, y) ** 2)
    if not len(e):
        return np.zeros(0, bool)
    db = 10 * np.log10(e + 1e-15)
    ref, floor = np.percentile(db, 95), np.percentile(db, 10)
    # footage often carries room tone or a music bed: sit the threshold between floor and speech
    thr = max(ref + rel_db, floor + 0.4 * (ref - floor), -55.0)
    m = db > thr
    return close_holes(m, int(hang / 0.01))


def close_holes(m: np.ndarray, n: int) -> np.ndarray:
    """Fill False runs shorter than n frames that sit between True frames; drop True blips < 3 frames."""
    m = m.copy()
    idx = np.flatnonzero(np.diff(np.r_[0, m.astype(int), 0]))
    runs = list(zip(idx[::2], idx[1::2]))
    for (s0, e0), (s1, _e1) in zip(runs, runs[1:]):
        if s1 - e0 < n:
            m[e0:s1] = True
    idx = np.flatnonzero(np.diff(np.r_[0, m.astype(int), 0]))
    for s, e in zip(idx[::2], idx[1::2]):
        if e - s < 3:
            m[s:e] = False
    return m


def words_mask(words: list[dict], total: float, pad: float = 0.05, merge: float = 0.25) -> np.ndarray:
    """Speech mask from transcript words; gaps shorter than `merge` s count as speech."""
    n = int(math.ceil(total / 0.01))
    m = np.zeros(n, bool)
    for w in words:
        s, e = max(0, int((float(w["s"]) - pad) / 0.01)), min(n, int(math.ceil((float(w["e"]) + pad) / 0.01)))
        m[s:e] = True
    return close_holes(m, int(merge / 0.01)) if merge > 0 else m


def speech_mask(work: Path | None, voice: np.ndarray, total: float | None = None) -> tuple[np.ndarray, str]:
    """Transcript-based mask when audio/transcript.json exists, else energy VAD on `voice`."""
    total = total or as2d(voice).shape[1] / SR
    tr_p = work / "audio" / "transcript.json" if work else None
    if tr_p and tr_p.is_file():
        try:
            words = json.loads(tr_p.read_text(encoding="utf-8")).get("words") or []
        except (OSError, json.JSONDecodeError):
            words = []
        n = int(math.ceil(total / 0.01))
        if words:
            m = fit_mask(words_mask(words, total), n)
            # ASR word timings tend to bridge short breaths; where the energy VAD sees a clear
            # gap (>= 0.2 s) inside the transcript span, trust the VAD.
            v = fit_mask(vad_mask(voice), n)
            if 0.3 < v.mean() < 0.995:
                gaps = ~close_holes(v, 20)
                return m & ~gaps, "transcript+vad"
            return m, "transcript"
    m = vad_mask(voice)
    n = int(math.ceil(total / 0.01))
    return np.pad(m, (0, max(0, n - len(m))))[:n], "vad"


def fit_mask(m: np.ndarray, n10: int) -> np.ndarray:
    return np.pad(np.asarray(m, bool), (0, max(0, n10 - len(m))))[:n10]


def fmt(v: float) -> str:
    return "−inf" if not math.isfinite(v) else f"{v:.1f}"


def main(argv: list[str] | None = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(description="BS.1770 meter with speech gating")
    ap.add_argument("file", type=Path)
    ap.add_argument("--transcript", type=Path)
    a = ap.parse_args(argv)
    x = decode(a.file, 2)
    total = x.shape[1] / SR
    if a.transcript:
        m = words_mask(json.loads(a.transcript.read_text())["words"], total)
    else:
        m = vad_mask(x)
    m = fit_mask(m, int(math.ceil(total / 0.01)))
    print(json.dumps({"integrated": round(integrated(x), 2), "speech_gated": round(masked(x, m), 2),
                      "non_speech": round(masked(x, ~m, gate=False), 2), "true_peak_db": round(true_peak_db(x), 2),
                      "speech_ratio": round(float(m.mean()), 3)}))


if __name__ == "__main__":
    sys.exit(main())
