# Style previews

Show these images to the client **before** starting a reel and ask which style to use. Each strip holds 4 frames from the rendered demo of that style (`assets/style-*/demo/*.mp4`).

| File | Style | One-liner | Best for |
|---|---|---|---|
| `style-a.jpg` | A "3D Keyword" | Dark/light backgrounds, big glossy 3D objects, 2–4 keyword headlines, voice only | faceless tech/AI explainers, tutorials |
| `style-b.jpg` | B "iOS Keynote" | Apple-like UI: kicker + bold headline, iOS cards, players, counters, light/dark/blue themes | personal brand, marketing, step-by-step tips |
| `style-c.jpg` | C "Keynote 3D" | A × B hybrid: cinematic 3D scenes alternate with iOS UI scenes under one chrome | product/app promos, mixed content |
| `style-d.jpg` | D "3D Keyword Talking Head" | Style A over the client's footage: keyword headlines above/below the face, 3D objects beside the speaker, full-screen A inserts | expert talking-head reels (needs footage) |
| `style-e.jpg` | E "Data News" | White editorial news page: channel header + chapter tabs, gold-accent headlines, news cover / post / data cards with count-ups and bars, uppercase literal captions | news, statistics, education/HR data explainers |

Regenerate after a demo changes: extract 4 settled frames (text fully revealed, not mid-transition) at 360 px width and `hstack` them, as in `scripts/make_previews.sh`.
The 4 instants used for each strip are in `timestamps.json` (reuse them when regenerating).

**Branded previews:** when the client has brand colours/font, `scripts/make_brand_previews.sh work/<slug> [a b c d e]` renders the same 4 instants of each demo with the client's brand layer into `work/<slug>/previews/style-<x>.jpg` (these files stay untouched) — see `references/branding.md`.
