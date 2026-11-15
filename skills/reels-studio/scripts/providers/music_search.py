#!/usr/bin/env python3
"""Find a real, commercially usable music track on the internet, rank it by fit, conform it.

Sources (no paid keys needed):
  1. Openverse audio API   https://api.openverse.org/v1/audio/  (no key; CC0 / PDM / CC BY by default)
  2. Jamendo API           only when JAMENDO_CLIENT_ID is set (NC/ND tracks filtered out)
  Freesound (SFX only)     `freesound_sfx()` when FREESOUND_API_KEY is set — used by sfx_plan.py

Pipeline
  query   niche preset `music` mood + BPM (assets/niches.json) + style + brief topic + energy
  filter  licence (reject NC/ND; SA only with --allow-sa), vocals in tags/title, duration ≥ needed
          (or ≥ 15 s and loopable), mature
  analyse librosa on the downloaded file: tempo, onset rate (energy), spectral centroid, share of
          power < 150 Hz (sub-bass beds are inaudible on phone speakers -> rejected when > 70 % or
          when < 15 % sits in 300–5000 Hz),
          share of power in the 300–5000 Hz phone band; "too sleepy" tracks rejected for
          energetic briefs
  rank    licence preference (CC0 > BY > BY-SA) + BPM fit + energy fit + phone-band audibility
  write   audio/music_candidates.json (top 3: title, artist, licence, attribution, source url, bpm,
          score…), audio/music_src.<ext> (chosen original), audio/music.wav (exact length:
          starts on a downbeat after any quiet intro, 0.5 s fade-in, 1.2 s fade-out — or a
          bar-aligned seamless loop with equal-power crossfades when the track is too short),
          work/<slug>/CREDITS.txt + env.json -> used.music {licence, attribution, source_url}

Usage: music_search.py --work work/<slug> [--dur 41.2] [--mood "…"] [--bpm 100-110]
                       [--energy high|medium] [--query "extra words"] [--pick N] [--allow-sa]
                       [--out audio/music.wav] [--max-download 6]
Exit code 3 = nothing suitable found / network down (music.py then tries the next provider).
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import math
import os
import re
import shutil
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SKILL_DIR, ProviderError, ffmpeg, load_dotenv, log, record_used, write_json  # noqa: E402

SR = 48000
UA = {"User-Agent": "reels-studio/1.0 (music search; +https://openverse.org)"}
OPENVERSE = "https://api.openverse.org/v1/audio/"
LIC_LABEL = {"cc0": "CC0 1.0", "pdm": "Public Domain Mark", "by": "CC BY", "by-sa": "CC BY-SA"}
LIC_SCORE = {"cc0": 3.0, "pdm": 3.0, "by": 2.0, "by-sa": 0.5}
VOCAL_WORDS = ("vocal", "vocals", "voice", "singer", "singing", "lyrics", "lyric", "rap", "feat", "ft.",
               "acapella", "choir", "song")
STOP = {"with", "and", "no", "light", "very", "soft", "bed", "sub-bass", "subbass", "bass", "deep", "round",
        "gentle", "pulse", "groove", "pad", "minimal", "subtle", "slow", "the", "a", "of", "for", "like",
        "jingle", "childish", "clean", "tight", "shimmer", "steady"}
HIGH_WORDS = ("driving", "punchy", "upbeat", "bright", "bouncy", "energetic", "motivated", "hype", "fast",
              "confident", "playful", "modern")
CALM_WORDS = ("calm", "soft", "steady", "minimal", "gentle", "cosy", "cozy", "smooth", "airy", "sweet")
GENRE_GOOD = {"high": ("upbeat", "electronic", "pop", "funk", "corporate", "hiphop", "dance", "house",
                       "rock", "indie", "motivational", "energetic", "lounge"),
              "medium": ("corporate", "lounge", "chillout", "lofi", "pop", "electronic", "indie", "acoustic",
                         "jazz", "funk", "hiphop", "positive")}
GENRE_BAD = ("ambient", "classical", "drone", "soundscape", "noise", "experimental", "meditation", "horror")


class NoMatch(RuntimeError):
    pass


# --------------------------------------------------------------------------- http
def get_json(url: str, timeout: float = 25) -> dict:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ProviderError(f"HTTP {e.code} from {url.split('?')[0]}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ProviderError(f"network error for {url.split('?')[0]}: {e}") from None


# Downloads follow URLs that come from third-party API responses, so treat them as untrusted:
# https only, public IPs only (checked on every redirect hop), known audio extensions only.
AUDIO_EXTS = {"mp3", "ogg", "wav", "flac", "m4a", "opus"}


def safe_ext(ft: str | None) -> str:
    ft = (ft or "mp3").lower().replace("mp32", "mp3")
    return ft if ft in AUDIO_EXTS else "mp3"


def check_public_https(url: str) -> None:
    u = urllib.parse.urlsplit(url)
    if u.scheme != "https" or not u.hostname:
        raise ProviderError(f"refusing non-https download URL: {url[:80]}")
    try:
        infos = socket.getaddrinfo(u.hostname, u.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise ProviderError(f"cannot resolve {u.hostname}: {e}") from None
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast:
            raise ProviderError(f"refusing download from non-public address {ip} ({u.hostname})")


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_SAFE_OPENER = urllib.request.build_opener(_SafeRedirect)


def download(url: str, dst: Path, cap_mb: float = 25, timeout: float = 60) -> Path:
    check_public_https(url)
    req = urllib.request.Request(url, headers=UA)
    dst.parent.mkdir(parents=True, exist_ok=True)
    got = 0
    try:
        with _SAFE_OPENER.open(req, timeout=timeout) as r, open(dst, "wb") as f:
            while chunk := r.read(1 << 16):
                got += len(chunk)
                if got > cap_mb * 1e6:
                    raise ProviderError(f"download larger than {cap_mb} MB — skipped")
                f.write(chunk)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        dst.unlink(missing_ok=True)
        raise ProviderError(f"download failed: {e}") from None
    except ProviderError:
        dst.unlink(missing_ok=True)
        raise
    if got < 20000:
        dst.unlink(missing_ok=True)
        raise ProviderError("download too small (not audio?)")
    return dst


# --------------------------------------------------------------------------- brief -> search intent
def load_intent(work: Path | None, mood: str | None, bpm: str | None, energy: str | None,
                extra: str | None, dur: float | None) -> dict:
    brief, scenes, preset = {}, {}, {}
    if work:
        for name, var in (("brief.json", "brief"), ("plan/scenes.json", "scenes")):
            p = work / name
            if p.is_file():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    data = {}
                if var == "brief":
                    brief = data
                else:
                    scenes = data
    niches = json.loads((SKILL_DIR / "assets" / "niches.json").read_text(encoding="utf-8")).get("niches", {})
    niche = brief.get("niche") or brief.get("niche_id") or "default"
    preset = (niches.get(niche) or niches.get("default") or {}).get("music", {})
    music_cfg = (scenes.get("audio") or {}).get("music") or {}
    mood = mood or music_cfg.get("mood") or preset.get("mood") or "upbeat corporate"
    if bpm:
        parts = [float(v) for v in re.split(r"[-–,]", str(bpm)) if v.strip()]
        rng = (min(parts), max(parts))
    elif music_cfg.get("bpm"):
        rng = (float(music_cfg["bpm"]) - 6, float(music_cfg["bpm"]) + 6)
    elif preset.get("bpm"):
        rng = tuple(float(v) for v in preset["bpm"])
    else:
        rng = (100.0, 120.0)
    low = mood.lower()
    if not energy:
        energy = "high" if any(w in low for w in HIGH_WORDS) else "medium"
        if brief.get("audio_profile", "energetic") == "energetic" and energy == "medium" and \
                not any(w in low for w in CALM_WORDS):
            energy = "high"
    if dur is None:
        total = float(scenes.get("duration") or 0)
        dur = max(1.0, total - float(music_cfg.get("start", 0) or 0)) if total else 30.0
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-]+", low) if w not in STOP]
    return {"mood": mood, "bpm": rng, "energy": energy, "dur": dur, "niche": niche,
            "style": brief.get("style"), "topic": brief.get("topic") or "", "mood_words": words,
            "extra": (extra or "").strip()}


def queries_for(intent: dict) -> list[str]:
    qs: list[str] = []
    if intent["extra"]:
        qs.append(intent["extra"])
    mw = intent["mood_words"]
    for w in mw[:3]:
        qs.append(w)
    if len(mw) >= 2:
        qs.insert(0, f"{mw[0]} {mw[1]}")
    base = (["upbeat", "corporate", "motivational", "energetic", "funk", "electronic"]
            if intent["energy"] == "high" else ["corporate", "chill", "lofi", "positive", "lounge"])
    qs += base
    seen, out = set(), []
    for q in qs:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out[:8]


# --------------------------------------------------------------------------- sources
def norm_licence(code: str) -> str | None:
    c = (code or "").lower().replace("_", "-")
    if "nc" in c.split("-") or "nd" in c.split("-"):
        return None
    if c in ("cc0", "pdm", "by", "by-sa"):
        return c
    return None


def search_openverse(qs: list[str], allow_sa: bool, pages: int = 2) -> list[dict]:
    lic = "cc0,pdm,by" + (",by-sa" if allow_sa else "")
    found: dict[str, dict] = {}
    errors = 0
    for q in qs:
        for page in range(1, pages + 1):
            url = OPENVERSE + "?" + urllib.parse.urlencode(
                {"q": q, "license": lic, "license_type": "commercial", "category": "music",
                 "page_size": 20, "page": page, "mature": "false"})
            try:
                data = get_json(url)
            except ProviderError as e:
                errors += 1
                log(f"[music_search] openverse '{q}' p{page}: {e}")
                break
            for r in data.get("results", []):
                licence = norm_licence(r.get("license", ""))
                if not licence or not r.get("url") or r.get("mature"):
                    continue
                dur = (r.get("duration") or 0) / 1000.0
                found.setdefault(r["id"], {
                    "provider": "openverse/" + (r.get("source") or r.get("provider") or "?"),
                    "id": r["id"], "title": r.get("title") or "Untitled", "artist": r.get("creator") or "Unknown",
                    "licence": licence, "licence_version": r.get("license_version") or "",
                    "licence_url": r.get("license_url") or "", "source_url": r.get("foreign_landing_url") or "",
                    "file_url": r["url"], "filetype": safe_ext(r.get("filetype")),
                    "duration": dur, "genres": [g.lower() for g in (r.get("genres") or [])],
                    "tags": [t["name"].lower() for t in (r.get("tags") or []) if t.get("name")],
                    "attribution": r.get("attribution") or "", "query": q})
            if page >= int(data.get("page_count") or 1):
                break
    if not found and errors:
        raise ProviderError("openverse unreachable")
    return list(found.values())


def search_jamendo(qs: list[str], intent: dict, allow_sa: bool) -> list[dict]:
    cid = os.environ.get("JAMENDO_CLIENT_ID", "").strip()
    if not cid:
        return []
    out = []
    speed = "high+veryhigh" if intent["energy"] == "high" else "medium+high"
    for q in qs[:4]:
        url = "https://api.jamendo.com/v3.0/tracks/?" + urllib.parse.urlencode(
            {"client_id": cid, "format": "json", "limit": 30, "fuzzytags": q.replace(" ", "+"),
             "vocalinstrumental": "instrumental", "include": "licenses musicinfo", "audioformat": "mp32",
             "speed": speed, "order": "popularity_total", "durationbetween": f"{int(min(intent['dur'], 60))}_600"})
        try:
            data = get_json(url)
        except ProviderError as e:
            log(f"[music_search] jamendo '{q}': {e}")
            continue
        for t in data.get("results", []):
            m = re.search(r"licenses/([a-z\-]+)/([\d.]+)", t.get("license_ccurl") or "")
            licence = norm_licence(m.group(1)) if m else None
            if not licence or (licence == "by-sa" and not allow_sa):
                continue
            file_url = t.get("audiodownload") if t.get("audiodownload_allowed") else t.get("audio")
            if not file_url:
                continue
            title, artist, ver = t.get("name") or "Untitled", t.get("artist_name") or "Unknown", m.group(2)
            lic_url = t.get("license_ccurl")
            mi = t.get("musicinfo") or {}
            out.append({"provider": "jamendo", "id": f"jamendo-{t['id']}", "title": title, "artist": artist,
                        "licence": licence, "licence_version": ver, "licence_url": lic_url,
                        "source_url": t.get("shareurl") or "", "file_url": file_url, "filetype": "mp3",
                        "duration": float(t.get("duration") or 0),
                        "genres": [g.lower() for g in (mi.get("tags") or {}).get("genres", [])],
                        "tags": ["instrumental"] + [g.lower() for g in (mi.get("tags") or {}).get("vartags", [])],
                        "attribution": f"\"{title}\" by {artist} is licensed under {LIC_LABEL[licence]} {ver}. "
                                       f"To view a copy of this license, visit {lic_url}.", "query": q})
    return out


def freesound_sfx(query: str, dst: Path, max_dur: float = 2.0) -> dict | None:
    """Fetch one CC0 sound effect from Freesound (needs FREESOUND_API_KEY). Returns a credit dict."""
    token = os.environ.get("FREESOUND_API_KEY", "").strip()
    if not token:
        return None
    url = "https://freesound.org/apiv2/search/text/?" + urllib.parse.urlencode(
        {"query": query, "filter": f'license:"Creative Commons 0" duration:[0.1 TO {max_dur}]',
         "fields": "id,name,username,license,url,duration,previews", "page_size": 10,
         "sort": "rating_desc", "token": token})
    try:
        data = get_json(url)
        for r in data.get("results", []):
            prev = (r.get("previews") or {}).get("preview-hq-mp3")
            if not prev:
                continue
            raw = download(prev, dst.with_suffix(".dl.mp3"), cap_mb=5)
            ffmpeg("-i", str(raw), "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(dst))
            raw.unlink(missing_ok=True)
            return {"name": dst.stem, "title": r.get("name"), "artist": r.get("username"), "licence": "cc0",
                    "source_url": r.get("url"), "provider": "freesound"}
    except (ProviderError, RuntimeError) as e:
        log(f"[freesound] {query}: {e}")
    return None


# --------------------------------------------------------------------------- scoring
def meta_score(c: dict, intent: dict) -> tuple[float, list[str]]:
    reasons, s = [], LIC_SCORE[c["licence"]]
    reasons.append(f"licence {c['licence']}")
    text = " ".join([c["title"].lower(), *c["tags"], *c["genres"]])
    if any(re.search(rf"\b{re.escape(w)}\b", text) for w in VOCAL_WORDS) and "instrumental" not in c["tags"]:
        s -= 3
        reasons.append("vocals?")
    if "instrumental" in c["tags"]:
        s += 1.5
        reasons.append("instrumental")
    need = intent["dur"]
    if c["duration"] >= need + 1:
        s += 2
    elif c["duration"] >= 15:
        s += 0.5
        reasons.append("needs loop")
    elif c["duration"]:
        s -= 10
    good = GENRE_GOOD["high" if intent["energy"] == "high" else "medium"]
    if any(g in text for g in good):
        s += 1
    if any(g in text for g in GENRE_BAD):
        s -= 1.5
    if intent["energy"] == "high":
        s += 1 if "speed_high" in c["tags"] or "speed_veryhigh" in c["tags"] else 0
        s -= 1 if "speed_low" in c["tags"] or "speed_verylow" in c["tags"] else 0
    s += 0.5 * sum(1 for w in intent["mood_words"] if w in text)
    return s, reasons


def analyse(path: Path) -> dict:
    import librosa
    y, sr = librosa.load(str(path), sr=22050, mono=True, duration=120)
    if len(y) < sr * 5:
        raise ProviderError("track shorter than 5 s")
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_t = librosa.frames_to_time(beats, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    S = np.abs(librosa.stft(y, n_fft=4096, hop_length=1024)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)
    total = S.sum() + 1e-12
    low_ratio = float(S[freqs < 150].sum() / total)
    phone_ratio = float(S[(freqs >= 300) & (freqs <= 5000)].sum() / total)
    centroid = float(np.median(librosa.feature.spectral_centroid(S=np.sqrt(S), sr=sr)))
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=1024)[0]
    rms_db = 20 * np.log10(rms + 1e-9)
    # downbeat phase: of the 4 possible bar phases pick the one with the strongest onsets
    phase = 0
    if len(beats) >= 8:
        strength = [onset_env[beats[p::4]].mean() for p in range(4)]
        phase = int(np.argmax(strength))
    return {"bpm": round(tempo, 1), "beats": beat_t.tolist(), "downbeats": beat_t[phase::4].tolist(),
            "onset_rate": round(len(onsets) / (len(y) / sr), 2), "centroid_hz": round(centroid),
            "low_ratio": round(low_ratio, 3), "phone_ratio": round(phone_ratio, 3),
            "rms_db_median": round(float(np.median(rms_db)), 1),
            "rms_curve": rms_db[:: max(1, int(sr / 1024 / 2))].round(1).tolist(),   # ~2 values/s
            "analysed_sec": round(len(y) / sr, 1)}


def fit_score(c: dict, a: dict, intent: dict) -> tuple[float, list[str]]:
    lo, hi = intent["bpm"]
    reasons, s = [], 0.0
    # power spectra of most produced music are bass-heavy, so "mostly sub" means > 70 % below
    # 150 Hz, or too little left in the band a phone speaker actually reproduces
    if a["low_ratio"] > 0.7 or a["phone_ratio"] < 0.15:
        raise NoMatch(f"{a['low_ratio']:.0%} of energy below 150 Hz, {a['phone_ratio']:.0%} in 300–5000 Hz "
                      "(inaudible on phone speakers)")
    sleepy = a["onset_rate"] < (1.2 if intent["energy"] == "high" else 0.6)
    if sleepy or (intent["energy"] == "high" and a["centroid_hz"] < 700):
        raise NoMatch(f"too sleepy (onsets {a['onset_rate']}/s, centroid {a['centroid_hz']} Hz)")
    d = min(abs(b - min(max(b, lo), hi)) for b in (a["bpm"], a["bpm"] * 2, a["bpm"] / 2))
    s += max(-2.0, 2.0 - d / 8)
    reasons.append(f"bpm {a['bpm']:.0f} (Δ{d:.0f})")
    s += min(a["onset_rate"] / 3.0, 1.0) * (2.0 if intent["energy"] == "high" else 1.0)
    s += 3.0 * a["phone_ratio"]
    if 1000 <= a["centroid_hz"] <= 3500:
        s += 1
    reasons.append(f"phone-band {a['phone_ratio']:.0%}, onsets {a['onset_rate']}/s")
    return s, reasons


# --------------------------------------------------------------------------- fit to length
def _sin_fade(n: int, up: bool) -> np.ndarray:
    x = np.linspace(0, np.pi / 2, max(n, 1), dtype=np.float32)
    return np.sin(x) if up else np.cos(x)


def pick_start(a: dict, track_len: float, dur: float) -> float:
    """First downbeat at/after which the track is at full level (skips a quiet intro)."""
    downs = [t for t in a["downbeats"] if t + dur <= track_len - 0.1]
    if not downs:
        return 0.0
    curve = np.array(a["rms_curve"])
    full = np.median(curve) - 4
    for t in downs:
        i = int(t * 2)
        if i < len(curve) and curve[i: i + 4].mean() >= full:
            return float(t)
    return float(downs[0])


def loop_body(x: np.ndarray, a: dict, dur: float, xf: float = 0.3) -> tuple[np.ndarray, str]:
    """Repeat a bar-aligned section with equal-power crossfades until `dur` (+ tail)."""
    downs = a["downbeats"] or [0.0]
    total = x.shape[1] / SR
    b0 = next((t for t in downs if t >= 0.0), 0.0)
    cands = [t for t in downs if t <= total - xf - 0.05 and t - b0 >= 4.0]
    b1 = cands[-1] if cands else total - xf - 0.05
    s0, s1, nx = int(b0 * SR), int(b1 * SR), int(xf * SR)
    body = x[:, s0: s1 + nx]
    out = x[:, : s1 + nx].copy()
    need = int(dur * SR) + nx
    up, dn = _sin_fade(nx, True), _sin_fade(nx, False)
    while out.shape[1] < need:
        tail = out[:, -nx:] * dn + body[:, :nx] * up
        out = np.concatenate([out[:, :-nx], tail, body[:, nx:]], axis=1)
    return out, f"loop {b0:.2f}-{b1:.2f}s (bar-aligned, {xf:.1f}s equal-power xfade)"


def conform(src: Path, a: dict, dur: float, dst: Path) -> str:
    import audio_meter as am
    x = am.decode(src, 2)
    total = x.shape[1] / SR
    if total >= dur + 0.2:
        start = pick_start(a, total, dur)
        y = x[:, int(start * SR): int(start * SR) + int(round(dur * SR))]
        how = f"trim from downbeat {start:.2f}s"
    else:
        y, how = loop_body(x, a, dur)
        y = y[:, : int(round(dur * SR))]
    n = int(round(dur * SR))
    y = np.pad(y, ((0, 0), (0, max(0, n - y.shape[1]))))[:, :n].astype(np.float32)
    fi, fo = int(min(0.5, dur / 4) * SR), int(min(1.2, dur / 4) * SR)
    y[:, :fi] *= _sin_fade(fi, True)
    y[:, n - fo:] *= _sin_fade(fo, False)
    peak = float(np.max(np.abs(y))) or 1.0
    if peak > 0.98:
        y *= 0.98 / peak
    import subprocess
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s16le", str(dst)], input=y.T.astype("<f4").tobytes(), check=True)
    return how + ", fade-in 0.5 s, fade-out 1.2 s"


# --------------------------------------------------------------------------- credits
def write_credits(work: Path, section: str, lines: list[str]) -> Path:
    """Replace one [section] of work/<slug>/CREDITS.txt (music / sfx), keeping the others."""
    p = work / "CREDITS.txt"
    sections: dict[str, list[str]] = {}
    if p.is_file():
        cur = None
        for ln in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\[(\w+)\]$", ln.strip())
            if m:
                cur = m.group(1)
                sections[cur] = []
            elif cur:
                sections[cur].append(ln)
    sections[section] = lines
    out = ["# CREDITS — third-party audio and video in this reel. Lines marked CAPTION must be pasted into the",
           "# post caption (CC BY / CC BY-SA require attribution). CC0 / bundled kit need none.", ""]
    for name in ("music", "sfx", *[s for s in sections if s not in ("music", "sfx")]):
        if name in sections:
            out += [f"[{name}]", *[ln for ln in sections[name] if ln.strip()], ""]
    p.write_text("\n".join(out), encoding="utf-8")
    return p


def caption_line(c: dict) -> str:
    lic = f"{LIC_LABEL[c['licence']]} {c.get('licence_version') or ''}".strip()
    return f"Music: \"{c['title']}\" by {c['artist']} ({lic}) {c['source_url']}".strip()


def record_music(work: Path | None, out: Path, c: dict, how: str) -> None:
    record_used(out, "music", c["provider"], f"\"{c['title']}\" by {c['artist']} — {LIC_LABEL[c['licence']]}; {how}")
    if not work:
        return
    env_p = work / "env.json"
    if env_p.is_file():
        env = json.loads(env_p.read_text(encoding="utf-8"))
        env.setdefault("used", {}).setdefault("music", {}).update(
            {"title": c["title"], "artist": c["artist"], "licence": c["licence"],
             "licence_version": c.get("licence_version"), "licence_url": c.get("licence_url"),
             "attribution": c["attribution"], "source_url": c["source_url"],
             "attribution_required": c["licence"] in ("by", "by-sa")})
        write_json(env_p, env)
    lines = [f"track: \"{c['title']}\" by {c['artist']} — {LIC_LABEL[c['licence']]} {c.get('licence_version', '')}".rstrip(),
             f"source: {c['source_url']}", f"licence: {c.get('licence_url') or ''}",
             f"attribution: {c['attribution']}"]
    if c["licence"] in ("by", "by-sa"):
        lines.append(f"CAPTION: {caption_line(c)}")
    else:
        lines.append("CAPTION: (not required — public domain / CC0)")
    write_credits(work, "music", lines)


# --------------------------------------------------------------------------- main flow
def search(intent: dict, out: Path, work: Path | None, allow_sa: bool = False, max_download: int = 6,
           pick: int = 1) -> dict:
    audio_dir = out.parent
    cand_dir = audio_dir / "music_cands"
    cands_json = audio_dir / "music_candidates.json"
    # --pick N on an existing candidates file: reuse, no new search
    if pick > 1 and cands_json.is_file():
        data = json.loads(cands_json.read_text(encoding="utf-8"))
        ranked = data["candidates"]
        if pick > len(ranked):
            raise NoMatch(f"only {len(ranked)} candidates")
    else:
        qs = queries_for(intent)
        log(f"[music_search] energy={intent['energy']} bpm={intent['bpm'][0]:.0f}-{intent['bpm'][1]:.0f} "
            f"need {intent['dur']:.1f}s; queries: {qs}")
        pool = search_openverse(qs, allow_sa)
        try:
            pool += search_jamendo(qs, intent, allow_sa)
        except ProviderError as e:
            log(f"[music_search] jamendo: {e}")
        if not pool:
            raise NoMatch("no search results")
        for c in pool:
            c["meta_score"], c["reasons"] = meta_score(c, intent)
        pool = [c for c in pool if c["meta_score"] > -5]
        pool.sort(key=lambda c: -c["meta_score"])
        log(f"[music_search] {len(pool)} licence-clean results; analysing top {max_download}")
        if cand_dir.exists():
            shutil.rmtree(cand_dir)
        cand_dir.mkdir(parents=True)
        ranked = []
        for i, c in enumerate(pool[: max_download * 2]):
            if len(ranked) >= max_download or i >= max_download * 2:
                break
            f = cand_dir / f"{len(ranked) + 1:02d}_{re.sub(r'[^A-Za-z0-9]+', '_', str(c['id']))[:24]}.{safe_ext(c.get('filetype'))}"
            if not f.resolve().is_relative_to(cand_dir.resolve()):
                continue
            try:
                download(c["file_url"], f)
                a = analyse(f)
                fs, why = fit_score(c, a, intent)
            except NoMatch as e:
                log(f"[music_search]  reject \"{c['title']}\": {e}")
                f.unlink(missing_ok=True)
                continue
            except (ProviderError, RuntimeError, ValueError, OSError) as e:
                log(f"[music_search]  skip \"{c['title']}\": {e}")
                f.unlink(missing_ok=True)
                continue
            c.update(analysis={k: v for k, v in a.items() if k not in ("beats", "rms_curve", "downbeats")},
                     _a=a, file=str(f), score=round(c["meta_score"] + fs, 2), reasons=c["reasons"] + why)
            ranked.append(c)
            log(f"[music_search]  ok \"{c['title']}\" by {c['artist']} [{c['licence']}] score {c['score']} "
                f"(bpm {a['bpm']:.0f}, onsets {a['onset_rate']}/s, <150Hz {a['low_ratio']:.0%}, "
                f"phone {a['phone_ratio']:.0%})")
        if not ranked:
            raise NoMatch("no candidate passed the audibility / energy analysis")
        ranked.sort(key=lambda c: -c["score"])
        for c in ranked[3:]:
            Path(c["file"]).unlink(missing_ok=True)
        ranked = ranked[:3]
        for r, c in enumerate(ranked, 1):
            c["rank"] = r
        write_json(cands_json, {"query": {k: intent[k] for k in ("mood", "bpm", "energy", "dur", "niche", "style")},
                                "chosen": pick, "note": "re-run with --pick N to use another candidate",
                                "candidates": [{k: v for k, v in c.items() if not k.startswith("_")} for c in ranked]})
    chosen = ranked[pick - 1]
    src_file = Path(chosen["file"])
    if not src_file.is_file():
        raise NoMatch(f"candidate file missing: {src_file}")
    a = chosen.get("_a") or analyse(src_file)
    music_src = audio_dir / f"music_src.{src_file.suffix.lstrip('.')}"
    for old in audio_dir.glob("music_src.*"):
        old.unlink()
    shutil.copy2(src_file, music_src)
    how = conform(music_src, a, intent["dur"], out)
    if pick > 1 and cands_json.is_file():
        data = json.loads(cands_json.read_text(encoding="utf-8"))
        data["chosen"] = pick
        write_json(cands_json, data)
    record_music(work, out, chosen, how)
    return chosen


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--work", type=Path)
    ap.add_argument("--dur", type=float)
    ap.add_argument("--mood")
    ap.add_argument("--bpm", help="e.g. 104-114 or 108")
    ap.add_argument("--energy", choices=("high", "medium"))
    ap.add_argument("--query", help="extra search words (e.g. from the brief)")
    ap.add_argument("--pick", type=int, default=1, help="use candidate N of audio/music_candidates.json")
    ap.add_argument("--allow-sa", action="store_true", help="also accept CC BY-SA")
    ap.add_argument("--max-download", type=int, default=6)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    load_dotenv()
    if not a.work and not a.out:
        ap.error("--work or --out is required")
    out = a.out or a.work / "audio" / "music.wav"
    intent = load_intent(a.work, a.mood, a.bpm, a.energy, a.query, a.dur)
    try:
        c = search(intent, out, a.work, a.allow_sa, a.max_download, a.pick)
    except (NoMatch, ProviderError) as e:
        print(f"error: music search: {e}", file=sys.stderr)
        sys.exit(3)
    print(f"{out}: {intent['dur']:.2f}s from \"{c['title']}\" by {c['artist']} [{LIC_LABEL[c['licence']]}] "
          f"score {c['score']} — {c['source_url']}")


if __name__ == "__main__":
    main()
