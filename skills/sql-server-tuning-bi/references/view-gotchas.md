# SQL Server view gotchas (reusable across projects)

Read before writing, changing or deploying any T-SQL view. Each entry: symptom, why, fix, how to check.
Numbers are illustrative, rounded from real incidents on a BI data warehouse; names are generic.
Useful helper scripts to write per project: deploy-test, benchmark, backup-view-definitions, post-deploy-check.

## SQL-G1 A CTE or view referenced N times is computed N times
- Symptom: a view looks cheap but reads the fact tables 2-4x. a check view v1 used ~33 s CPU (3 refs); a monthly view read ~230k pages (2 refs) vs ~145k after;
  an exception view read the month view 4 times (4 UNION branches): ~1.0M reads vs ~260k after.
- Why: SQL Server inlines CTEs and views; it never materialises them. Each reference is a new scan.
- Fix: read the source once. Use window functions (running SUM, LEAD) on one stream instead of joining a CTE to
  itself; evaluate several checks in ONE pass with `CROSS APPLY (VALUES (...), (...)) AS c(..., Hit) WHERE c.Hit = 1`
  instead of `UNION ALL` of N selects over the same view.
- Check: count how many times each CTE / view name appears after its definition. More than once = suspect.
  This was documented and still recurred within 4 days: grep for it on every review.

## SQL-G2 `TOP` turns a 1-second view into a 3-minute view (row goal)
- Symptom: `SELECT * FROM view` = 1.2 s, but SSMS "Select Top 1000 Rows" on the same view = 175 s, single-threaded,
  7.8 million reads. Same rows. Power Query / Power BI Navigator previews also add `TOP 1000`.
- Why: `TOP` (also `FAST n`, `EXISTS`, `IN`) sets a row goal; the optimizer picks nested loops that re-run the inner
  side (a whole CTE / view) per outer row. Worst with G1 patterns, UNION ALL, window functions, inequality joins.
- Fix: remove G1 multi-references and give the optimizer one stream. A view cannot carry
  `OPTION (USE HINT('DISABLE_OPTIMIZER_ROWGOAL'))`, so the shape has to be robust on its own.
- Check: always benchmark the access patterns in SQL-G4, not only `SELECT *`.

## SQL-G3 Measure on the server, by CPU and logical reads, not wall time
- Parallel plans hide CPU (a 300 ms query can burn 1.9 s CPU); other jobs (a Power BI gateway refresh pulling
  whole fact tables) can make any query look slow. One user query ran 2 min 24 s while the gateway was using
  ~130 s CPU per query.
- How: prefix the query with a unique comment tag, run it, then read
  `sys.dm_exec_query_stats` joined to `sys.dm_exec_sql_text` WHERE text LIKE '%tag%':
  `total_worker_time` (CPU), `total_logical_reads`, `total_elapsed_time`. Needs VIEW SERVER STATE.
- To see who is running now: `sys.dm_exec_requests` (wait_type, blocking_session_id) + `sys.dm_exec_sessions`
  (host_name, program_name). `Mashup Engine` on a gateway host = a Power BI refresh.

## SQL-G4 Deploy gate: 7 access patterns per view
Run each against the exact view body (wrap the body as a CTE `VwT`) and fail on CPU or reads above a limit
(example limits: CPU 5,000 ms, reads 600,000 per query; revisit as data grows):
`SELECT *` · `TOP (1000)` · `TOP (10)` · one month `WHERE YM = ...` · `GROUP BY` over a year ·
`COUNT(*)` · key filter (`WHERE AssetCode = ...` / `GLAccountID = ...`).
Also compare results with the live view row by row (every column) when the change is a refactor.

## SQL-G5 Empty-string keys are not NULL
- Symptom: per-key totals off by a large round amount (a large round amount: one `code = ''` line and its
  uncoded reversal looked like a mismatch).
- Fix: `NULLIF(LTRIM(RTRIM(col)), '')` before testing `IS NULL` or grouping. Applies to every ERP code column.

