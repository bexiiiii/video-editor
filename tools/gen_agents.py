#!/usr/bin/env python3
"""Render tools/agents.yaml into Claude Code agent files and Codex agent roles.

Tiny YAML subset parser (list of flat mappings) so the repo has no dependencies.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_roster(path: pathlib.Path) -> list[dict]:
    agents, cur = [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip() or line.strip() == "agents:":
            continue
        m = re.match(r"\s*-\s+(\w+):\s*(.*)", line) or re.match(r"\s+(\w+):\s*(.*)", line)
        if not m:
            raise ValueError(f"cannot parse line: {raw!r}")
        if line.lstrip().startswith("- "):
            cur = {}
            agents.append(cur)
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        cur[key] = val
    return agents


def body(a: dict) -> str:
    return (
        f"You are the **{a['name']}** worker of the reels-studio pipeline.\n\n"
        f"1. Load and follow the `{a['skill']}` skill (sibling of the `reels-studio` skill).\n"
        "2. Work only from the brief path the orchestrator gives you; read `reels-studio/references/contracts.md` first.\n"
        "3. Write only inside your assigned output folder and finish with the result JSON the skill specifies.\n"
        "4. Never print API keys. Report failures in the result JSON instead of guessing.\n"
    )


def main() -> None:
    roster = load_roster(ROOT / "tools" / "agents.yaml")
    claude_dir, codex_dir = ROOT / "agents", ROOT / "codex" / "agents"
    claude_dir.mkdir(exist_ok=True)
    codex_dir.mkdir(parents=True, exist_ok=True)
    for a in roster:
        (claude_dir / f"{a['name']}.md").write_text(
            "---\n"
            f"name: {a['name']}\n"
            f"description: {a['description']}\n"
            f"tools: {', '.join(a['tools'])}\n"
            f"model: {a['model']}\n"
            "---\n\n" + body(a), encoding="utf-8")
        instr = body(a).replace('"""', "'''")
        (codex_dir / f"{a['name']}.toml").write_text(
            f'name = "{a["name"]}"\n'
            f'description = "{a["description"]}"\n'
            f'developer_instructions = """\n{instr}"""\n', encoding="utf-8")
    print(f"rendered {len(roster)} agents → agents/*.md, codex/agents/*.toml")


if __name__ == "__main__":
    main()
