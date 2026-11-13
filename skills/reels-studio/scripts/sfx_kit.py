#!/usr/bin/env python3
"""Generate the bundled CC0 sound-effect kit into assets/sfx/*.wav (48 kHz, mono, 16-bit).

Every sound is synthesised from oscillators + filtered noise, so the kit is ours to license
as CC0. Deterministic: each sound has a fixed seed, so regenerating gives identical files.
Peaks are normalised per sound (quiet UI sounds lower than impacts); mix.py applies the
per-cue gain on top.

Usage: sfx_kit.py [--out assets/sfx] [--only click,pop] [--list]
"""
from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
OUT_DEFAULT = Path(__file__).resolve().parents[1] / "assets" / "sfx"


# --------------------------------------------------------------------------- primitives
def T(d: float) -> np.ndarray:
    return np.arange(int(d * SR)) / SR


def norm(x: np.ndarray, peak: float) -> np.ndarray:
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def env(n: int, a: float, d: float, c: float = 4.0) -> np.ndarray:
    x = np.arange(n) / SR
    return np.clip(x / max(a, 1e-4), 0, 1) * np.exp(-c * np.clip(x - a, 0, None) / max(d, 1e-4))


def filt(x: np.ndarray, kind: str, f, order: int = 2) -> np.ndarray:
    f = np.atleast_1d(f) / (SR / 2)
    b, a = signal.butter(order, f if len(f) > 1 else f[0], kind)
    return signal.lfilter(b, a, x)


def fsine(f: np.ndarray) -> np.ndarray:
    """Sine following a per-sample frequency curve."""
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def sweep(n: int, f0: float, f1: float, q: float, rng) -> np.ndarray:
    """Band-passed noise whose centre glides exponentially f0 -> f1 (block-wise filter)."""
    x, out, blk, zi = rng.standard_normal(n), np.zeros(n), 256, None
    for i in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (i / n)
        lo, hi = max(40, fc - fc / q / 2), min(SR / 2 - 200, fc + fc / q / 2)
        b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
        if zi is None:
            zi = np.zeros(max(len(a), len(b)) - 1)
        out[i:i + blk], zi = signal.lfilter(b, a, x[i:i + blk], zi=zi)
    return out


def tone(f: float, d: float, dec: float) -> np.ndarray:
    t = T(d)
    return np.sin(2 * np.pi * f * t) * env(len(t), 0.002, dec, 3)


def echo(x: np.ndarray, d: float = 0.11, fb: float = 0.3, n: int = 3) -> np.ndarray:
    out = np.concatenate([x, np.zeros(int(d * SR * n))])
    for k in range(1, n + 1):
        s = int(d * SR * k)
        out[s:s + len(x)] += x * fb ** k
    return out


def layer(*parts: np.ndarray) -> np.ndarray:
    """Sum arrays of different lengths (shorter ones are zero-padded)."""
    out = np.zeros(max(len(p) for p in parts))
    for p in parts:
        out[: len(p)] += p
    return out


def at(buf: np.ndarray, x: np.ndarray, t: float, g: float = 1.0) -> None:
    s = int(t * SR)
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s] * g


def tail_fade(x: np.ndarray, ms: float = 8) -> np.ndarray:
    """Short release (and a 1 ms attack ramp) so no sound starts or ends on a click."""
    n, a = min(len(x), int(ms / 1000 * SR)), int(0.001 * SR)
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)
    x[:a] *= np.linspace(0, 1, a)
    return x


# --------------------------------------------------------------------------- sounds
def click(rng):
    t = T(0.05)
    x = filt(rng.standard_normal(len(t)), "high", 3000) * env(len(t), 0.0002, 0.004, 5)
    return norm(x + np.sin(2 * np.pi * 1800 * t) * env(len(t), 0.0005, 0.01, 5) * 0.6, 0.55)


def tick(rng):
    return norm(tone(3200, 0.04, 0.01) + filt(rng.standard_normal(int(0.04 * SR)), "high", 6000)
                * env(int(0.04 * SR), 0.0002, 0.003, 5) * 0.3, 0.4)


def tap(rng):
    t = T(0.09)
    x = filt(rng.standard_normal(len(t)), "high", 2500) * env(len(t), 0.0003, 0.006, 5)
    return norm(x + np.sin(2 * np.pi * 180 * t) * env(len(t), 0.001, 0.03, 4) * 0.8, 0.5)


