# IBCS Notation Reference

Source: IBCS Association — ibcs.com (CC BY-SA 4.0)
Full spec: IBCS Standards 1.2 (book/PDF — ibcs.com/standards)

## The SUCCESS Framework

| Letter | Principle | Meaning |
|---|---|---|
| **S** | SAY | Convey a message — every chart must have a clear title stating the insight |
| **U** | UNIFY | Apply semantic notation — same thing = same look everywhere |
| **C** | CONDENSE | Increase information density — show more in less space |
| **C** | CHECK | Ensure visual integrity — no distortion, correct zero baselines |
| **E** | EXPRESS | Choose proper visualization — match chart type to data question |
| **S** | SIMPLIFY | Avoid clutter — remove every non-data element that doesn't add value |
| **S** | STRUCTURE | Organize content — consistent layout across all pages |

---

## Semantic Color System (UNIFY)

These colors are fixed across ALL charts in an IBCS-compliant report. Do not use these colors for anything else.

| Scenario | Element | Fill | Border | Font |
|---|---|---|---|---|
| **AC** — Actual current period | Bar/column | `#1A1A1A` (black) | — | `#1A1A1A` |
| **BU** — Budget / Plan | Bar/column | transparent | `#888888` (gray) 2px | `#888888` |
| **PY** — Prior Year | Bar/column | `#CCCCCC` (light gray) | — | `#888888` |
| **FC** — Forecast | Bar/column | hatched / dotted | `#1A1A1A` | `#1A1A1A` |
| **Positive variance (AC > BU)** | Delta bar | `#107C10` (green) | — | `#107C10` |
| **Negative variance (AC < BU)** | Delta bar | `#D13438` (red) | — | `#D13438` |
| **Neutral / reference** | Line | `#888888` | — | `#888888` |

**Rule:** Never use color to identify categories — only to show scenario (AC/BU/PY) or direction (positive/negative).

---

## Scenario Labels (UNIFY)

Always abbreviate scenarios consistently:

| Full name | Abbreviation |
|---|---|
| Actual | **AC** |
| Budget | **BU** |
| Plan | **PL** |
| Previous Year | **PY** |
| Forecast | **FC** |
| Target | **TG** |

Write abbreviations in the column/bar header, not in a legend.

---

## Chart Title Rules (SAY)

IBCS titles state the **insight**, not just the topic.

```
Wrong:  "Sales by Region 2025"
Right:  "EMEA sales exceed budget by 12% in Q3 2025"

Wrong:  "Revenue Trend"
Right:  "Revenue declining 3% MoM since March 2025"
```

Format: `[Metric] [direction/status] [by how much] [timeframe/context]`

---

## Chart Type Rules (EXPRESS)

### When to use which chart:

| Data question | IBCS-preferred chart |
|---|---|
| Comparison across categories (few) | Horizontal bar chart |
| Comparison across categories (many) | Small multiples |
| Time trend | Line chart (no fill area) |
| Actual vs Budget/Plan | Integrated bar+delta chart |
| Waterfall (contribution) | Waterfall chart (bridge chart) |
| Part-to-whole | Stacked bar (not pie/donut) |
| Distribution | Dot plot or histogram |
| Correlation | Scatter chart |

### IBCS strictly discourages:
- Pie charts (use stacked bars instead)
- 3D charts (distort perception)
- Donut charts for comparison
- Area charts with fill (use line charts)
- Dual-axis charts without clear labeling
- Bubble charts without a legend for size scale

---

## Axis Rules (CHECK — visual integrity)

- **Always start Y-axis at zero** for bar/column charts — never truncate
- **Exception:** Line charts may start above zero when showing trends, but add a broken-axis indicator
- **Time flows left→right** on X-axis always (past → future, never reversed)
- **Consistent axis scale** across all charts on the same page showing the same metric
- **No axis gridlines** except horizontal light gray on value axis
- **Remove axis titles** when the chart title is descriptive enough

---

## Typography Rules (SIMPLIFY)

| Element | Font | Size | Color |
|---|---|---|---|
| Page title / insight title | Segoe UI Semibold | 14–16px | `#1A1A1A` |
| Chart title | Segoe UI Semibold | 12px | `#1A1A1A` |
| Axis labels | Segoe UI | 10–11px | `#605E5C` |
| Data labels | Segoe UI | 10–11px | `#1A1A1A` |
| Footnotes / sources | Segoe UI | 9px | `#888888` |

**Rule:** Never use more than 2 font sizes per chart. Never use decorative fonts.

---

## Density Rules (CONDENSE)

- Use **small multiples** instead of one big chart with a legend
- Remove chart borders and background fills from individual visuals
- Combine Actual + Budget + Delta in one visual (integrated chart) instead of 3 separate charts
- Show numbers directly on bars (data labels) — remove the value axis when you do this
- Remove chart legends when the chart title and direct labels are sufficient

---

## Clutter Rules (SIMPLIFY)

Remove these elements unless absolutely necessary:
- Chart backgrounds (set to transparent)
- Visual borders
- Grid lines on the category axis
- Tick marks on axes
- Drop shadows on any element
- Decorative images or logos inside charts
- Color fills on table/matrix headers (use bold text instead)
- Rounded corners on bars (use square corners for precision)

---

## Structure Rules (STRUCTURE)

- **Consistent layout** across all pages: same title position, same slicer placement, same margin
- **Reading order**: F-pattern (top-left summary → top-right trend → bottom detail)
- **Page flow**: Executive summary page → Department pages → Detail drill-through pages
- **Section headers**: Plain text, not colored shapes
- **Numbering**: Pages numbered consistently, reports dated

---

## IBCS-Compliant DAX Variance Template

```dax
-- Semantic delta labeling
Delta Label =
VAR _ac = [Sales AC]
VAR _bu = [Sales BU]
VAR _delta = _ac - _bu
VAR _pct = DIVIDE(_delta, ABS(_bu))
RETURN
    IF(_delta >= 0,
        "▲ " & FORMAT(_delta, "#,##0") & " (" & FORMAT(_pct, "+0.0%") & ")",
        "▼ " & FORMAT(ABS(_delta), "#,##0") & " (" & FORMAT(_pct, "0.0%") & ")"
    )

-- Semantic color via conditional formatting
Delta Color =
IF([Sales AC] >= [Sales BU], "#107C10", "#D13438")
```

---

## Further Reading

- Full IBCS Standards 1.2: https://www.ibcs.com/standards/
- Free online browser: https://www.ibcs.com/standards (requires free account)
- Book: "Solid, Outlined, and Hatched" by Hichert + Faisst (Amazon)
- Chartisan (Power BI implementation): https://www.chartisan.com
