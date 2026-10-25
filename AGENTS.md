# AGENTS.md — working on the reels-studio repo

- Skills live in `skills/` (Agent Skills standard: `SKILL.md` frontmatter = `name` + `description` only, so the same folders load in Codex and Claude Code). Keep each SKILL.md < 500 lines; push detail into `references/`.
- Worker roster: edit `tools/agents.yaml`, then run `python3 tools/gen_agents.py` — never hand-edit `agents/*.md` or `codex/agents/*.toml`.
- Data contracts between agents: `skills/reels-studio/references/contracts.md`. Change contracts there first, then update scripts and skills.
- Compositions must be deterministic (no `Date`, no `Math.random` → `RS.rand(seed)`), seek-safe, and lint-clean with `npx -y hyperframes@0.8.154 lint`.
- Never commit `.env`, `work/` or renders. Never log API keys.
- Test without paid keys first (edge-tts, faster-whisper small, procedural music). Ask before spending on paid providers.
