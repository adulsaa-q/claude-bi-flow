# BI + AI team flow (managed by claude-bi-flow; edit the repo, not this block)

**Language:** reply in the language the user writes in. Keep code and technical terms in English. AI-facing files (CLAUDE.md, AGENTS.md, skills, agent definitions) are written in English.

## Skill routing (invoke the skill first, announce it in one short sentence)

| Situation | Skill |
|---|---|
| Write / edit / review DAX or measures, query a semantic model | `power-bi-dax` |
| Tables, columns, relationships, calculation groups | `power-bi-modeling` |
| Report layer: pages, visuals, themes, filters (PBIR) | `power-bi-report`, `power-bi-visuals`, `power-bi-pages`, `power-bi-themes`, `power-bi-filters` |
| Export / import TMDL, deploy | `power-bi-deployment` |
| Dashboard design, IBCS, visual selection | `power-bi-design-advanced` |
| Custom visuals with SVG-in-DAX | `power-bi-svg-design` |
| Document or audit a model | `power-bi-docs` |
| RLS / OLS | `power-bi-security` |
| Review pandas / SQL / ETL code, including code you wrote yourself, before commit or delivery | `data-code-review` |
| Pipeline or script is broken, slow, or gives wrong numbers right now | `data-debug-troubleshoot` |
| New dataset (CSV / Excel / Parquet) before ETL or a dashboard | `data-profiling` |
| Star schema, fact/dimension, SCD, surrogate keys | `data-warehouse-kimball` |
| Slow SQL Server query, indexes, execution plans, or ANY SQL Server view change | `sql-server-tuning-bi` |
| Start a new project or lay out a new repo | `project-init` |
| End of day / close session / save progress | `handoff` |

Two skills fit: pick the more task-specific one. Nothing fits: just work normally, do not force a skill.

## Code habits

- Do what was asked and do not silently change anything else (output text, formats, names, behavior). If you see something better, a risk, or a nearby bug, say so briefly with the reason and the trade-off, and let the user decide.
- Read the existing code first and reuse it. Do not add a near-duplicate beside it.
- Run it before saying it is done. State what you ran and what you did not verify.
- Before declaring data code ready for real use, run it through `data-code-review` once.

## Working style for BI projects

- Step by step. The AI runs background queries and checks; the user builds or approves visuals.
- Never read, print, or commit `.env` or any file with credentials. Use `.env.example` for structure.
- Databases you do not own: SELECT only, small exploratory queries (aggregates / TOP), no PII columns. Any write (`UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`) needs the user's explicit OK first.
- Close Power BI Desktop before editing `.tmdl` or report JSON on disk; otherwise use live `pbi` commands.
- Anything reusable written in the session scratchpad (`%LOCALAPPDATA%\Temp\claude\...`) moves into the project's `scripts/` before the session ends; the scratchpad is auto-deleted.
- An automation (scheduled task, hook) is not done until it has been seen to run once.
- When you find a surprising constraint or bug cause, add it to the project's gotcha list immediately.
