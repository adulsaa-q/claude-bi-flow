# Power BI Theme JSON Schema Reference

Source: Microsoft Learn — learn.microsoft.com/power-bi/create-reports/report-themes-create-custom
Schema file: github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema

---

## Full Structure

```json
{
  "name": "Theme Name",           // REQUIRED — only mandatory field
  "$schema": "reportThemeSchema.json",

  // === 1. DATA COLORS ===
  "dataColors": [],               // ordered list of hex colors for series

  // === 2. STATUS COLORS ===
  "good":    "#hex",              // KPI/waterfall positive
  "neutral": "#hex",              // KPI neutral
  "bad":     "#hex",              // KPI/waterfall negative
  "maximum": "#hex",              // conditional formatting max
  "center":  "#hex",              // conditional formatting center
  "minimum": "#hex",              // conditional formatting min
  "null":    "#hex",              // null value color

  // === 3. STRUCTURAL COLORS ===
  "firstLevelElements":   "#hex", // primary text, trend lines, card values
  "secondLevelElements":  "#hex", // secondary text, legend, axis labels
  "thirdLevelElements":   "#hex", // gridlines, gauge arc background
  "fourthLevelElements":  "#hex", // legend dimmed, funnel stroke
  "background":           "#hex", // visual backgrounds, button fill
  "secondaryBackground":  "#hex", // table grid outline, shape map default
  "tableAccent":          "#hex", // table/matrix accent line

  // === 4. TEXT CLASSES ===
  "textClasses": { ... },

  // === 5. VISUAL STYLES ===
  "visualStyles": { ... }
}
```

---

## 1. Data Colors

Ordered list — first color = first series, second = second series, etc.

```json
"dataColors": [
  "#0078D4",   // Blue — primary
  "#107C10",   // Green
  "#D13438",   // Red
  "#FF8C00",   // Orange
  "#6B69D6",   // Purple
  "#038387",   // Teal
  "#C239B3",   // Magenta
  "#744DA9",   // Dark purple
  "#0099BC",   // Light blue
  "#E81123"    // Bright red
]
```

Power BI auto-generates additional colors (adjusting saturation/hue) when all colors are used.

---

## 2. Structural Colors

6 color classes that control the entire visual framework:

| Property | Also called | Controls |
|---|---|---|
| `firstLevelElements` | `foreground` | Primary text, trend lines, card data labels, KPI text |
| `secondLevelElements` | `foregroundNeutralSecondary` | Axis labels, legend text, slicer items |
| `thirdLevelElements` | `backgroundLight` | Gridlines, gauge arc, table grid |
| `fourthLevelElements` | `foregroundNeutralTertiary` | Dimmed legend, disabled buttons |
| `background` | — | Label backgrounds inside data points, button fill |
| `secondaryBackground` | `backgroundNeutral` | Table grid outline, ribbon chart fill |
| `tableAccent` | — | Table/matrix accent line |

**Dark theme pattern:**
```json
"firstLevelElements":  "#FFFFFF",   // white text
"secondLevelElements": "#C8C6C4",   // light gray secondary
"thirdLevelElements":  "#323130",   // dark gridlines
"background":          "#201F1E",   // dark background
"secondaryBackground": "#3B3A39"    // slightly lighter
```

---

## 3. Text Classes

4 primary classes control all text in the report. Secondary classes inherit automatically.

```json
"textClasses": {
  "callout": {
    "fontSize":  45,
    "fontFace":  "Segoe UI Light",
    "color":     "#252423"
  },
  "title": {
    "fontSize":  14,
    "fontFace":  "Segoe UI Semibold",
    "color":     "#252423"
  },
  "header": {
    "fontSize":  12,
    "fontFace":  "Segoe UI Semibold",
    "color":     "#252423"
  },
  "label": {
    "fontSize":  11,
    "fontFace":  "Segoe UI",
    "color":     "#252423"
  }
}
```

| Primary class | Controls | Default |
|---|---|---|
| `callout` | Card data labels, KPI values | DIN 45pt |
| `title` | Axis titles, multi-row card title | DIN 12pt |
| `header` | Key influencers headers | Segoe UI Semibold 12pt |
| `label` | Table/matrix columns, values | Segoe UI 10pt |