def pop(rng):
    t = T(0.18)
    f = 900 * 0.35 + 900 * 0.65 * np.exp(-t * 32)
    x = fsine(f) * env(len(t), 0.002, 0.06, 3)
    x += filt(rng.standard_normal(len(t)), "high", 3000) * env(len(t), 0.0004, 0.005, 5) * 0.2
    return norm(x, 0.5)


def whoosh_short(rng):
    n = int(0.32 * SR)
    return norm(sweep(n, 500, 4500, 1.5, rng) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 0.45)


def whip(rng):
    """Fast whip-pan: very short bright sweep with a hard ending + tiny crack."""
    n = int(0.18 * SR)
    x = sweep(n, 900, 8000, 1.2, rng) * np.linspace(0, 1, n) ** 2.5
    crack = filt(rng.standard_normal(int(0.02 * SR)), "high", 4000) * env(int(0.02 * SR), 0.0002, 0.004, 5)
    out = np.zeros(n + len(crack))
    out[:n] += x
    out[n - len(crack) // 2: n - len(crack) // 2 + len(crack)] += crack * 0.7
    return norm(out, 0.5)


def swoosh_up(rng):
    n = int(0.34 * SR)
    x = sweep(n, 250, 5000, 1.3, rng)
    return norm(x * np.linspace(0, 1, n) ** 1.7 * np.r_[np.ones(n - 900), np.linspace(1, 0, 900)], 0.45)


def swoosh_down(rng):
    n = int(0.34 * SR)
    return norm(sweep(n, 5000, 300, 1.3, rng) * np.sin(np.linspace(0, np.pi, n)) ** 1.2, 0.45)


def boom_sub(rng):
    """Portal / big reveal: pitch-dropping sub with a noise thump and short tail."""
    t = T(1.1)
    x = fsine(36 + 90 * np.exp(-t * 9)) * env(len(t), 0.003, 0.6, 2.5)
    x += filt(rng.standard_normal(len(t)), "low", 500) * env(len(t), 0.001, 0.08, 4) * 0.5
    return norm(np.tanh(1.5 * x), 0.85)


def glitch(rng):
    """Digital stutter: chopped, bit-crushed bursts of tones and noise."""
    out = np.zeros(int(0.32 * SR))
    pos = 0.0
    for i in range(9):
        d = [0.018, 0.03, 0.012, 0.025][i % 4]
        n = int(d * SR)
        f = [180, 1200, 640, 2400, 90][i % 5]
        burst = signal.square(2 * np.pi * f * np.arange(n) / SR) * 0.6 + rng.standard_normal(n) * 0.4
        burst = np.round(burst * 6) / 6                       # crude bit crush
        at(out, burst * np.r_[np.ones(n - 40), np.linspace(1, 0, 40)], pos, 0.5 + 0.5 * (i % 2))
        pos += d + (0.012 if i % 3 == 2 else 0.004)
    return norm(filt(out, "high", 120), 0.4)


def shutter(rng):
    out = np.zeros(int(0.25 * SR))
    for t0, g in ((0.0, 1.0), (0.07, 0.8)):
        n = int(0.03 * SR)
        at(out, filt(rng.standard_normal(n), "band", [1500, 7000]) * env(n, 0.0003, 0.008, 4), t0, g)
    return norm(out, 0.5)


def chime(rng):
    out = np.zeros(int(1.0 * SR))
    for i, f in enumerate((1567.98, 2093.0, 2637.0)):
        at(out, layer(tone(f, 0.6, 0.35), tone(f * 2.76, 0.3, 0.08) * 0.15), i * 0.06)
    return norm(out, 0.3)


def notification(rng):
    """Two-note phone-style ping (E6 -> B6) with a soft echo."""
    out = np.zeros(int(0.6 * SR))
    at(out, tone(1318.5, 0.25, 0.12), 0.0)
    at(out, tone(1975.5, 0.4, 0.2), 0.11)
    return norm(echo(out, 0.12, 0.2, 2), 0.32)


def typing_loop(rng):
    """Exactly 1.0 s of keyboard clatter that loops seamlessly (keys don't cross the end)."""
    out = np.zeros(SR)
    t, i = 0.02, 0
    while t < 0.94:
        n = int(0.03 * SR)
        key = filt(rng.standard_normal(n), "band", [1200 + 300 * (i % 4), 6000]) * env(n, 0.0003, 0.008, 5)
        body = np.sin(2 * np.pi * (250 + 40 * (i % 3)) * np.arange(n) / SR) * env(n, 0.001, 0.015, 5) * 0.4
        at(out, key + body, t, 0.6 + 0.4 * rng.random())
        t += 0.055 + 0.05 * rng.random()
        i += 1
    return norm(out, 0.35)


def riser_1s(rng):
    n, t = SR, T(1.0)
    nz = sweep(n, 300, 9000, 1.2, rng) * np.linspace(0, 1, n) ** 2.2
    tn = signal.sawtooth(2 * np.pi * np.cumsum(220 * 2 ** (t * 2.0)) / SR) * np.linspace(0, 1, n) ** 3 * 0.25
    return norm(filt(nz + tn, "high", 200), 0.5)


def bass_hit(rng):
    t = T(1.0)
    x = np.tanh(2.2 * fsine(55 * (1 + 1.5 * np.exp(-t * 30)))) * env(len(t), 0.002, 0.7, 2)
    return norm(x, 0.8)


def success(rng):
    """Rising major arpeggio C6-E6-G6-C7 — 'done / unlocked'."""
    out = np.zeros(int(0.9 * SR))
    for i, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
        at(out, layer(tone(f, 0.45, 0.25), tone(f * 2, 0.2, 0.06) * 0.2), i * 0.07)
    return norm(echo(out, 0.1, 0.18, 2), 0.32)


def whoosh_long(rng):
    """Airy transition whoosh with body: noise sweeps up 250 -> 5000 Hz over 0.55 s."""
    n = int(0.55 * SR)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.3
    body = sweep(n, 250, 5000, 1.2, rng) * shape
    air = filt(rng.standard_normal(n), "high", 4000) * shape ** 3 * 0.15
    return norm(body + air, 0.5)


def whoosh_air(rng):
    """Soft falling swish 6 kHz -> 600 Hz (scene-to-scene, gentle)."""
    n = int(0.45 * SR)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    return norm(sweep(n, 6000, 600, 0.8, rng) * shape, 0.42)


def impact_soft(rng):
    """Statement hit that still reads on phone speakers: 90 Hz thump + 350 Hz body + transient."""
    t = T(0.6)
    sub = fsine(90 * (1 + 0.8 * np.exp(-t * 25))) * env(len(t), 0.002, 0.35, 3)
    bodyt = np.sin(2 * np.pi * 350 * t) * env(len(t), 0.001, 0.12, 4) * 0.5
    hit = filt(rng.standard_normal(len(t)), "low", 2500) * env(len(t), 0.0005, 0.03, 5) * 0.6
    return norm(np.tanh(1.6 * (sub + bodyt + hit)), 0.7)


def pop_bright(rng):
    """Bubbly entrance pop (higher than `pop`, cuts through on phones)."""
    t = T(0.15)
    x = fsine(600 + 800 * np.exp(-t * 40)) * env(len(t), 0.001, 0.05, 3)
    x += filt(rng.standard_normal(len(t)), "high", 4000) * env(len(t), 0.0003, 0.004, 5) * 0.25
    return norm(x, 0.5)


KIT = [click, tick, tap, pop, whoosh_short, whip, swoosh_up, swoosh_down, boom_sub, glitch,
       shutter, chime, notification, typing_loop, riser_1s, bass_hit, success,
       whoosh_long, whoosh_air, impact_soft, pop_bright]   # new sounds go at the END (seeds = index)


def write(path: Path, x: np.ndarray) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--only", help="comma-separated subset of sound names")
    ap.add_argument("--list", action="store_true", help="print sound names and exit")
    args = ap.parse_args(argv)
    if args.list:
        print("\n".join(fn.__name__ for fn in KIT))
        return
    wanted = set(args.only.split(",")) if args.only else None
    unknown = (wanted or set()) - {fn.__name__ for fn in KIT}
    if unknown:
        print(f"error: unknown sounds: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(1)
    args.out.mkdir(parents=True, exist_ok=True)
    total = 0
    for seed, fn in enumerate(KIT):
        if wanted and fn.__name__ not in wanted:
            continue
        x = fn(np.random.default_rng(100 + seed))
        x = x if fn is typing_loop else tail_fade(x)   # the loop must stay exactly 1.0 s
        path = args.out / f"{fn.__name__}.wav"
        write(path, x)
        total += path.stat().st_size
        print(f"{path.name:18s} {len(x) / SR:5.2f}s")
    print(f"total {total / 1e6:.2f} MB -> {args.out}")


if __name__ == "__main__":
    main()
