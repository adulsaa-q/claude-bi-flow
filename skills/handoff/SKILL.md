---
name: handoff
description: End-of-session handoff for long-running Power BI / SQL / ETL projects. Reads git diff + conversation context, then updates a tiered memory system (AI_CONTEXT.md, CLAUDE.md, the daily .remember log) and writes HANDOFF.md — a cross-AI morning brief any assistant (Claude, Gemini, Codex, DeepSeek, Qwen, or a future model) can read cold and resume from. Use this whenever the user runs /handoff or says "ปิด session", "สรุป session", "จบงานวันนี้", "wrap up the session", "checkpoint before I stop", or otherwise signals they are done for the day and want progress saved. Do NOT trigger on casual mentions of the word "handoff" (e.g. "hand off this task to the API team", "handoff between threads") when the user is not actually ending a work session.
---

You are running the `/handoff` skill. This is an end-of-session operation for a project that runs for weeks to months.

Your job: synthesize this session into a durable briefing any AI can read cold tomorrow and resume immediately — while keeping the memory footprint **flat**, so per-session context cost does not grow as the project ages. That flatness is the entire reason this skill exists. A handoff that only ever appends will bloat the project to death over a month.

Work through Steps 1–7 in order.

---

## The tier model (read first — it drives every decision)

| Tier | Real files | Loaded when | Growth control |
|---|---|---|---|
| **1 — Permanent** | `AI_CONTEXT.md` (`CRITICAL_RULES`, `AUDIT_ANCHORS`), `AGENTS.md`/`CLAUDE.md` (`Critical Gotchas` — whichever file actually holds that section, see Step 5) | every session | **append-only**; `NEXT_ACTIONS` is the *only* prunable part |
| **2 — Recent** | `.remember/today-YYYY-MM-DD.md` (today's log) | every session | one file per day; the **remember plugin** rotates old days — this skill does not |
| **3 — Cold** | `.remember/*.done.md`, `recent.md`, `archive.md`, `.handoff-archive/` | only when asked | never loaded by default |

When deciding where a fact belongs, ask: **will this still matter in a month?**
- Yes, project-wide → Tier 1 rule (promote it).
- Only matters now → today's daily log (Tier 2).
- Already superseded → leave it; it ages into Tier 3 on its own.

### Append-only vs. rotatable — do not confuse these

- **APPEND-ONLY — never cap, prune, or rewrite:** `AGENTS.md`/`CLAUDE.md` `## Critical Gotchas`, `AI_CONTEXT.md` `## CRITICAL_RULES`, `## AUDIT_ANCHORS`. These are permanent technical constraints and verified numbers. They do not go stale. Capping them is how a project loses hard-won knowledge.
- **ROTATABLE / prune:** `AI_CONTEXT.md` `## NEXT_ACTIONS` (cap ~10, drop done/stale before adding) is the only thing this skill prunes. Daily logs rotate too, but the **remember plugin owns that** — you never move or delete `.remember/` files.

---

## Step 1 — Gather git context (source of truth for what changed)

Trust git over memory for *what files changed*. Capture the branch (needed for the daily-log entry) and a diff stat with a fallback chain so short histories don't error:

```bash
git branch --show-current
git status --short
git log --oneline -10
git diff HEAD~3..HEAD --stat 2>/dev/null || git diff HEAD~1..HEAD --stat 2>/dev/null || git diff --stat
```

PowerShell: the `||` chain works in pwsh 7; use `2>$null` instead of `2>/dev/null` if a step complains.
Not a git repo → skip this step and synthesize from conversation memory alone.

**Step 1b — Salvage and hygiene (added 2026-09-17 — each check is a real loss that project took):**

1. **Scratchpad scripts worth keeping.** List `*.py`/`*.ps1`/`*.dax` in this session's scratchpad dir (`%LOCALAPPDATA%\Temp\claude\<project>\<session>\scratchpad`). Anything reusable (a Desktop-automation script, a QA scan, a query runner) goes into `scripts/<area>/` now with hardcoded paths replaced; genuine one-offs go into `archive/scripts_oneoff/<date_topic>/`. Claude Code deletes the scratchpad on its retention sweep — that project's whole Desktop self-verification toolkit lived only there for weeks and would have vanished.
2. **Untracked / uncommitted leftovers.** Every `??` and ` M` in `git status` older than this session gets a decision in HANDOFF `next`: commit, archive, or delete — with the reason. Never let a file sit undecided across sessions (a past project: 5 sessions).
3. **Dead commands in Key Commands / skills.** `grep` the paths, file names and script names cited in `AGENTS.md` Key Commands and `.claude/skills/*/SKILL.md` prerequisites against the disk. Anything that no longer exists (a retired `.pbip` name, a deleted script) is fixed in this handoff, not noted for later.
4. **Automation still runs?** If the project has a scheduled task or cron, check its last result (`Get-ScheduledTaskInfo -TaskName <name>` → `LastTaskResult` 0) rather than assuming it does.

---

## Step 2 — Synthesize the session, then classify each discovery

Produce these six sections from git output + conversation context:

- **A. Accomplished** — specific file / measure / script names. Not vague.
- **B. Files changed** — from `git status`. Categorize Created / Modified / Deleted.
- **C. Discoveries** — things NOT known at session start: hidden constraints, root causes, surprises. Highest value for the next AI — it knows the codebase, it doesn't know the surprises.
- **D. Current state** — one line per work area. Status DONE / WIP / TODO / BLOCKED + note.
- **E. Next actions** — numbered, specific enough to start without asking. Include the first command / file / decision.
- **F. Key commands** — new commands / patterns / one-liners discovered.

**Then classify each discovery in C — this is the skill's one real judgment call:**
- **Project-wide** (will matter in a month: a schema fact, sign convention, join rule, a gotcha that must never be repeated) → promote to Tier 1 (Step 4 `CRITICAL_RULES`, or Step 5 `Critical Gotchas` if it's a hard technical constraint). For SQL/ETL projects, confirmed schema facts — key columns, join logic, sign conventions — go in as `CRITICAL_RULES` in the existing compact `key  value  note` style. Do **not** create a separate `## SCHEMA` or `## DISCOVERIES` section; this project deliberately keeps confirmed facts as rules so the same fact never lives in two places.
- **Session-only** (only relevant to current WIP) → it stays in today's daily log (Step 6) and nowhere else.

---

## Step 3 — Write + archive HANDOFF.md (the morning brief)

HANDOFF.md is a **snapshot** — the one file this skill fully overwrites. Archive the previous one cheaply first (it's ~80 lines), then overwrite.

**Name the archive after the date in the *previous* brief's own header** (`# HANDOFF — YYYY-MM-DD ...`), not today's date — the archive answers "what did the brief say on day X", so the brief's own date is the useful key and it won't collide with the new brief you're about to write. If you re-run handoff twice on the same day, the previous brief carries today's date and the archive simply overwrites the earlier same-day copy (which was superseded anyway).

```bash
mkdir -p .handoff-archive
if [ -f HANDOFF.md ]; then
  prev=$(grep -m1 '^# HANDOFF' HANDOFF.md | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
  cp HANDOFF.md ".handoff-archive/${prev:-$(date +%Y-%m-%d)}.md"
fi
```

PowerShell equivalent:
```powershell
New-Item -ItemType Directory -Force .handoff-archive | Out-Null
if (Test-Path HANDOFF.md) {
  $prev = (Select-String -Path HANDOFF.md -Pattern '^# HANDOFF.*?(\d{4}-\d{2}-\d{2})').Matches[0].Groups[1].Value
  if (-not $prev) { $prev = Get-Date -Format yyyy-MM-dd }
  Copy-Item HANDOFF.md ".handoff-archive/$prev.md" -Force
}
```

Then overwrite `HANDOFF.md`:

```markdown
# HANDOFF — YYYY-MM-DD HH:MM
# Read this before asking any questions.
# project: [from AI_CONTEXT.md or folder name]

## accomplished
[Section A — bullets, specific]

## files_changed
[Section B — from git status]

## discoveries
[Section C — most important first]

## state
[Section D — "PageName STATUS note", one line each]

## next
[Section E — numbered, actionable]

## commands
[Section F — code block]

## context_files
AI_CONTEXT.md   [exists/missing]  tier-1 universal context
AGENTS.md       [exists/missing]  tier-1 gotchas + rules, tool-independent (primary since 2026-08-15)
CLAUDE.md       [exists/missing]  tier-1 Claude-specific addendum (thin, or gotchas if project hasn't split yet)
.remember/      [exists/missing]  tier-2 daily log (today-YYYY-MM-DD.md)
```

**Keep HANDOFF.md under 80 lines.** It is scanned, not read — density matters. If it overflows, trim lowest-priority first: `commands` → `files_changed` → `accomplished`. **Never trim `discoveries` or `next`** — they are why the next AI opens this file at all.

---

## Step 4 — Update AI_CONTEXT.md (Tier 1) — edit changed lines only, never rewrite

Universal context for all AIs. Touch ONLY what changed:

1. `Updated:` / `updated:` line at top — today's date + time.
2. `## PAGES` — update the status of any page/work-area that changed.
3. `## NEXT_ACTIONS` — reflect current pending work. **Prune to ~10:** drop completed or stale items *before* adding new ones. This is the only section you prune.
4. `## CRITICAL_RULES` — append any discovery you classified as project-wide in Step 2, in the existing `key  value  note` style. Only if it isn't already covered.
5. **Fix the stale buffer pointer:** if `## CONTEXT_FILES` (or any line) still points at `.remember/now.md` as the "session memory buffer", correct it to `.remember/today-YYYY-MM-DD.md` (daily session log; remember plugin rotates older days). `now.md` is dead — never write to it.

**Do NOT touch `## AUDIT_ANCHORS` unless an audited number actually changed.** It is append-only verified data.

Format (token efficiency): one fact per line, `key: value` or plain statement. No prose, no padding, no emoji. Tables only for 3+ columns; otherwise `name  value  note` space-separated. Code blocks for commands only.

---

## Step 5 — Update AGENTS.md or CLAUDE.md (gotchas only, Tier 1)

**Check which file actually holds `## Critical Gotchas` before writing anything — don't assume it's CLAUDE.md.** The recommended project-level pattern is AGENTS.md as the primary tool-independent file with gotchas/rules, and CLAUDE.md demoted to a thin Claude-only addendum. Older projects or ones not yet split may still have gotchas in CLAUDE.md. Resolve it in this order:
1. `AGENTS.md` exists and has a `## Critical Gotchas` section → write there. **If the project has graduated** (a `knowledge/GOTCHAS.md` exists), the full entry goes to the END of `knowledge/GOTCHAS.md`, the one-line title goes to `knowledge/GOTCHA_INDEX.md` (or the index section in AGENTS.md if there is no separate index file yet), and — if the gotcha belongs to one file type — a one-line distillation goes into the matching `.claude/rules/*.md`. Never write the full text into the index file "for now".
2. `AGENTS.md` doesn't exist, or exists but gotchas are still in `CLAUDE.md` → write to `CLAUDE.md`.
3. Never write the same gotcha into both files, and never move existing gotchas between files as part of a handoff — that's a deliberate migration decision (see `project-init`'s "Gotcha graduation" section for how that migration is actually done), not something to do incidentally while closing a session.

If a Step-2 discovery is a **permanent technical constraint** (the kind that, if violated, silently breaks something — e.g. an encoding rule, a port-discovery quirk, a rename-propagation trap), append it to the resolved file's `## Critical Gotchas`, numbered sequentially (check the last number first).

**Never prune or renumber existing gotchas.** Do not rewrite any other section. If nothing this session is a permanent constraint, leave both files untouched.

---

## Step 6 — Append today's entry to the daily log (Tier 2)

If `.remember/` exists, append to `.remember/today-YYYY-MM-DD.md` (today's date). **Create today's file if it's absent, but do NOT create `.remember/` itself** if the project doesn't have it — the project may intentionally not use it.

Entry format, **max 4 lines**:

```
## HH:MM | [branch] [HANDOFF]
[1 line: what was done]
[1 line: most important discovery]
[1 line: next action]
```

Do not rotate, move, or delete any `.remember/` file — the remember plugin owns the daily-log lifecycle (`.done.md` → `recent.md` → `archive.md`). Your job here is one append, nothing more.

---

## Step 7 — Output confirmation

Compact, one screen, no filler:

```
HANDOFF — [date]  project: [name]

git: [N commits | M files | +X -Y]   (or: no git — synthesized from memory)

tier-1  AI_CONTEXT.md   pages + next_actions updated [N pruned]; [N rules promoted / no rule change]
        AGENTS.md/CLAUDE.md   gotchas [N added to <which file> / no change]
tier-2  today-YYYY-MM-DD.md   entry appended
snapshot HANDOFF.md     overwritten; prev → .handoff-archive/[date].md

resume: read HANDOFF.md → any AI starts immediately
```

---

## Rules

1. **git output is authoritative** for file changes — trust it over memory.
2. **HANDOFF.md is always fully overwritten** — it's a snapshot. This is the one intentional exception to rule 3.
3. **Never rewrite a full file** otherwise — edit only the lines that changed.
4. **Update only what exists.** Never create `AI_CONTEXT.md`, `AGENTS.md`, `CLAUDE.md`, or `.remember/` if absent — scaffolding a new project's files is `project-init`'s job, not this skill's. The only things this skill creates are `HANDOFF.md`, the `.handoff-archive/` dir, and today's daily-log file (only when `.remember/` already exists).
5. **Append-only is not prunable.** `Critical Gotchas`, `CRITICAL_RULES`, `AUDIT_ANCHORS` are never capped. Only `NEXT_ACTIONS` is pruned.
6. **Discoveries > Accomplishments** — future AIs know the codebase; they don't know the surprises.
7. **Don't touch `.remember/` rotation.** The remember plugin owns it. One append to today's file is your only write there.
8. **GEMINI.md** — deprecated, do not touch.

## Detection logic

| File | Exists? | Action |
|---|---|---|
| `HANDOFF.md` | always written | archive prev → overwrite |
| `AGENTS.md` | if exists with `## Critical Gotchas` | append a gotcha only if a permanent constraint surfaced (see Step 5) |
| `CLAUDE.md` | if exists | append a gotcha there instead **only if** `AGENTS.md` doesn't hold that section (see Step 5) — otherwise leave it, it's a thin addendum |
| `AI_CONTEXT.md` | if exists | update `updated`/`PAGES`/`NEXT_ACTIONS` (+ prune), promote rules, fix `now.md` pointer |
| `.remember/` | if exists | append one entry to `today-YYYY-MM-DD.md` (create the day's file if needed) |
| `GEMINI.md` | skip | deprecated |

Claude-only project (no `AI_CONTEXT.md`): update `AGENTS.md` (or `CLAUDE.md` if that's still where gotchas live) + `HANDOFF.md` + daily log only.
Multi-AI project (`AI_CONTEXT.md` present): update all tiers.