Secondary classes (auto-inherited, override only if needed):
- `largeTitle` (14pt) — visual title
- `largeLabel` (12pt) — multi-row card data labels
- `smallLabel` (9pt) — reference line labels, slicer date range
- `lightLabel` (#605E5C) — legend text, funnel labels, slicer items
- `boldLabel` (Segoe UI Bold) — matrix subtotals, table totals
- `smallLightLabel` (#605E5C 9pt) — data labels, value axis labels

---

## 4. Visual Styles

Target specific visual types. Structure:

```json
"visualStyles": {
  "<visualName>": {
    "*": {                          // default style ("*" = all presets)
      "<cardName>": [{
        "<propertyName>": <value>
      }]
    },
    "My Preset Name": { ... }       // named style preset
  }
}
```

### Global (apply to ALL visuals)

```json
"visualStyles": {
  "*": {
    "*": {
      "*": [{ "wordWrap": true }],
      "title": [{
        "show":        true,
        "fontSize":    14,
        "fontBold":    true,
        "fontColor":   { "solid": { "color": "#252423" } },
        "background":  { "solid": { "color": "#FFFFFF" } }
      }],
      "background": [{
        "show":        false
      }],
      "border": [{
        "show":        false
      }],
      "dropShadow": [{
        "show":        false
      }]
    }
  }
}
```

### Visual Names Reference

| Power BI Visual | Theme `visualName` |
|---|---|
| Clustered bar chart | `barChart` |
| Clustered column chart | `columnChart` |
| Stacked bar chart | `stackedBarChart` |
| Stacked column chart | `stackedColumnChart` |
| Line chart | `lineChart` |
| Area chart | `areaChart` |
| Combo chart | `lineClusteredColumnComboChart` |
| Scatter chart | `scatterChart` |
| Pie chart | `pieChart` |
| Donut chart | `donutChart` |
| Treemap | `treemap` |
| Waterfall chart | `waterfallChart` |
| Funnel chart | `funnel` |
| Gauge | `gauge` |
| Card | `card` |
| Multi-row card | `multiRowCard` |
| KPI | `kpi` |
| Table | `tableEx` |
| Matrix | `matrix` |
| Slicer | `slicer` |
| Map | `map` |
| Filled map | `filledMap` |
| Shape map | `shapeMap` |
| Button | `button` |

### Common Visual Formatting Examples

**Remove gridlines from all charts:**
```json
"visualStyles": {
  "*": {
    "*": {
      "categoryAxis": [{ "gridlineShow": false }],
      "valueAxis":    [{ "gridlineStyle": "dotted", "gridlineColor": { "solid": { "color": "#F0F0F0" } } }]
    }
  }
}
```

**Card visual — large clean number:**
```json
"visualStyles": {
  "card": {
    "*": {
      "dataLabel":  [{ "fontSize": 36, "fontBold": false, "color": { "solid": { "color": "#252423" } } }],
      "categoryLabel": [{ "fontSize": 11, "color": { "solid": { "color": "#605E5C" } } }],
      "background": [{ "show": false }],
      "border":     [{ "show": false }]
    }
  }
}
```

**Matrix — clean table style:**
```json
"visualStyles": {
  "matrix": {
    "*": {
      "grid":         [{ "gridVertical": false, "rowPadding": 4 }],
      "columnHeaders":[{ "fontBold": true, "fontSize": 11, "background": { "solid": { "color": "#F5F5F5" } } }],
      "values":       [{ "fontSize": 11 }],
      "background":   [{ "show": false }],
      "border":       [{ "show": false }]
    }
  }
}
```

**Slicer — clean dropdown style:**
```json
"visualStyles": {
  "slicer": {
    "*": {
      "selection":    [{ "singleSelect": false }],
      "header":       [{ "show": true, "fontSize": 11, "fontBold": true }],
      "items":        [{ "fontSize": 11 }],
      "background":   [{ "show": false }],
      "border":       [{ "show": false }]
    }
  }
}
```

---

## Complete Corporate Theme Template

```json
{
  "name": "Corporate Professional",
  "$schema": "reportThemeSchema.json",

  "dataColors": [
    "#0078D4", "#107C10", "#FF8C00", "#6B69D6",
    "#038387", "#C239B3", "#744DA9", "#D13438"
  ],

  "good":    "#107C10",
  "neutral": "#FFB900",
  "bad":     "#D13438",
  "maximum": "#0078D4",
  "center":  "#FFB900",
  "minimum": "#DEEFFF",
  "null":    "#BDBDBD",

  "firstLevelElements":  "#252423",
  "secondLevelElements": "#605E5C",
  "thirdLevelElements":  "#F3F2F1",
  "fourthLevelElements": "#B3B0AD",
  "background":          "#FFFFFF",
  "secondaryBackground": "#F5F5F5",
  "tableAccent":         "#0078D4",

  "textClasses": {
    "callout": { "fontSize": 36, "fontFace": "Segoe UI Light",    "color": "#252423" },
    "title":   { "fontSize": 14, "fontFace": "Segoe UI Semibold", "color": "#252423" },
    "header":  { "fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#252423" },
    "label":   { "fontSize": 11, "fontFace": "Segoe UI",          "color": "#252423" }
  },

  "visualStyles": {
    "*": {
      "*": {
        "background":  [{ "show": false }],
        "border":      [{ "show": false }],
        "dropShadow":  [{ "show": false }],
        "title": [{
          "fontSize":  13,
          "fontBold":  true,
          "fontColor": { "solid": { "color": "#252423" } }
        }],
        "valueAxis": [{
          "gridlineStyle": "dotted",
          "gridlineColor": { "solid": { "color": "#EEEEEE" } }
        }]
      }
    },
    "card": {
      "*": {
        "dataLabel":     [{ "fontSize": 36, "fontBold": false }],
        "categoryLabel": [{ "fontSize": 11, "color": { "solid": { "color": "#605E5C" } } }]
      }
    },
    "matrix": {
      "*": {
        "grid":          [{ "gridVertical": false, "rowPadding": 6 }],
        "columnHeaders": [{ "fontBold": true, "background": { "solid": { "color": "#F5F5F5" } } }]
      }
    }
  }
}
```

---

## Tips

- Use `"$schema": "reportThemeSchema.json"` with VS Code for autocomplete
- Export any report's current theme via View → Themes → Save current theme
- Download the full schema: github.com/microsoft/powerbi-desktop-samples → Report Theme JSON Schema
- Use Semantic Link Labs to apply themes programmatically across multiple reports
