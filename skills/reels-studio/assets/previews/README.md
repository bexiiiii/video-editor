# Style previews

Show these images to the client **before** starting a reel and ask which style to use. Each strip holds 4 frames from the rendered demo of that style (`assets/style-*/demo/*.mp4`).

| File | Style | One-liner | Best for |
|---|---|---|---|
| `style-a.jpg` | A "3D Keyword" | Dark/light backgrounds, big glossy 3D objects, 2–4 keyword headlines, voice only | faceless tech/AI explainers, tutorials |
| `style-b.jpg` | B "iOS Keynote" | Apple-like UI: kicker + bold headline, iOS cards, players, counters, light/dark/blue themes | personal brand, marketing, step-by-step tips |
| `style-c.jpg` | C "Keynote 3D" | A × B hybrid: cinematic 3D scenes alternate with iOS UI scenes under one chrome | product/app promos, mixed content |
| `style-d.jpg` | D "Talking Head Editorial" | Speaker on camera, karaoke captions, chest-band widgets, paper/dark editorial inserts, iPhone proof | expert talking-head reels (needs footage) |

Regenerate after a demo changes: extract 4 settled frames (text fully revealed, not mid-transition) at 360 px width and `hstack` them, as in `scripts/make_previews.sh`.
