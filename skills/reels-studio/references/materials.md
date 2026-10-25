# Materials request — ask the client for real assets

Real material beats generated illustration (layouts.md §4). After the plan is drafted, the director lists every asset the client must provide in `plan/materials.json` and asks for them **in one message** before fan-out.

## When to request
| Plan contains | Request |
|---|---|
| a scene about the client's app/site/product UI | **screenshots** (PNG, phone 1179×2556 or desktop 2880×1800, light theme unless stated) or a **screen recording** (MP4, 5–15 s, 60 fps if possible, no notifications, tap the exact flow) |
| a tutorial step ("open settings → …") | one screenshot **per step**, or one screen recording of the whole flow |
| a spoken result / metric / proof ("+300 заявок", "12 400 подписчиков") | screenshot of the real dashboard / stats (numbers must be real — never invented); allow blurring of private data |
| a brand, partner, app or tool name | official **logo** (SVG/PNG with transparency) — or permission to use the public logo |
| the client's product / place / team | **photos** or 5–10 s **B-roll** clips (vertical 9:16, good light) |
| style D or modes `hook_cta` / `head_overlay` | **talking-head footage** (see modes.md: 9:16, face in upper third, clean audio, pauses between thoughts, hook first) |
| CTA with avatar | **avatar** photo (square, ≥ 600 px) — or the brand logo |
| client voice clone (faceless) | **30–60 s clean voice sample**, no music, one speaker |

## Message format to the client (short, numbered, with specs)
```
Чтобы ролик выглядел реально, пришлите, пожалуйста:
1. Скриншот экрана «Табель» в приложении (телефон, светлая тема) — сцена s04.
2. Запись экрана: нажатие «Начать день» → селфи → «Отмечено», 8–10 сек — сцена s03.
3. Логотип Link HR (PNG без фона или SVG) — финал.
Можно прислать не всё — недостающее заменю графикой и напишу, где именно.
```
Language of the message = language the client writes in. Ask only for what the plan really uses; ≤ 6 items; mark each item *обязательно* / *желательно*.

## plan/materials.json
```json
{"requested_at": "…", "items": [
  {"id": "m1", "scene": "s04", "kind": "screenshot|screen_recording|logo|photo|broll|footage|avatar|voice_sample|stats",
   "what": "Screen «Табель», phone, light theme", "spec": "PNG 1179×2556", "required": true,
   "status": "requested|received|missing", "path": "input/m1_tabel.png|null",
   "fallback": "RSB.calendar mock with neutral data"}]}
```

## After the client answers
- Save files to `input/` with the item id prefix; set `status`. Check them: resolution, aspect, no private data visible (offer blur), recording length.
- Screen recordings: trim to the needed part (`ffmpeg -ss … -t …`), scale to fit the phone/screenshot frame, keep 30 fps.
- Missing **required** item → remind once; if still missing, use the `fallback`, and list it in the final report ("s04: макет вместо реального скриншота").
- Never fabricate real-looking metrics, reviews or a real company's UI as genuine.
