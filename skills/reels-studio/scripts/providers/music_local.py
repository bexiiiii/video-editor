#!/usr/bin/env python3
"""Procedural music bed (free, offline, deterministic) — the last link of the music chain.

Three presets, all written so a voice sits comfortably on top:
  soft-subbass  style-B bed: soft pad + low sine sub + muted kick, quiet ticks (default 108 BPM)
  upbeat        four-on-the-floor, claps, off-beat bass, pluck stabs              (default 120 BPM)
  tense         drone + minor-second pulse ostinato, clock ticks, rising filter  (default 90 BPM)

Output is exactly round(dur * 48000) samples, stereo, 16-bit, with fade-in/out. Same
arguments + seed => bit-identical file. Arrangement: 2-bar intro (no drums), full body,
last bar without kick, then the fade.

Usage: music_local.py --dur 20 --mood soft-subbass [--bpm 108] [--seed 7] --out music.wav
"""
from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
MOODS = ("soft-subbass", "upbeat", "tense")
DEFAULT_BPM = {"soft-subbass": 108, "upbeat": 120, "tense": 90}


# --------------------------------------------------------------------------- DSP primitives
def t_axis(d: float) -> np.ndarray:
    return np.arange(int(d * SR)) / SR


def midi(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n: int, a: float, d: float, curve: float = 4.0) -> np.ndarray:
    """Linear attack `a` seconds, then exponential decay with time constant ~d/curve."""
    x = np.arange(n) / SR
    return np.clip(x / max(a, 1e-4), 0, 1) * np.exp(-curve * np.clip(x - a, 0, None) / max(d, 1e-4))


