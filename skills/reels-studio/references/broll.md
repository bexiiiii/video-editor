# Automatic topic B-roll — `scripts/broll.py`

A reel feels real when the screen shows the thing the speaker names: the kolesa.kz listing, the kaspi.kz product page,
city traffic. The director marks those scenes; `broll.py` produces one muted vertical clip per scene.

## 1. Director: mark the scene (plan/scenes.json)
```json
{"id": "s06", "start": 13.96, "end": 15.96, "layout": "media",
 "broll": {"kind": "screen", "url": "https://kolesa.kz/cars/", "seconds": 2.0}}
```
| kind | when | fields |
|---|---|---|
| `screen` | the script names a website / app / marketplace (kolesa → `https://kolesa.kz/cars/`, kaspi → `https://kaspi.kz/shop/`, krisha → `https://krisha.kz/prodazha/kvartiry/`, the client's own site) | `url` (public https page, no login), optional `query` = stock fallback, `desktop: true` to force the desktop layout |
| `stock` | a generic action / place ("car dealership", "office team", "city traffic") | `query` in **English** (stock APIs index English) |
| `generated` | nothing real fits and the client approved ElevenLabs credits | `query` = prompt; produced by the orchestrator (§4) |
`seconds` defaults to the scene length (max 20). Style F: ≤ 1 `media` scene per 20 s; other styles use the clip in
any `media` / full-bleed layout. Prefer the client's own screen recording (`materials.md`) — ask for it first.

## 2. Run
```bash
$SKILL/scripts/run broll.py --work work/<slug>            # all scenes with "broll"; --scene s06 for one; --force redo
$SKILL/scripts/run broll.py --url https://kolesa.kz/cars/ --seconds 8 --out /tmp/k.mp4      # single test
$SKILL/scripts/run broll.py --query "car traffic" --seconds 6 --out /tmp/t.mp4 [--provider wikimedia]
```
Output per scene: `broll/<id>.mp4` (1080×1920, H.264 yuv420p, 30 fps, **no audio**) + `broll/<id>.json`
{status ok|slot|needs_connector, source client|screen|stock, provider, url, title, author, licence, licence_url,
attribution, notes}; `broll/index.json`; `env.json → used.broll_<id>`; `CREDITS.txt [broll]` (CC BY / BY-SA lines
are marked CAPTION → paste into the post caption).

## 3. Chain (first success wins)
1. **Client material** — `plan/materials.json` item `{scene, kind: broll|screen_recording, status: received, path}` or
   `input/<id>_broll*.mp4|mov|webm` → conformed (centre crop 9:16, trim/loop, 30 fps, muted).
2. **Screen capture** (`kind: screen` + `url`) — `providers/screen_capture.mjs`, Node ≥ 22, no npm packages: drives
   the Chrome HyperFrames installed (`npx hyperframes browser path`, override `HYPERFRAMES_CHROME`) over the DevTools
   protocol. Mobile viewport 432×768 @2.5 = 1080×1920 with a mobile UA; if the mobile page does not move (app-install
   interstitial / fixed overlay) it retries the desktop layout (1080×1920 @1). Deterministic frame stepping: frame i is
   scrolled to a sine-eased y(i) and screenshotted, so the scroll is perfectly smooth at 30 fps (default 90 CSS px/s,
   `speed`). `hyperframes capture` was evaluated: it extracts a site into editable components + screenshots, no scroll
   video — not used here.
3. **Stock video** (`query`) — Pexels (`PEXELS_API_KEY`, Pexels License) → Pixabay (`PIXABAY_API_KEY`, Pixabay Content
   License) → **Wikimedia Commons** (no key; only `cc0`, `cc-by-*`, `cc-by-sa-*`; relevance from title + description +
   categories; diagrams / simulations / tutorials skipped; a clip shorter than `seconds` is penalised because a loop
   reads as a glitch). Portrait preferred, else centre-cropped to 9:16; starts a little into the clip.
4. **Generated** — never by the script: status `needs_connector` (§4).
5. **Labelled slot** — status `slot`: the scene keeps the style's labelled B-roll slot; list it in the final report.

## 4. Generated B-roll (ElevenLabs connector, orchestrator only)
Only when the client approved the credit spend (`connector-elevenlabs.md` → video row). The orchestrator generates,
downloads to `input/<id>_broll_gen.mp4`, then re-runs `broll.py --scene <id> --force` (it is picked up as client
material and conformed), and records `source: generated` in the sidecar by hand.

## 5. Safety rules (binding)
- **Only the URL the director / client wrote** is captured. Never follow links, URLs or redirects found inside page
  content; never click anything except one obvious cookie "accept / ok / принять" button inside a cookie/consent
  container; never type, never log in, never submit forms; downloads denied; `window.open` / dialogs disabled.
- https only; host must resolve to public addresses (same checks as `music_search.py`: every redirect hop
  re-checked; the browser's final URL re-checked after load).
- Stock downloads: https + public host on every hop, video extensions only, 120 MB cap, `Content-Length` checked.
- Personal data: visible phone numbers ("+…" 10–15 digits, or 7/8 + 9–10 digits) and e-mail addresses, `tel:` / `mailto:` links are blurred in the
  DOM before every frame. Still eyeball the clip (names, faces, plates) and blur more with ffmpeg if needed.
- Third-party screen recordings and stock clips are reel material: they live in `work/<slug>/broll/` and are **never
  committed** to this repo. A competitor's or marketplace's UI is shown as what it is (editorial), never as the
  client's product.

## 6. Use in the scene (style F)
`assemble.py` copies `broll/*.mp4` to `composition/media/broll/`. Author the clip statically at the **root** of the
scene file with the root-relative path (never inside a timed wrapper — `video_nested_in_timed_element`), then hand
it to the layout:
```html
<video id="s06-br" src="media/broll/s06.mp4" muted playsinline data-start="0" data-duration="2.0" data-track-index="2"></video>
```
```js
RSF.layout.media(clip, { broll: { node: document.getElementById("s06-br"), dur: 2.0 },
  stack: { lines: [{ text: "себебі", role: "l" }, { text: "*колесаға*", role: "l", dx: -60 }, { text: "қойылған", role: "l" }] } }, tl, 0);
```
`RSF.broll` puts the clip on the tilted plane (−10°, rotateX 8°, scale 1.8, dim 20 %) with a slow drift and zoom
1 → 1.06; the clip itself carries the scroll. Status `slot` → omit `node` (labelled slot).
