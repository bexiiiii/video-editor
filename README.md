# reels-studio

Multi-agent production of vertical reels (Instagram Reels / TikTok / Shorts, 1080×1920) for **Claude Code** and **OpenAI Codex** from one source tree.

- **Inputs:** self-shot talking-head footage, or a script with AI voiceover (stock voice, or the client's cloned voice).
- **Styles:**
  - **A "3D Keyword"**: faceless 3D motion, keyword headlines, voice only.
  - **B "iOS Keynote"**: Apple-UI motion, literal word-synced text, soft music bed and UI clicks.
  - **C "Keynote 3D"**: hybrid. Chapters alternate a cinematic 3D scene in the A look with an iOS UI scene in the B look, held together by B's chrome.
  - A and B were reverse-engineered frame by frame from reference reels (`skills/reels-studio/references/teardowns/`). C is built on top of both.
- **Layouts:** 10 layout types (`references/layouts.md`) with enforced spacing and variety rules: no layout twice in a row, no component reused within 3 scenes, no drawn people, no emoji or placeholder heroes.
- **Modes:** faceless · talking-head hook/CTA + motion body · talking head with overlays.
- **Languages:** Russian, Uzbek, Kazakh. Speech recognition always runs with the language forced.
- **Output:**
  - captions or keywords synced to each word;
  - generated images;
  - sound design and music per style;
  - a loudness-mastered master at −14 LUFS / −1 dBTP;
  - an automatic QA report.

## How it works
```
brief ─► voice & timing ─► director plan ─► ┌ art ×N        (images)      ┐ ─► assemble ─► render ─► QA ─► fix ×≤2 ─► deliver
          (editor | tts)    (scenes.json)   ├ scene-builder ×N (motion)  ┤
                                            └ sound          (music/mix) ┘
```
The orchestrator skill `reels-studio` produces the brief, the plan and the final cut. Workers run in parallel and talk through files in `work/<slug>/` (`skills/reels-studio/references/contracts.md`). Because the workers only exchange files, the pipeline behaves the same in Claude Code (Agent tool subagents) and in Codex (`spawn_agent` subagents or `codex exec` fan-out).

## Install
```bash
git clone https://github.com/bexiiiii/video-editor && cd video-editor
./install.sh --deps        # skills + agents for both hosts, Python deps in ~/.reels-studio/venv
```
- Claude Code: either run the command above, or add it as a plugin marketplace: `claude plugin marketplace add bexiiiii/video-editor` then `claude plugin install reels-studio@reels-studio`. You can also copy `.claude/settings.example.json` permissions into your project.
- Codex: merge `codex/config.example.toml` into `~/.codex/config.toml`. Network access is required for the renderer and the provider APIs.

Requirements: ffmpeg, Node ≥ 20 (renderer `hyperframes@0.8.154` via npx), Python ≥ 3.10.

## Providers (all optional, graceful fallback)
| | best | fallback chain |
|---|---|---|
| TTS | ElevenLabs v3/v4 (ru/uz/kk) | Gemini TTS → Yandex SpeechKit → Azure → edge-tts (free) |
| Speech-to-text | ElevenLabs Scribe v2 | OpenAI whisper-1 → local faster-whisper large-v3 |
| Images | Codex built-in image generation / OpenAI gpt-image-2 | Gemini → Fluent Emoji 3D |
| Music | ElevenLabs Music | Lyria → local procedural generator |
| SFX | bundled CC0 kit | ElevenLabs Sound Effects |
| Cleanup | DeepFilterNet 3 | ffmpeg filter chain / ElevenLabs Voice Isolator |

Copy `.env.example` → `.env` and fill any subset of the keys. With no keys at all, everything except voice cloning still works (lower TTS quality).

## Use
In Claude Code or Codex, inside any folder:
> сделай рилс в стиле B на узбекском из `input/take1.mov`, режим hook_cta, CTA — подписка

The orchestrator asks for anything missing: clone vs stock voice for faceless reels, and the name, Instagram handle and avatar shown in the final CTA. It then shows the scene plan and delivers `work/<slug>/renders/final.mp4`.

## Repo layout
```
skills/reels-studio/   orchestrator: SKILL.md, references/, scripts/, assets/{shared,style-a,style-b,style-c,sfx}, examples/
skills/reels-{scene,art,sound,editor,qa}/   worker skills
tools/agents.yaml      worker roster → agents/*.md (Claude) + codex/agents/*.toml (Codex) via tools/gen_agents.py
.claude-plugin/        Claude Code plugin + marketplace manifests
install.sh             symlink installer for both hosts
```
