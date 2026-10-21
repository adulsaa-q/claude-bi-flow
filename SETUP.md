# SETUP.md - runbook for the AI (Claude Code)

You were told to set up the BI + AI flow from this repo. Follow these steps in order. Do not skip verification. Do not install anything outside the user scope (no admin rights are available). Report to the user in their own language.

## 0. What this repo installs

- `skills/` -> `~/.claude/skills/` (9 skills: handoff, data-code-review, data-debug-troubleshoot, data-profiling, sql-server-tuning-bi, data-warehouse-kimball, power-bi-design-advanced, power-bi-svg-design, project-init)
- 13 `power-bi-*` skills from `pbi-cli` (`pbi-cli skills install`)
- `global/CLAUDE.team.md` -> a marked block inside `~/.claude/CLAUDE.md` (skill routing + working rules)
- plugins listed in `plugins.txt`

It does NOT touch any project. New projects are scaffolded later by the `project-init` skill.

## 1. Check prerequisites

Run `git --version`, `python --version` (need 3.11+), `claude --version`, `uv --version` (or `pipx --version`).
If something is missing, tell the user what and how to install it in user scope (uv: https://docs.astral.sh/uv/ ; Python: python.org installer with "Install for me only"; git: https://git-scm.com). Wait for the user. Do not use winget machine scope or anything needing admin.

## 2. Dry run, then install

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun
```
Read the output. If a line says `WARN ... exists and differs`, the user already has their own version of that skill: show them and ask whether to keep it (default) or run with `-Force` (a backup is made first). Then:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

## 3. Verify (mandatory)

Open a NEW terminal (PATH changes), then:
```powershell
powershell -ExecutionPolicy Bypass -File .\doctor.ps1
```
`PASS` = ok, `OPT` = optional tool missing (fine), `FAIL` = fix it. Re-run until no FAIL. Report the real output to the user; do not say "done" unless doctor ends with "All required checks passed."

## 4. Optional tools (only if the user's work needs them; ask first)

| Tool | Needed for | Notes |
|---|---|---|
| Power BI Desktop | live model work via `pbi` | usually already installed |
| Tabular Editor 2 | offline BPA lint (`project-init` `scripts/lint_pbip.ps1`) | portable zip, unzip to `%LOCALAPPDATA%\Programs\TabularEditor2`, plus `BPARules-Microsoft.json` beside it |
| fab-inspector | PBIR rules lint | also used by `lint_pbip.ps1`; ask the user where the team gets it |
| `sqlcmd` | SQL Server work | comes with SQL Server client tools |
| DAX Studio (`dscmd`) | DAX performance | portable |
| `duckdb`, `gh`, `ruff`, `gitleaks` | exploration, GitHub, lint, secret scan | `winget install --scope user` where available |
| Excel / Word / PowerPoint skills | create .xlsx / .docx / .pptx | NOT shipped here (Anthropic-licensed). Ask the user to get `xlsx`, `docx`, `pptx` from https://github.com/anthropics/skills and copy into `~/.claude/skills/` |

## 5. First use

Tell the user to restart Claude Code, then try: "start a new BI project here" (triggers `project-init`) or open an existing PBIP project and ask a DAX question (triggers `power-bi-dax`, needs `pbi connect` with Desktop open).

## Troubleshooting

- `pbi: command not found` right after install: open a new terminal; or `uv tool update-shell`.
- Skill not showing in Claude Code: restart the app; check `~/.claude/skills/<name>/SKILL.md` exists.
- `claude plugin install` fails: the plugin is optional; continue and tell the user which one failed.
- Never edit files between the `claude-bi-flow:begin/end` markers in `~/.claude/CLAUDE.md` by hand; re-run `install.ps1` to refresh them.
