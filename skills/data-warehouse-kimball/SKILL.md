---
name: data-warehouse-kimball
description: Data warehousing and dimensional modeling standards based on Ralph Kimball's methodology. Guides the design of robust star schemas, fact tables, dimension tables, slowly changing dimensions (SCD), and date dimensions for optimized Power BI reporting. ALWAYS trigger this skill if the user mentions database design, data warehousing, Kimball methodology, star schemas, dimensional modeling, surrogate keys, or slowly changing dimensions (SCD).
---

# Dimensional Modeling & Data Warehousing (Kimball Methodology)

This skill provides guidelines for designing and building analytical databases using Ralph Kimball's dimensional modeling technique, optimized for Power BI semantic models.

---

## When to Use

- Designing a new Datamart or Data Warehouse schema.
- Structuring tables in SQL Server to simplify Power BI DAX calculations and improve performance.
- Resolving complex many-to-many relationship issues in reporting.
- Implementing tracking for historical changes (Slowly Changing Dimensions).

---

## The 4-Step Dimensional Design Process

Always follow these four steps sequentially when designing analytical models:

1. **Select the Business Process**: Identify what process is being analyzed (e.g., Sales Invoicing, Inventory Snapshots, HR Attrition).
2. **Declare the Grain**: Define exactly what a single row in the fact table represents (e.g., "One line item on a customer invoice", "Daily count of items in a warehouse"). *Never mix grains in a single fact table.*
3. **Identify the Dimensions**: Determine the context of the business process (Who, What, Where, When, Why, How).
4. **Identify the Facts**: Determine the numeric, measurable metrics belonging to the process (e.g., Quantity Sold, Extended Amount, Discount Price).

---

## Star Schema vs. Snowflake Schema

Power BI engine (VertiPaq) is highly optimized for the **Star Schema**. 

```
   ┌───────────────┐        ┌────────────────┐        ┌───────────────┐
   │ DimCustomer   │◄───────┤   FactSales    ├───────►│   DimProduct  │
   └───────────────┘        └───────┬────────┘        └───────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │    DimDate    │
                            └───────────────┘
```

### 🚫 Snowflake Schema (Avoid)
- Structuring dimensions by normalizing them (e.g., `FactSales` ➔ `DimProduct` ➔ `DimSubcategory` ➔ `DimCategory`).
- **Why**: Creates extra relationship hops, slowing down filter propagation in Power BI and leading to overly complex DAX.

###  Star Schema (Recommended)
- De-normalize secondary dimensions directly into the primary dimension (e.g., merge Category and Subcategory columns directly into `DimProduct`).
- **Result**: Direct relationships (1-to-many) from Fact to Dimension tables.

---

## Keys in the Data Warehouse

### Surrogate Keys (SK)
- **Rule**: Always use integer-based surrogate keys (e.g., `ProductSK` = 125) to join Fact and Dimension tables rather than operational Natural Keys (e.g., `ProductCode` = 'PROD-XYZ-99').
- **Reason**: 
  1. Performance: Joins on `INT` or `BIGINT` are much faster than joins on `VARCHAR`.
  2. History Tracking: Natural keys cannot support Slowly Changing Dimensions Type 2 (multiple rows for the same product code over time).

---

## Slowly Changing Dimensions (SCD)

Determine how to handle changes in dimension attributes over time:

### Type 1: Overwrite (No History)
- Overwrites the old value with the new value. Historical context is lost.
- *Use case*: Correcting typos, or when history is irrelevant (e.g., customer correcting their middle name).

### Type 2: Add New Row (History Tracked)
- Creates a new row in the dimension table with a new Surrogate Key. Uses timestamps to track active periods.
- *Required columns*: `StartDate` (DATETIME), `EndDate` (DATETIME), and `IsCurrent` (BIT / 1 or 0).
- *Use case*: Track salesman region shifts (e.g., Salesperson moves from North to South region, historical sales must remain credited to North, new sales credited to South).

---

## Date & Time Dimensions (Role-Playing)

- **Physical Date Table**: Always create a physical Date dimension table (`DimDate`) in the SQL database. Do not rely on Power BI's automatic date/time hierarchies.
- **Auto Date/Time Warning**: Power BI's built-in Auto Date/Time creates a hidden date table for *every single date column* in your model, causing massive file sizes and memory bloat. Disable this setting.
- **Granularity**: Separate Date and Time into two distinct dimensions if timestamp-level analysis is required. *Never join Fact tables to Date tables on full timestamp strings.* Join on `DateKey` (Format: `YYYYMMDD` as an integer) and keep time in a separate dimension.

---

## Working in an EXISTING warehouse (any project)

Before designing or recommending anything in a warehouse that already exists:

1. **Discover its conventions first, then follow them** — naming patterns (`FACT_*`/`Dim*` vs `fact_`/`dim_`), key style (integer DateKey vs datetime), and relationship layout. Query `INFORMATION_SCHEMA.TABLES`/`COLUMNS` and read the project's `AGENTS.md` if one exists (or `CLAUDE.md` if the project hasn't split its rules/gotchas out yet — see `D:\AI_WORKSPACE_ARCHITECTURE.md` §10). Consistency with the existing model beats textbook purity — a "correct" table that breaks the house style creates more confusion than it fixes.
2. **Hunt for mixed-grain traps before trusting any fact table** — a common real-world anti-pattern is pre-aggregated rollup rows stored in the same table as detail rows (distinguished only by a flag column). Every query must filter that flag or totals double-count. When you find one: document it, filter it, but do NOT copy the pattern into new designs — new fact tables get one grain, rollups live in separate tables or views.
3. **New greenfield designs follow the standards above** (4-step process, star schema, surrogate keys, physical DimDate) regardless of what legacy tables look like.