def adsr(n: int, a: float, r: float) -> np.ndarray:
    """Sustained note: attack ramp, flat, release ramp (sum never exceeds n)."""
    e = np.ones(n)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x: np.ndarray, f: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, min(f, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def highpass(x: np.ndarray, f: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bandpass(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def osc(freq: float, n: int, shape: str = "sine", phase: float = 0.0) -> np.ndarray:
    ph = 2 * np.pi * freq * np.arange(n) / SR + phase
    if shape == "sine":
        return np.sin(ph)
    if shape == "tri":
        return signal.sawtooth(ph, 0.5)
    if shape == "saw":
        return signal.sawtooth(ph)
    return signal.square(ph, 0.35)


def sweep_sine(f_of_t: np.ndarray) -> np.ndarray:
    """Sine with time-varying frequency (array of Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f_of_t) / SR)


class Bus:
    """Stereo accumulation buffer with sample-accurate placement and constant-power pan."""

    def __init__(self, n: int):
        self.buf = np.zeros((2, n))

    def add(self, x: np.ndarray, at: float, gain: float = 1.0, pan: float = 0.0) -> None:
        s = int(round(at * SR))
        if s >= self.buf.shape[1] or s + len(x) <= 0:
            return
        x = x[max(0, -s):]
        s = max(0, s)
        e = min(self.buf.shape[1], s + len(x))
        th = (pan + 1) * np.pi / 4
        self.buf[0, s:e] += x[: e - s] * gain * np.cos(th) * 1.414
        self.buf[1, s:e] += x[: e - s] * gain * np.sin(th) * 1.414


# --------------------------------------------------------------------------- instruments
def kick(soft: bool = False) -> np.ndarray:
    t = t_axis(0.4)
    f = 42 + (70 if soft else 120) * np.exp(-t * (28 if soft else 40))
    x = sweep_sine(f) * env(len(t), 0.002, 0.28 if soft else 0.22, 2.5)
    return lowpass(x, 900) if soft else x


def clap(rng) -> np.ndarray:
    n = int(0.2 * SR)
    e = sum(np.pad(env(n - s, 0.0005, 0.03, 4), (s, 0)) for s in (0, 330, 700))
    return bandpass(rng.standard_normal(n), 900, 5000) * e * 0.6


def hat(rng, open_: bool = False) -> np.ndarray:
    d = 0.18 if open_ else 0.045
    n = int(d * SR)
    return highpass(rng.standard_normal(n), 7000) * env(n, 0.0005, d * 0.5, 4)


def tick(freq: float = 3000) -> np.ndarray:
    n = int(0.03 * SR)
    return osc(freq, n) * env(n, 0.0005, 0.01, 4)


def pad(notes: list[int], d: float, cutoff: float, rng) -> tuple[np.ndarray, np.ndarray]:
    """Detuned triangle pad, separately rendered per channel for width."""
    n = int(d * SR)
    out = []
    for ch in (0, 1):
        x = np.zeros(n)
        for m in notes:
            for det in (-0.006, 0.0, 0.006):
                x += osc(midi(m) * (1 + det + (0.0015 if ch else -0.0015)), n, "tri", rng.uniform(0, 6.28))
        out.append(lowpass(x, cutoff) * adsr(n, 0.35, 0.4) / (len(notes) * 3))
    return out[0], out[1]


def sub(m: int, d: float) -> np.ndarray:
    """Low sine with a touch of saturation so phones (no sub-bass) still hear the pitch."""
    n = int(d * SR)
    return np.tanh(1.6 * osc(midi(m), n)) * env(n, 0.006, d, 2.0)


def pluck(m: int, d: float = 0.35, bright: float = 2600) -> np.ndarray:
    n = int(d * SR)
    x = osc(midi(m), n, "saw") + 0.5 * osc(midi(m) * 2.001, n, "tri")
    return lowpass(x, bright) * env(n, 0.002, d * 0.6, 3.5) * 0.5


def reese(m: int, d: float) -> np.ndarray:
    n = int(d * SR)
    x = osc(midi(m), n, "saw") + osc(midi(m) * 1.007, n, "saw")
    return np.tanh(2.2 * lowpass(x, 650)) * env(n, 0.003, d, 1.5)


# --------------------------------------------------------------------------- arrangements
class Song:
    """Shared timing helpers for the three presets."""

    def __init__(self, dur: float, bpm: float, seed: int):
        self.dur, self.beat = dur, 60.0 / bpm
        self.bar = self.beat * 4
        self.nbars = int(np.ceil(dur / self.bar)) + 1
        self.last_full_bar = max(int(dur // self.bar) - 1, 2)
        self.rng = np.random.default_rng(seed)
        self.bus = Bus(int(round(dur * SR)) + SR)

    def section(self, b: int) -> str:
        if b < 2:
            return "intro"
        return "outro" if b >= self.last_full_bar else "body"


def soft_subbass(s: Song) -> None:
    prog = [[62, 65, 69], [58, 62, 65], [53, 57, 60], [60, 64, 67]]   # Dm Bb F C
    roots = [38, 34, 41, 36]                                              # D2 Bb1 F2 C2
    K = kick(soft=True)
    for b in range(s.nbars):
        at, sec, ch = b * s.bar, s.section(b), prog[b % 4]
        l, r = pad(ch, s.bar + 0.4, 1100 if sec == "body" else 800, s.rng)
        pump = np.ones(len(l))
        if sec == "body":   # gentle sidechain-style pump on each kick
            for k in (0, 2):
                i = int(k * s.beat * SR)
                seg = np.clip(np.arange(int(0.25 * SR)) / (0.25 * SR), 0.55, 1)[: len(pump) - i]
                pump[i:i + len(seg)] = seg
        s.bus.add(l * pump, at, 0.55, -0.6)
        s.bus.add(r * pump, at, 0.55, 0.6)
        s.bus.add(sub(roots[b % 4], s.beat * 1.4), at, 0.42)
        s.bus.add(sub(roots[b % 4], s.beat * 1.2), at + s.beat * 2.5, 0.32)
        if sec == "body":
            for k in (0, 2):
                s.bus.add(K, at + k * s.beat, 0.55)
            for k in range(8):   # whisper-quiet off-beat ticks
                if k % 2:
                    s.bus.add(hat(s.rng), at + k * s.beat / 2, 0.035, 0.3 if k % 4 == 1 else -0.3)
            arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
            for k in range(4):
                s.bus.add(pluck(arp[k], 0.5, 1800), at + s.beat * k + s.beat / 2, 0.06, -0.4 + 0.27 * k)


def upbeat(s: Song) -> None:
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
    roots = [33, 29, 36, 31]
    K = kick()
    for b in range(s.nbars):
        at, sec, ch = b * s.bar, s.section(b), prog[b % 4]
        l, r = pad(ch, s.bar + 0.3, 2200 if sec == "body" else 1200, s.rng)
        s.bus.add(l, at, 0.35, -0.7)
        s.bus.add(r, at, 0.35, 0.7)
        for k in range(4):
            bt = at + k * s.beat
            if sec != "intro":
                if sec == "body" or k < 2:
                    s.bus.add(K, bt, 0.7)
                if k % 2 == 1 and sec == "body":
                    s.bus.add(clap(s.rng), bt, 0.4)
                s.bus.add(reese(roots[b % 4], s.beat * 0.45), bt + s.beat / 2, 0.22)
            s.bus.add(hat(s.rng, open_=True), bt + s.beat / 2, 0.07 if sec == "body" else 0.04, 0.25)
            for q in (1, 3):
                s.bus.add(hat(s.rng), bt + q * s.beat / 4, 0.035, -0.25)
        if sec == "body":
            for k in (1.5, 3.0):
                for m in ch:
                    s.bus.add(pluck(m + 12, 0.22, 3200), at + k * s.beat, 0.16)


def tense(s: Song) -> None:
    root = 40                                    # E2
    K = kick()
    for b in range(s.nbars):
        at, sec = b * s.bar, s.section(b)
        progress = min(b / max(s.nbars - 1, 1), 1.0)
        n = int((s.bar + 0.3) * SR)
        drone = (osc(midi(root - 12), n, "saw") + osc(midi(root - 5), n, "saw", 1.0) * 0.6)
        drone = lowpass(drone, 300 + 900 * progress) * adsr(n, 0.3, 0.3)
        s.bus.add(drone, at, 0.22, -0.2)
        s.bus.add(drone, at + 0.013, 0.22, 0.2)
        second = 1 if b % 2 else 0               # minor-second rub every other bar
        for k in range(8):
            m = root + 12 + (second if k in (3, 7) else 0)
            s.bus.add(pluck(m, 0.18, 900 + 2500 * progress), at + k * s.beat / 2, 0.12, -0.3 if k % 2 else 0.3)
        if sec != "intro":
            s.bus.add(K, at, 0.6)
            for k in range(16):
                s.bus.add(tick(2800 if k % 4 else 3600), at + k * s.beat / 4, 0.03 + 0.03 * (k % 4 == 0))
        if b % 4 == 0 and sec == "body":
            s.bus.add(kick(soft=True), at, 0.8)


PRESETS = {"soft-subbass": soft_subbass, "upbeat": upbeat, "tense": tense}


# --------------------------------------------------------------------------- render
def render(dur: float, mood: str = "soft-subbass", bpm: float | None = None, seed: int = 7) -> np.ndarray:
    if mood not in PRESETS:
        raise ValueError(f"mood must be one of {MOODS}")
    if dur <= 0:
        raise ValueError("duration must be > 0")
    song = Song(dur, bpm or DEFAULT_BPM[mood], seed)
    PRESETS[mood](song)
    n = int(round(dur * SR))
    mix = song.bus.buf[:, :n]
    # Short cross-feed "room" so the bed is not bone-dry, then soft clip and normalise.
    for delay, g in ((0.021, 0.10), (0.037, 0.08), (0.059, 0.06)):
        k = int(delay * SR)
        mix[0, k:] += mix[1, :-k] * g
        mix[1, k:] += mix[0, :-k] * g
    peak = np.max(np.abs(mix)) or 1.0
    mix = np.tanh(mix / peak * 1.2) / np.tanh(1.2)
    fade_in, fade_out = min(int(0.25 * SR), n // 4), min(int(1.5 * SR), n // 4)
    if fade_in:
        mix[:, :fade_in] *= np.linspace(0, 1, fade_in)
    if fade_out:
        mix[:, -fade_out:] *= np.linspace(1, 0, fade_out) ** 1.5
    return mix * 0.89                          # ~ -1 dBFS peak; mix.py sets the real level


def write_wav(path: Path, stereo: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(stereo.T, -1, 1) * 32767).astype("<i2").tobytes())


def mood_preset(text: str | None) -> str:
    """Map a free-text mood (from scenes.json) onto a preset."""
    t = (text or "").lower()
    if t in PRESETS:
        return t
    if any(k in t for k in ("tense", "dark", "suspense", "urgent", "danger", "problem")):
        return "tense"
    if any(k in t for k in ("upbeat", "energetic", "happy", "drive", "fast", "hype", "fun")):
        return "upbeat"
    return "soft-subbass"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dur", type=float, required=True, help="exact length in seconds")
    ap.add_argument("--mood", default="soft-subbass", help=f"{'|'.join(MOODS)} or free text")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    preset = mood_preset(args.mood)
    try:
        write_wav(args.out, render(args.dur, preset, args.bpm, args.seed))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"{args.out}: {args.dur}s {preset} @ {args.bpm or DEFAULT_BPM[preset]} BPM (seed {args.seed})")


if __name__ == "__main__":
    main()
