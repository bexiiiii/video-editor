# ElevenLabs connector (MCP) — use it when connected, after asking

Some hosts (Claude desktop/web, Claude Code, Codex) can have the **ElevenLabs connector** attached. Its tools show up in the agent's own tool list with a host-specific prefix, e.g. `mcp__<id>__creative_generate_speech`. Scripts can't see these tools; only the agent can call them. That is why the **orchestrator** makes connector calls itself. Workers with a restricted tool list can't.

## 1. Detect (step 0)
The connector is available if your tool list contains tools ending in `creative_generate_speech`, `creative_transcribe_audio`, `creative_list_voices` (speech/ASR) and optionally `creative_generate_image`, `creative_design_voice`, `creative_get_flow_run_status`. Search deferred tools for "creative speech transcribe" if needed. More than one instance may be listed; use one consistently.

## 2. Ask before using (mandatory)
Every connector call spends the client's ElevenLabs credits. Before the first call in a reel, ask once, in the client's language, listing exactly what would run there:
```
Подключён ElevenLabs. Использовать его для этого ролика?
• озвучка (eleven_v4, язык uz) — ~45 сек
• распознавание речи с таймингом слов
• 3D-объекты (6 шт., gpt-image-2 + удаление фона)
Это тратит кредиты вашего аккаунта ElevenLabs. Без него — бесплатные запасные варианты (edge-tts, локальный Whisper, Codex/OpenAI картинки), качество ниже.
```
- Get the price first: call the generation tools with `estimate_only: true` and show the total credits in that message.
- The answer can be "да", "нет" or partial ("только озвучку"). Record it in `brief.json → providers.elevenlabs_connector = {"allowed": true, "scope": ["tts","asr","images"]}` and in `env.json → used`.
- Approval covers this reel only. Ask again for re-generations beyond the plan (e.g. redoing all images).
- Without approval, use the provider chain from `providers.md` and never call a connector tool.

## 3. How to use each capability
General rules:
- Pass `generations_count: 1` (tools default to 2–4 takes, which multiplies cost).
- Create **one flow per reel** with `creative_create_flow` and pass its `flow_id` to every call.
- Never re-call a generation to retry, because it charges again. Poll `creative_get_flow_run_status(flow_id, session_ids)` until `all_completed` or `has_failures`.
- Download result files from the returned URLs into the work dir with `curl -L -o`.

| Capability | Connector call | Then |
|---|---|---|
| Voice list | `creative_list_voices(languages:["ru"|"uz"|"kk"], use_cases:["social_media","informative_educational"], gender?)` | Pick one natural voice and record `voice_id` in `brief.voice`. For uz/kk, if no native voices are listed, use a multilingual high-quality voice and say so. |
| TTS (faceless) | `creative_generate_speech(prompt=<script text, can include v4 tags like [pause]>, model_id:"eleven_v4"` (or `eleven_v3`), `voice_id, generations_count:1, flow_id)` | Download to `audio/voice_src.mp3`, convert to `audio/voice.wav` (48 kHz mono). Get timings by transcribing that audio (next row), or run `asr.py --text input/script.txt` locally. |
| ASR + word timings | upload: `creative_upload_flow_reference` (audio file) → `creative_transcribe_audio(connect_from:[node_id], model_id:"eleven_scribe_v1", flow_id)` | The status result has `transcripts[].words` (start/end seconds) and `words_download_url`. Save the JSON as `audio/connector_words.json`, then run `$SKILL/scripts/run connector_words.py audio/connector_words.json --lang <lang> --out audio/transcript.json` to get the contract format (sentences, pauses). Language is still validated against `brief.lang`. |
| Voice clone / custom voice | `creative_design_voice` → `creative_get_voice_design_previews` → `creative_save_designed_voice` | Only if the client chose a clone or custom voice. A real clone from the client's sample needs their explicit consent that it is their own voice. |
| Images (3D hero objects, icons) | `creative_generate_image(prompt=<art-direction preset + object>, model_id:"gpt-image-2"` (or `"bytedance-seedream-5-pro"` for photoreal products), `generations_count:1, flow_id)`, then `creative_generate_image(model_id:"birefnet-v2-bg-removal", connect_from:[image_node])` for a transparent cut-out | Download to `assets/img/<asset_id>.png`, then check edges with `image.py --cutout` only if a halo remains. Keep the same art-direction words across the whole reel. |
| Music / SFX | not exposed by this connector (check `creative_get_flow_node_types` once) | Use `providers/music.py` / the bundled SFX kit. |

## 4. Report
List connector usage in the delivery message: what ran on ElevenLabs, credits used (from the estimates), and anything that fell back.
