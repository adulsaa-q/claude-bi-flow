---
name: power-bi-design-advanced
description: Advanced Power BI dashboard design — covers IBCS notation standards, Themes JSON authoring, visual selection principles, layout design, and SVG-via-DAX custom visuals. Use when the user wants to design a professional-grade or competition-level Power BI dashboard, asks about IBCS, wants to create a theme JSON file, wants pixel-perfect design, or wants help choosing the right visual for their data.
argument-hint: "[design-task] [context]"
---

# Power BI Advanced Design

Professional-grade dashboard design combining IBCS standards, Power BI Themes JSON, visual selection principles, and custom SVG visuals.

**Sources:**
- Dashboard-Design/Power-BI-Design-Files (SVG techniques, examples)
- Microsoft Learn: Power BI Themes JSON schema
- IBCS Association: SUCCESS framework (CC BY-SA 4.0)
- Microsoft: Design effective reports learning path

## When to Use

- Design a full dashboard from scratch (layout, color, typography)
- Author or improve a Power BI theme JSON file
- Choose the right chart type for specific data
- Apply IBCS business communication standards
- Create custom SVG visuals beyond native Power BI
- Audit an existing dashboard for design quality

## Sub-skill Routing

| Task | Reference |
|---|---|
| IBCS notation, SUCCESS rules, semantic colors | `references/ibcs-notation.md` |
| Theme JSON — colors, fonts, visual styles | `references/theme-json-schema.md` |
| Which chart type to use | `references/visual-selection.md` |
| Layout grid, spacing, page structure | `references/layout-principles.md` |
| SVG bullet chart, bubble, scatter, variance | SVG SKILL: `power-bi-svg-design` |

---

## Step 1: Define the Dashboard Purpose

Before designing, classify the dashboard type — this determines layout and visual choices:

| Type | Audience | Update frequency | Design priority |
|---|---|---|---|
| **Operational** | Front-line staff | Real-time / daily | Clarity, alerts, current status |
| **Analytical** | Data analysts | Weekly / on-demand | Exploration, filters, drill-through |
| **Executive** | Leadership | Monthly | Summary KPIs, trends, comparison |
| **Tactical** | Team leads | Daily / weekly | Performance vs target, variance |

---

## Step 2: IBCS Design (Business Reports)

Read `references/ibcs-notation.md` for full rules. Core rules:

- **AC** (Actual) = solid black `#1A1A1A`
- **BU** (Budget) = gray outline only `#888888`
- **PY** (Prior Year) = light gray `#AAAAAA`
- **FC** (Forecast) = hatched / dashed
- **Positive delta** = green `#107C10`
- **Negative delta** = red `#D13438`
- No 3D, no gradients, no decorative colors
- Time always on X-axis (left → right = past → future)

---

## Step 3: Theme JSON

Read `references/theme-json-schema.md` for full schema. Minimal professional theme:

```json
{
  "name": "Corporate Clean",
  "dataColors": [
    "#0078D4", "#107C10", "#D13438", "#FF8C00",
    "#6B69D6", "#038387", "#C239B3", "#744DA9"
  ],
  "good":    "#107C10",
  "neutral": "#FFB900",
  "bad":     "#D13438",
  "maximum": "#0078D4",
  "center":  "#FFB900",
  "minimum": "#DEEFFF",
  "null":    "#BDBDBD",
  "firstLevelElements":    "#252423",
  "secondLevelElements":   "#605E5C",
  "thirdLevelElements":    "#F3F2F1",
  "fourthLevelElements":   "#B3B0AD",
  "background":            "#FFFFFF",
  "secondaryBackground":   "#F5F5F5",
  "tableAccent":           "#0078D4",
  "textClasses": {
    "callout": { "fontSize": 36, "fontFace": "Segoe UI Light", "color": "#252423" },
    "title":   { "fontSize": 14, "fontFace": "Segoe UI Semibold", "color": "#252423" },
    "header":  { "fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#252423" },
    "label":   { "fontSize": 11, "fontFace": "Segoe UI", "color": "#252423" }
  }
}
```

---

## Step 4: Visual Selection

Read `references/visual-selection.md` for the full chart chooser. Quick reference:

| Data question | Best visual |
|---|---|
| Comparison across categories | Clustered bar / column chart |
| Trend over time | Line chart |
| Part of a whole (≤5 segments) | Donut chart |
| Part of a whole (>5 segments) | Stacked bar |
| Actual vs target | Bullet chart (SVG) or gauge |
| Distribution | Histogram or box plot |
| Correlation between 2 metrics | Scatter chart |
| Geography | Map or filled map |
| High-level KPI | Card visual |
| Waterfall / bridge | Waterfall chart |
| Ranking with magnitude | Horizontal bar chart |

---

## Step 5: Layout

Read `references/layout-principles.md` for full grid system. Standard report layout:

```
┌─────────────────────────────────────────────────────────┐
│  HEADER BAR  │  Report Title    │  Logo  │  Last Refresh │  32px
├──────────────────────────────────────────────────────────┤
│  SLICER ROW  │  Date  │  Region  │  Category  │  Reset   │  48px
├─────────────────────────────────────────────────────────┤
│  KPI ROW  │  [Card]  │  [Card]  │  [Card]  │  [Card]    │  120px
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MAIN VISUALS                                            │  variable
│  Left col 60%          │  Right col 40%                  │
│                        │                                 │
│  [Primary chart]       │  [Secondary chart]              │
│                        │  [Table / detail]               │
└─────────────────────────────────────────────────────────┘

Margins: 16px all sides
Spacing between visuals: 8px
Title height: 24px per visual
```

---

## Step 6: SVG Custom Visuals

For custom visuals beyond native Power BI, use the companion skill:

```
/power-bi-svg-design
```

Covers: Dynamic Bullet Points, Matrix Bubble Chart, Scatter Plot with Images, IBCS Variance Chart.

---

## Design Quality Checklist

Before delivering a dashboard, verify:

- [ ] Color palette ≤ 5 colors + black/white/gray
- [ ] Semantic colors consistent (green=good, red=bad)
- [ ] No 3D charts anywhere
- [ ] No pie charts with > 5 segments
- [ ] All axis titles present and readable
- [ ] KPI cards have clear labels (not just numbers)
- [ ] Slicers positioned consistently (top or left)
- [ ] Mobile layout tested if required
- [ ] Data labels not overlapping
- [ ] Title hierarchy clear: Page title > Section > Visual title
- [ ] Theme JSON applied (not manually overriding colors per-visual)
- [ ] "Reset filters" button on every page
