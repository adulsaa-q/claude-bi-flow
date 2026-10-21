# Power BI Visual Selection Guide

Chart chooser — matching data questions to the right visual type.

---

## Primary Decision Tree

```
What do you want to show?
│
├── COMPARISON
│   ├── Few categories (≤ 8) → Clustered bar chart (horizontal)
│   ├── Many categories (> 8) → Table with conditional formatting
│   ├── Over time → Line chart
│   └── Actual vs Target → Bullet chart (SVG) or grouped bar
│
├── COMPOSITION / PART-TO-WHOLE  
│   ├── Static snapshot → Donut (≤ 5 parts) / Stacked bar (> 5)
│   ├── Over time → Stacked column (few periods) / Area (many periods)
│   └── Hierarchy → Treemap / Decomposition tree
│
├── DISTRIBUTION
│   ├── Single variable → Histogram / Box plot
│   └── Two variables → Scatter chart
│
├── RELATIONSHIP / CORRELATION
│   ├── Two metrics → Scatter chart
│   ├── Many variables → Scatter matrix (small multiples)
│   └── Cause and effect → Key influencers visual
│
├── TREND
│   ├── Single metric → Line chart
│   ├── Multiple metrics → Multi-line chart (max 4 lines)
│   └── Forecast + actual → Line with forecast
│
├── GEO / LOCATION
│   ├── Country/region level → Filled map (choropleth)
│   ├── Exact lat/lng points → Bubble map
│   └── Custom territory → Shape map
│
├── KPI / SCORECARD
│   ├── Single headline number → Card visual
│   ├── vs Target → KPI visual or Gauge
│   └── Multiple metrics overview → Multi-row card / Matrix scorecard
│
└── FLOW / CHANGE
    ├── From → To (absolute) → Waterfall chart
    ├── From → To (process) → Funnel chart
    └── Ranking shift over time → Ribbon chart
```

---

## Comparison Charts

### Clustered Bar Chart (Horizontal)
**Best for:** Comparing values across categories. Most readable for category names.
- Categories on Y-axis (easy to read long names)
- Sort descending by value unless category order matters (e.g., months)
- Max 15 categories before switching to a table

### Clustered Column Chart (Vertical)
**Best for:** Time series comparison where time order matters.
- Time on X-axis (left = oldest, right = newest)
- Use when categories are short labels (Q1, Jan, Week 1)
- Avoid if > 12 time periods — switch to line chart

### Small Multiples
**Best for:** Comparing the same metric across many categories simultaneously.
- One mini-chart per category
- Shared axis scale across all multiples
- Better than a legend with many colors
- Use when you have 4–16 categories to compare

---

## Trend Charts

### Line Chart
**Rules:**
- Max 4–5 lines before it becomes unreadable
- Label lines directly at the end (avoid legends when possible)
- Do not fill area under line (use Area chart only for cumulative)
- Start Y-axis at 0 only when 0 is meaningful; otherwise start at the data range

### Area Chart
**Use only for:** Cumulative totals, stacked contributions over time.
**Avoid for:** Comparing individual trends (lines are clearer).

---

## Part-to-Whole Charts

### Donut Chart
**Use only when:** ≤ 5 segments AND the parts-to-whole relationship is the primary story.
- Put the most important number in the center
- Label slices directly (not with a legend)
- Sort from largest to smallest, starting at 12 o'clock

### Stacked Bar / Column
**Use when:** > 5 segments OR when individual segment trends matter.
- Stacked column → when time is on X-axis
- Stacked bar → when category comparison is primary
- 100% stacked → when proportions matter more than absolute values

### Treemap
**Use for:** Hierarchical part-to-whole (e.g., Sales by Region > Country > Product).
- Use only 2 levels of hierarchy maximum
- Avoid if precise comparisons are needed (area is harder to read than length)

---

## KPI Charts

### Card Visual
**Use for:** Single headline metric.
- Large number, short label below
- One card per metric — don't crowd multiple numbers
- Add comparison period text: "vs PY: +12%"

### KPI Visual
**Use for:** Metric with a target and trend.
- Shows: current value, target, trend indicator, trend sparkline
- Best for executive scorecards

### Gauge Visual
**Use for:** Progress toward a single target (e.g., 73% of annual target).
- Works well when there's a clear max (100% or a capacity limit)
- Avoid when showing multiple metrics — use a table instead

---

## Table / Matrix

### When to use a table:
- Many dimensions × many metrics
- Precise numbers matter more than patterns
- Users need to scan and look up specific values
- Data has > 20 rows (charts become unreadable)

### Table design rules:
- Remove all gridlines except horizontal row separators
- Right-align numbers; left-align text
- Bold total rows
- Use conditional formatting (color scale or data bars) instead of a separate chart for one column
- Limit to 5–6 columns maximum

### Matrix design rules:
- Collapse hierarchy by default (show top 2 levels)
- Add subtotals only when meaningful
- Use stepped layout for hierarchy indent
- Column header background: `#F5F5F5` with bold text

---

## Visuals to Avoid

| Visual | Why to avoid | Replace with |
|---|---|---|
| Pie chart with > 5 slices | Hard to compare thin slices | Stacked bar chart |
| 3D bar/column/pie | Distorts values (perspective effect) | Flat 2D equivalent |
| Dual Y-axis charts | Misleading scale comparison | Two separate charts or small multiples |
| Gauge with no target | Meaningless without reference | Card visual |
| Radar/spider chart | Very difficult to read accurately | Small multiples bar charts |
| Waterfall with too many bars (> 15) | Becomes unreadable | Summary waterfall + detail table |
| Bubble chart without size legend | Size = unknown | Add size reference legend |

---

## Accessibility Rules

Apply to all visual selections:
- Never use color as the ONLY way to convey information — add labels, patterns, or shapes
- Minimum contrast ratio 4.5:1 for text on background (WCAG AA)
- All charts must have alt text (Accessibility panel in Power BI)
- Use `Color-blind safe` theme as a starting point if accessibility is required
- Recommended colorblind-safe palette: `#0072B2`, `#E69F00`, `#009E73`, `#CC79A7`, `#D55E00`, `#56B4E9`, `#F0E442`

---

## Slicer Design Rules

| Slicer type | Use when |
|---|---|
| Dropdown | Many items (> 10), space is limited |
| List | Few items (≤ 8), always visible selections preferred |
| Between (range) | Date or numeric range selection |
| Relative date | "Last 7 days", "This month" type filters |
| Tile/button slicer | ≤ 5 options, tab-like UI preferred |

**Layout rules:**
- Place all slicers in one consistent location (top bar or left panel — not both)
- Group related slicers together
- Always include a "Clear filters" or "Reset" button
- Label each slicer clearly (not just the field name)
