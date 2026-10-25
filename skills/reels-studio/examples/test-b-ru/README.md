# Example: test-b-ru

End-to-end run of the pipeline: style B, faceless, Russian, 15 s, no paid APIs.
Voice from edge-tts, music generated locally, 4 scenes built by 4 parallel scene-builder agents.
Automatic QA passed (−14 LUFS, word sync, no gaps).

To reproduce: copy this folder to `work/test-b-ru/`, then run `tts.py` → `music.py` → `mix.py` → `assemble.py` → `render.py` → `qa.py`.
