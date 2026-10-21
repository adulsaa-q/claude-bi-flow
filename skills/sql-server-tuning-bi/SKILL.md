---
name: sql-server-tuning-bi
description: SQL Server query tuning and performance optimization specifically tailored for Business Intelligence (BI), data warehousing, and reporting workloads (T-SQL, columnstore indexes, partition elimination, avoiding locks). ALWAYS trigger this skill if the user mentions SQL query performance, slow queries, database indexing, temp tables vs CTEs, NOLOCK, execution plans, or optimizing SQL Server database queries for Power BI. ALSO trigger before writing, changing or deploying ANY SQL Server view, even when nobody mentioned speed.
---

# SQL Server Performance Tuning for BI & Reporting

This skill outlines strategies to write, analyze, and optimize T-SQL queries for Business Intelligence (BI) platforms (Power BI, paginated reports) and data warehouse environments.

**Before writing, changing or deploying any view, read `references/view-gotchas.md`** (SQL-G1..G8: CTE referenced N times = N scans, the `TOP` row-goal trap that turned 1.2 s into 175 s, measuring by server CPU/reads, the 7-pattern deploy gate, empty-string keys, covering-index column choice, safe create/alter on a shared server, month grids without self-joins). Every one of these has already cost real time.

---

## When to Use

- Power BI DirectQuery reports are loading slowly.
- Heavy analytical queries are causing 100% CPU usage on the SQL Server.
- Tables are getting locked due to long-running read operations.
- Determining whether to use CTEs, Views, Stored Procedures, or Temporary Tables.

---

## Step 1: Writing SARGable Queries (Search Argument Able)

Query clauses (WHERE, JOIN, HAVING) must be SARGable to allow SQL Server to use index seeks instead of scanning the entire table.

### 🚫 Non-SARGable (Avoid)
Do not wrap index columns inside functions:
```sql
SELECT * FROM Sales.Orders 
WHERE YEAR(OrderDate) = 2026;

SELECT * FROM Sales.Orders 
WHERE ISNULL(CustomerID, 0) = 99;
```

###  SARGable (Recommended)
Keep the index column isolated:
```sql
SELECT * FROM Sales.Orders 
WHERE OrderDate >= '2026-01-01' AND OrderDate < '2027-01-01';

SELECT * FROM Sales.Orders 
WHERE CustomerID = 99;   -- ISNULL(CustomerID,0)=99 can only match when CustomerID=99; drop the wrapper
```

---

## Step 2: Indexing Strategies for BI (Columnstore vs. Rowstore)

In reporting databases (Data Warehouses / Datamarts), data access patterns are read-heavy and aggregate-heavy (e.g., SUM, AVG).

### Clustered Columnstore Indexes (CCI)
- **Use case**: Large fact tables (typically > 1,000,000 rows).
- **Benefit**: Stores data column-by-column, achieving up to 10x data compression. Aggregation queries only read the specific columns requested, bypassing the rest.
- **Rule**: Create a CCI on your massive fact tables.
  ```sql
  CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales ON dbo.FactSales;
  ```

### Non-Clustered Columnstore Indexes (NCCI)
- **Use case**: Operational databases (OLTP) where you need to run reports without converting the entire table to columnstore.

---

## Step 3: Temporary Tables vs. Common Table Expressions (CTEs)

| Feature | CTE (`WITH ... AS`) | Temporary Table (`#Temp`) |
| :--- | :--- | :--- |
| **Materialization** | inline view (evaluated at runtime, not stored) | Written to `tempdb` |
| **Statistics** | No statistics (Cardinality estimate can be poor) | Yes, has statistics (helps Query Optimizer) |
| **Indexing** | Cannot be indexed | Can create indexes for fast joins |
| **Multiple references**| Evaluated multiple times if referenced multiple times | Read once, queried multiple times |
| **Best for** | Small datasets, simple recursion, organization | Large intermediate datasets (>10,000 rows) |

### Optimization Rule:
For complex ETL steps or BI datasets:
- If processing `< 10,000` rows: Use a **CTE** for readability.
- If processing `> 10,000` rows or joining the intermediate result multiple times: Use a **Temporary Table** (`#Temp`), specify a primary key, and insert data first.

---

## Step 4: Troubleshooting Locks & Blocks in BI

Analytical queries should not block transactional writes.

1. **RCSI (Read Committed Snapshot Isolation)**:
   This is the best practice for databases hosting BI data. Readers do not block writers, and writers do not block readers. SQL Server stores row versions in `tempdb`.
   ```sql
   ALTER DATABASE [YourDB] SET ALLOW_SNAPSHOT_ISOLATION ON;
   ALTER DATABASE [YourDB] SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
   ```
2. **`WITH (NOLOCK)` (Dirty Reads)**:
   If RCSI cannot be enabled, use `WITH (NOLOCK)` or `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` for reporting queries. 
   *Warning: Data might be in an uncommitted state (dirty reads), causing minor numerical discrepancies.*

---

## Step 5: Execution Plan Red Flags

Run `SET STATISTICS XML ON;` or inspect the graphical execution plan in SSMS for these bottlenecks:

- **Table Scan / Clustered Index Scan**: SQL Server read the entire table. Needs index tuning or query refactoring.
- **Key Lookup (RID Lookup)**: SQL Server found the row in a non-clustered index, but had to go back to the clustered index to fetch additional columns.
  - *Fix*: Create a `COVERING INDEX` using the `INCLUDE` clause:
    ```sql
    CREATE NONCLUSTERED INDEX IX_Orders_Cust ON Sales.Orders(CustomerID) INCLUDE (OrderDate, TotalAmount);
    ```
- **Hash Match Join**: Occurs on large unsorted tables. If unexpected, it may indicate missing indexes.
- **Spill Warnings (Yellow Warning Icon)**: The Query Optimizer estimated too little memory, and the operation (Sort/Hash) spilled to `tempdb` disk.

---

## Access & safety rules (any project)

the user's access varies by project — often analyst (SELECT) on databases owned by a DW team; on other projects you may own the ETL and the database outright. So don't assume either way — check per project. What stays constant is the write discipline:

- **Destructive statements (`DROP`, `TRUNCATE`, `DELETE`, `UPDATE`, `ALTER`) never run casually — on ANY database, owned or not.** Before executing one: state exactly what it will touch and why, get the user's explicit confirmation, and have a rollback path (wrap in `BEGIN TRAN` + verify rowcount with a `SELECT` first + `COMMIT` only after the numbers check out; or take a backup of the affected table). Production data feeds financial dashboards — a careless UPDATE is worse than a slow query.
- On databases the user does **not** own: measure with `sqlcmd` + `SET STATISTICS IO, TIME ON;` (or the project's read-only MCP), and write `CREATE INDEX` / `ALTER DATABASE` changes as copy-pasteable recommendations for the owning DBA team.
- On databases the user **does** own (future ETL projects): the same tuning actions are runnable directly — apply the confirmation + transaction discipline above, and test on dev/staging before prod when one exists.
- Before optimizing a query that returns "wrong" numbers, check the project's `AGENTS.md` (or `CLAUDE.md` if that's still where gotchas live) / data-quirk notes first — column trimming rules, filter flags, and lookalike column names cause wrong results that no index will fix. Slow is not the only failure mode.
