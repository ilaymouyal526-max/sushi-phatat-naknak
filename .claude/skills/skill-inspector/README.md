# skill-inspector (NVIDIA SkillSpector)

`SKILL.md` and `LICENSE` here are copied unchanged from
[NVIDIA/skillspector](https://github.com/NVIDIA/skillspector) at commit
`62c2fe8622f580ac292d4078c3b71f790194dbbd` (SkillSpector v2.12.0), under the
Apache 2.0 license.

The skill needs the `skillspector` CLI. Install it pinned to the same commit:

```bash
uv tool install git+https://github.com/NVIDIA/skillspector.git@62c2fe8622f580ac292d4078c3b71f790194dbbd
```

Static scans (`--no-llm`) are free and run locally. LLM analysis calls a paid
provider, so per `CLAUDE.md` it needs explicit approval with the cost shown first.

```bash
skillspector scan ./path/to/skill --no-llm
skillspector scan ./skills-folder --recursive --max-skills 100 --no-llm --format json --output report.json
```

The audit of all installed skills is in `security/skill-audit-2026-11-05.md`.