## SQL-G6 Pick columns that an existing index already covers
- Example: interest per GL read `FACT_Sales` filtered on `Level3` (not indexed): 82,851 reads, 96 ms.
  Getting the GL list from the small mapping table and reading `AmountReporting * SignMultiplier` (in the
  `(DataType, GLAccountID ...) INCLUDE (AmountReporting ...)` index) instead of `Balance` (not included):
  324 reads, 13 ms, identical rows.
- How: `sys.indexes` + `sys.index_columns` for key order and INCLUDE columns; filter on the leading keys, select
  only included columns. Prove the substitute column equals the original row by row before switching.
- A heap with no usable index (`FACT_Ledger`) cannot be fixed from a view: write an index proposal for the
  table owner (filtered index on the few GLs used is cheap to maintain), do not create it yourself.

## SQL-G7 Deploying on a shared server with no backup
- Create-only: `CREATE VIEW` errors if the name exists; never `CREATE OR ALTER` / `DROP` for a new object.
- Guard batch first: `IF DB_NAME() <> N'<db>' ... ELSE IF OBJECT_ID(N'dbo.<view>') IS NOT NULL ...` then
  `RAISERROR(..., 16, 1); SET NOEXEC ON;`. A `THROW` alone does not stop later `GO` batches in SSMS.
- `SET NOEXEC ON` is session-wide. End the file with `SET NOEXEC OFF; GO` (it runs even under NOEXEC), run the
  WHOLE file (F5, no selection) in a NEW query tab and close the tab afterwards. A stuck session reports
  "Commands completed successfully" without doing anything.
- Altering later: ALTER only your own objects, proven by name + schema + exact `create_date` in the guard;
  back up `OBJECT_DEFINITION` to a rollback file (CREATE -> ALTER) first; after deploy, compare the stored
  definition with the tested file (ignore the first word CREATE/ALTER) and re-run the numbers.
- Check the day's changes: `sys.objects WHERE modify_date >= <today>` shows nothing else was touched.

## SQL-G9 House style for views (the user's format, 2026-10-19) -- the next person must be able to read, trace and fix it
- File header block (before `USE`, so not stored in the view): view name, which report uses it, what one row
  means, which GL accounts, what was verified, history (version + why), how to change it safely.
- `USE [db]; GO` · `SET ANSI_NULLS ON; GO` · `SET QUOTED_IDENTIFIER ON; GO` · `ALTER VIEW [dbo].[name] AS`
  (deploying through sqlcmd: add `-I`, otherwise the view is stored with QUOTED_IDENTIFIER OFF).
- Every step / branch opens with a `/* ===== ... ===== */` block: what it does, the source, and WHY it is written
  this way when that is not obvious (performance trick, data quirk). Short Thai comments for Thai teams.
- Meaningful aliases (`asset`, `chk`, `posting`, `bs`, `pl`, `bal`, `cal`), never `a`/`b`/`x`.
- One column per line, one condition per line, `CASE WHEN ... THEN ... ELSE ... END` laid out vertically,
  `FROM` / `JOIN` / `WHERE` / `GROUP BY` / `HAVING` each on its own line with a one-line comment for the intent.
- Name the final result section `ผลลัพธ์` / "Result" and say what one row is and what each column group means.
- User-facing text values (e.g. a Detail column) in the readers' language.

## SQL-G8 Month grid without self-joins
- Need a row per entity per month including quiet months: aggregate movements once, compute running totals and
  `LEAD(YM)` per entity, then join a month list `ON m.YM >= p.YM AND (p.NextYM IS NULL OR m.YM < p.NextYM)`.
  Movement columns only where `m.YM = p.YM`. Same result as grid + LEFT JOIN, one source scan instead of two.
- The grid usually runs to the current (unclosed) month: the report must cap at the last closed month, and check
  that no posting is dated after the grid end (ERP schedules can post interest years ahead).
