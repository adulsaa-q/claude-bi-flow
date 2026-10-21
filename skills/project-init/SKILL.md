---
name: project-init
description: Bootstrap ANY new project (Power BI dashboard, ETL pipeline, SQL analysis, ad-hoc report, or anything else the user starts under your projects folder) with the user's proven long-running-project structure — distilled from the an earlier BI project's months of evolution, including the 2026-09-17 flow audit (hooks, path-scoped rules, offline lint, Desktop toolkit). This is the user's general project-scaffolding habit, not a BI-only tool — the BI-specific pieces (Desktop toolkit, lint_pbip.ps1) are just one branch selected in Step 0 based on the deliverable. ALWAYS trigger when the user starts a new project of any kind, says "เริ่มโปรเจกต์ใหม่", "setup โปรเจกต์", "โปรเจกต์ตัวใหม่", "วางโครงสร้าง project", creates a new folder under your projects folder, or asks how to structure a project that will run for weeks or months.
---

# Project Init — วางโครงสร้างวันแรกให้เหมือนโปรเจกต์ที่รอดมาแล้วหลายเดือน

Use the project's scope to choose the needed pieces. These templates were hardened against observed Git, SQL, Desktop and pipeline failures on 2026-09-22; they are not proof that a new machine or project is ready.

**Ready-made files live in `templates/` next to this SKILL.md** — copy them, don't retype them. They include tested generic guards. Copy only the toolkit needed by the deliverable; never transplant that project financial expectations or database queries into another project.

## Step 0 — Ask three questions first

1. **Deliverable**: dashboard (.pbip), ETL pipeline, ad-hoc analysis, or report?
2. **Data sources**: SQL Server (which server/db)? Files (Excel/CSV)? APIs?
3. **Lifespan**: weeks-to-months (full structure) or one-off (skip agents/MCP/hooks, keep git+.env+AGENTS.md only)?

## Step 1 — Scaffold

All AI-facing files below are written in **English** (token efficiency — the user reads chat, not config files). user-facing deliverables stay Thai.

```
<projects>\<ProjectName>\
├── AGENTS.md            ← the project's brain, tool-independent — rules, context, reference values. TARGET < 200 lines
├── CLAUDE.md            ← FIRST LINE MUST BE `@AGENTS.md` (Claude Code does NOT read AGENTS.md by itself) + thin Claude-only addendum
├── PROJECT_MAP.md       ← who reads what / where new files go / automation inventory (update whenever a folder or hook is added)
├── HANDOFF.md           ← latest session brief (the handoff skill overwrites it; previous copies -> .handoff-archive/)
├── .env.example         ← all key names, placeholder values — safe to commit
├── .env                 ← real values — NEVER commit (gitignored from the first commit!)
├── .gitignore           ← templates/gitignore
├── .mcp.json            ← only when there's a SQL Server source (Step 3)
├── .claude/
│   ├── settings.json    ← templates/.claude/settings.json (4 hooks wired, minimal allow-list — strip the 2 BI-only hook entries for non-BI deliverables, see Step 2b)
│   ├── hooks/           ← templates/.claude/hooks/*.py (Step 2b)
│   ├── rules/           ← templates/.claude/rules/*.md skeletons — path-scoped, fill as gotchas appear (Step 2c)
│   ├── agents/          ← empty at first — create a reviewer subagent once gotchas reach ~10 (give it `memory: project`)
│   └── skills/          ← empty at first — create a verify-* skill once reference values exist
├── knowledge/           ← PENDING_DECISIONS.md from day 1; GOTCHAS.md + GOTCHA_INDEX.md appear at graduation (Step 2c)
├── deliverables/        ← files sent to people outside the team (dated in the filename)
├── docs/                ← generated docs, FINDINGS_YYYY-MM-DD.md (old rounds -> archive/docs/)
├── reference/           ← immutable sources of truth: audit files, specs, reference numbers
├── metadata/            ← related SQL views / ETL source definitions (snapshots — date them, re-dump before trusting)
├── scripts/
│   ├── git-hooks/       ← templates/scripts/git-hooks/ (pre-commit: .env + BOM guard, one git grep, seconds on 2,000 files)
│   ├── desktop/         ← templates/scripts/desktop/ — BI only: Power BI Desktop self-verification via UI Automation (Step 2d)
│   ├── lint_pbip.ps1    ← templates/scripts/lint_pbip.ps1 — BI only: offline model BPA + report lint (Step 2e)
│   └── agent_scenarios.py ← templates/scripts/agent_scenarios.py — headless-session behavioral tests, add once hooks/scripts exist (Step 2f)
├── planning/            ← plans, audits (finished -> planning/done/)
└── archive/             ← docs/, planning/, scripts_oneoff/<date_topic>/, backups/ — not read unless asked
```

No `DEV_LOG.md`. that project kept one for 2.5 months of silence: `.remember/today-*.md` (per turn, plugin-rotated) + `.handoff-archive/<date>.md` (per session) already record the diary twice. Don't add a third.

Run `git init`, then `sh scripts/git-hooks/install.sh` before the first commit or real credentials. The installer supports linked worktrees. The guard checks staged blobs, including renames and every report JSON. Run `python scripts/test_workflow_guards.py` (disposable fixtures only) and `python .claude/hooks/test_guard_desktop_open.py` before the scaffold commit.

## Step 2 — AGENTS.md + CLAUDE.md (the compounding asset)

**AGENTS.md is the primary, tool-independent file** — any AI agent reads it first. Since Claude Code v2.1.277 (2026-09-18), Claude Code reads a project's `AGENTS.md` natively when there's no `CLAUDE.md`/`CLAUDE.local.md` in scope — so the **one-off path (Step 0: git+.env+AGENTS.md only)** now loads for free, no import needed. For the full-structure path, keep **CLAUDE.md starting with `@AGENTS.md`** anyway: the official guidance is to leave that import in place whenever CLAUDE.md holds other content (hooks/rules/subagents in Step 2's addendum) — it never causes AGENTS.md to load twice, and it keeps things working in sessions where native AGENTS.md support is unavailable (pre-v2.1.277, Bedrock, telemetry disabled). Keep AGENTS.md under ~200 lines — everything that only matters when touching a specific file type goes into a path-scoped rule (Step 2c), not here.

```markdown
# AGENTS.md - Developer Guide (AI Context)
Last Updated: <date>
> Repo map: `PROJECT_MAP.md` — read before creating any new file
> Claude-specific addendum: `CLAUDE.md`

## Project Context
* Deliverable / Active file (one selected artifact — .pbip, main pipeline script, notebook, etc.; archive retired versions only with the user's approval; local git is not an off-machine backup):
* Data sources:
* Scope & status (page numbers — re-check after any nav renumber):
* Work Style:

## Design Guidelines (Must Follow)
1.

## Critical Gotchas (Do Not Revert)
<!-- Numbered, dated, English. Inline until ~15 entries, then graduate (Step 2c). -->
1.

## Reference Check Values
<!-- Audited/confirmed numbers — the raw material for a verify-* skill later -->

## Key Commands
<!-- Only commands that exist. Re-verify every path here at each handoff — that project carried dead RDQ/sql_query.ps1 commands for a month. -->
```

```markdown
@AGENTS.md

# CLAUDE.md — <ProjectName> (Claude-specific addendum)
Last Updated: <date>
> `AGENTS.md` is imported above so it loads every session. This file only holds Claude Code mechanics: hooks, rules, subagents, skills.

## Hooks (`.claude/hooks/`, wired in settings.json)
- Universal: block_env_access.py · stop_uncommitted_nudge.py
- BI only (Power BI Desktop/PBIR present): guard_desktop_open.py · check_visual_json_bom.py
- see PROJECT_MAP §4
## Rules (`.claude/rules/`) — path-scoped, load themselves
## Subagents / Skills — none yet
```

Rule to state to the user (in their language) at the end of init: **"เจอของแปลกเมื่อไหร่ จดเข้า gotcha ทันที"**.

### Step 2b — Hooks (copy `templates/.claude/hooks/`, wired by `templates/.claude/settings.json`)

`block_env_access.py` and `stop_uncommitted_nudge.py` apply to any project. `guard_desktop_open.py` and `check_visual_json_bom.py` only matter when the deliverable is a Power BI dashboard (.pbip) — for ETL/SQL/report-only projects, delete their `PreToolUse`/`PostToolUse` entries (and the `PowerShell(Get-Process -Name PBIDesktop,msmdsrv ...)` allow-list line) from `settings.json` after copying it, rather than leaving them wired to run against files that will never exist.

| Hook | Event | Guards against (observed incidents) |
|---|---|---|
| `block_env_access.py` | PreToolUse Read/Edit/Write | `.env` with live DW creds read into context or clobbered |
| `guard_desktop_open.py` | PreToolUse Edit/Write/Bash/PowerShell | on-disk `.tmdl` / report JSON edits while Power BI Desktop runs — Desktop's next save silently reverts them (recurred 5+ times); denies direct edits, asks before scripts, treats failed process detection as unknown; live API calls exempt but export-tmdl is not |
| `check_visual_json_bom.py` | PostToolUse Edit/Write/**Bash/PowerShell** | UTF-8 BOM in PBIR JSON (Desktop rejects the file). Must cover Bash/PowerShell — batch scripts write most report JSON and an Edit-only matcher never saw them |
| `stop_uncommitted_nudge.py` | Stop | TMDL/report edits left uncommitted for hours (1 nudge/h, never blocks) |

Hooks recognize model/report paths; they are conservative guards, not a shell sandbox. They apply only in clients that load this hook configuration. Process detection failure must not silently permit edits. Don't add a 5th hook until a failure has repeated and a gotcha documents it.

`check_visual_json_bom.py` (PostToolUse) structurally can't block anything — PostToolUse fires after the action already happened — so it's wired with `asyncRewake: true` in `templates/.claude/settings.json`: it runs in the background and only interrupts Claude when it exits 2 (a real BOM found), which is the only case it ever needs to speak up. `stop_uncommitted_nudge.py` stays synchronous even though it also never blocks: it talks to Claude via an exit-0 `{"systemMessage": ...}` on stdout, and Claude Code only surfaces an async hook's output to Claude on exit 2 — making it async would silently swallow every nudge. `block_env_access.py` and `guard_desktop_open.py` stay synchronous since they genuinely deny actions.

### Step 2c — Gotcha graduation + path-scoped rules

AGENTS.md is read in full every session. Gotchas that only matter when touching DAX are a token tax on every other task. **When gotchas cross ~15 entries:**
1. `knowledge/GOTCHAS.md` — every entry **verbatim** (the "how it was found" detail is the value).
2. `knowledge/GOTCHA_INDEX.md` — one line per entry (number + short title). AGENTS.md keeps a 2-line pointer, not the index (that project's index alone was 144 lines).
3. **`.claude/rules/*.md` with `paths:` frontmatter** (skeletons in `templates/.claude/rules/`): distil the gotchas for each file type — `dax-measures.md` (`**/*.tmdl`), `report-layer.md` (`**/*.Report/**/*.json`), `dw-views.md` (`metadata/**`). Claude Code loads a rule only when it reads a matching file, so it can be long and specific at zero cost to unrelated sessions. Reviewer subagents point at the rule, not at the 200 KB GOTCHAS.md.
4. Numbers never change. Grep `.claude/agents/`, `.claude/skills/`, `.claude/rules/` for `#N` references after any move. Diff the moved text line-for-line before deleting.
5. **Never leave new gotchas written out in full in the index file "for now"** — that project accumulated 22 such entries in AGENTS.md before anyone noticed.

### Step 2d — Desktop self-verification toolkit (`templates/scripts/desktop/`)

Power BI Desktop can be driven by UI Automation without a human: `pbi_goto.ps1` (select a page tab + screenshot), `sweep.ps1` (every page, for rendered QA after any model-wide change), `pbi_ctrlclick.ps1` (test a button/bookmark), `pbi_close_nosave.ps1` (graceful close that clicks "Don't save" — never `taskkill`, it resurrects stale AutoRecovery state), `pbi_screenshot.ps1`, `run_dax.py` (pbi-cli DAX → clean table). **These existed in a past project for weeks only inside a session scratchpad and would have been auto-deleted** — anything reusable built during a session goes into `scripts/` before the session ends (the handoff skill now checks).

### Step 2e — Offline lint (`templates/scripts/lint_pbip.ps1`)

Tabular Editor 2 `-A` (Microsoft's 71 BPA rules, offline on the TMDL folder, no Desktop) + fab-inspector (PBIR rules). One-time machine setup: TE2 in `%LOCALAPPDATA%\Programs\TabularEditor2` with `BPARules-Microsoft.json` beside it; fab-inspector release zip in `%LOCALAPPDATA%\Programs\fab-inspector` with `Base-rules.json` — both already on the user's machine. Signal rows = DAX Expressions / Error Prevention. After the first run is reviewed, record them with `-UpdateBaseline` (writes `scripts/lint-rules/signal-baseline.txt`; if the project `.gitignore` ignores `*.txt`, add `!scripts/lint-rules/signal-baseline.txt`). From then on exit = number of NEW signal rows (printed `NEW:`), 255 = engine/rules missing — a known row is "known", not "accepted", so track its owner in the open-items file. First run on a past project found a fact-to-dimension relationship with mismatched data types nobody had seen in 3 months.

### Step 2f — Headless-session behavioral scenarios (`templates/scripts/agent_scenarios.py`)

Hooks and rules only cover what they were written to catch. Once a project has hooks worth trusting (Step 2b) and read-only scripts worth relying on (Steps 2d/3), verify the *behavior* they're supposed to produce, not just their presence: run `claude -p` inside a disposable git worktree with a fake `.env` (a canary secret, never real) and judge the transcript's tool calls and file changes, not its wording. Ship at minimum: `inspect` (a read-only request must not write anything), `docs` (a doc-only edit must touch only that file and never reach a live-data tool), `env` (a request for `.env` values must never leak the canary). Add project-specific scenarios once there's a specific live-verification step worth protecting (that project's `model` scenario: with no Desktop open, "verify the model" must report *not verified*, never claim a pass). Run after material skill/tool/hook/model changes, not on every commit — it costs model usage. Fill in `ALLOWED` and the `docs` judge's live-data markers with the project's actual scripts/MCP tool names before first use; the shipped template is illustrative, not a working list for a project that hasn't scaffolded those scripts yet.

## Step 3 — SQL source and reproducible runtime

Copy `templates/scripts/sql_readonly/` into the project. Create a project-local environment
(`uv venv .mcp-venv`, then `uv pip install --python .mcp-venv/Scripts/python.exe -r scripts/sql_readonly/requirements.txt`).
Ignore `.mcp-venv/`. Use the actual resolved project paths in local `.mcp.json`, never a previous user's home directory:

```json
{
  "mcpServers": {
    "<project>-sql-readonly": {
      "command": "<absolute-project>/.mcp-venv/Scripts/python.exe",
      "args": ["<absolute-project>/scripts/sql_readonly/server.py"],
      "env": {"SQL_ENV_PATH": "<absolute-project>/.env"}
    }
  }
}
```

The server accepts one parsed SELECT/CTE and executes the validated rendering; it rejects writes,
external execution and sequence advancement. This is defense in depth, **not** a replacement for a
dedicated SELECT-only database login. Verify effective permissions with read-only metadata, never a
destructive probe. Do not copy that project's overprivileged login. Certificate validation defaults on for
`SQL_ENV_PATH`; IT must provision the trust chain. Do not silently enable
`SQL_TRUST_SERVER_CERTIFICATE=yes`. `SQL_ODBC_DRIVER` can select the installed driver.

For Python-based project scripts, create `pyproject.toml`, `.python-version` and `uv.lock` with only
the project's actual dependencies; verify `uv sync --locked` in a clean environment. SQL guard tests
need the pinned sqlglot from the packaged requirements. Do not copy that project's entire dependency set.

If a health task is needed, adapt queries to the new schema. Require checked native exit codes,
failure logs, missing-success detection and an explicit business-approved freshness cutoff.
Pass sqlcmd passwords through a scoped child environment, never `-P`. Trigger the task once and
verify both LastTaskResult and a fresh log; installation alone is not verification.

## Step 4 — Register the project

- If the user wants a knowledge-vault entry, ask for its location and update only that approved vault. Do not assume a drive, username, or external governance file.
- **Backup from day 1, even without a remote:** no org git yet → `git bundle create <share>\<project>.bundle --all` on a network/OneDrive path, weekly. A repo that exists only on one laptop is not backed up. When an org remote is granted, it must be a private repo (finance data in `reference/`).
- Tell the user what was deferred and the trigger for each: reviewer subagent at ~10 gotchas (with `memory: project`); verify-* skill at the first confirmed reference numbers; project rule files for lint (`scripts/lint-rules/`) when a lint finding repeats.

## Standing rules learned the hard way

- **(BI dashboards) Identify the active `.pbip` explicitly.** Multiple projects must fail ambiguous auto-selection. Follow PBIP/PBIR artifact references, not matching filename stems. Never delete retired versions without user approval and a verified recovery path.
- **Two Claude sessions on one repo edit structural docs (AGENTS/PROJECT_MAP/GOTCHAS) in turns, or the second one works in a `git worktree`.** Concurrent edits to AGENTS.md happened on 2026-09-17; it worked out by luck.
- **Every automation gets verified, not just installed:** scheduled task → LastTaskResult; hook → feed it a planted failure; skill → run its command once. "Set up" ≠ "runs".
- **Uncommitted / untracked files need an owner and decision.** Do not delete or commit unexplained user files; report them and request disposition.
- **Global vs project:** methods in global skills, facts in the project. Don't put project knowledge in `~/.claude/`.

## What NOT to do on day 1

- Don't create the reviewer subagent or verify skill empty — worthless without accumulated gotchas/reference values.
- Don't skip `git init` "จนกว่าจะมีอะไรให้ commit" — `.gitignore` must exist before the first credential file does.
- Do not change global plugins/output preferences while scaffolding a project.

## Validation and limits

Run Git/SQL guard tests and Desktop-hook tests, both PowerShell screenshot dependency checks,
and lint's missing-tool case. A real lint run may legitimately return findings; a missing engine
must never look clean. UI click/close scripts still depend on Desktop locale, window geometry and
operator-selected context: inspect the target window first, never close a user's project implicitly.
Create a populated executable verify suite only after approved reference values exist. Include
identity checks, missing/BLANK failure cases and explicit numeric tolerances. No empty verify skill.
**Every check needs its own recorded independent source** (audit doc, finance workbook, decision
log, SQL recompute, model snapshot — `source.kind`/`source.ref` per check), never one blanket
provenance sentence covering all checks. Without it, a value the model produced and the value it's
being checked against can look interchangeable — that project ran 41 checks for weeks under one shared
sentence before that gap was caught (2026-09-23); reject any check that doesn't carry a source, and
have the verify runner list the self-confirming ones (no independent source) as a distinct category
rather than passing them silently.
For snapshot-based documentation, compare live structure/config before reuse; `--help` and dry runs
must not generate outputs. PDF conversion failure must fail the pipeline without accepting an old PDF.
Configured agent memory is not evidence that a memory directory has been created or persisted.
