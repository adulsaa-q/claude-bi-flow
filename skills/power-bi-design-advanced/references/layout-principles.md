# Power BI Layout Principles

Grid system, spacing, page structure, and visual hierarchy for professional dashboards.

---

## Standard Canvas Sizes

| Format | Width × Height | Use case |
|---|---|---|
| **16:9 Widescreen** | 1280 × 720 px | Default — most screens, presentations |
| **16:9 HD** | 1920 × 1080 px | High-res displays, TV dashboards |
| **4:3** | 960 × 720 px | Older monitors, printed reports |
| **Mobile Portrait** | 360 × 640 px | Power BI mobile app |
| **Letter** | 816 × 1056 px | Paginated reports, PDF export |

Default Power BI canvas is **1280 × 720 px** (use this unless a specific format is requested).

---

## Grid System (1280 × 720)

```
Total width: 1280px
Left margin:  16px
Right margin: 16px
Usable width: 1248px

Column grid (12 columns):
  Column width: 88px
  Gutter:       16px
  Total:        12 × 88 + 11 × 16 = 1056 + 192 = 1248px ✓

Common layouts:
  Full width:    12 cols = 1248px
  Two-thirds:     8 cols = 816px
  Half:           6 cols = 616px
  One-third:      4 cols = 408px
  One-quarter:    3 cols = 296px
```

**Standard spacing:**
- Page margin (all sides): **16px**
- Gap between visuals: **8px**
- Visual title height: **24px** (included in visual bounds)
- Header bar height: **32–40px**
- Slicer bar height: **40–48px**

---

## Page Zone Layout

### Standard Executive/Operational Layout

```
Y=0    ┌─────────────────────────────────────────────────────────┐
       │  HEADER ZONE (32px)                                      │
       │  [Logo 120×32]  [Report Title]  [Last Refresh: xx:xx]   │
Y=32   ├─────────────────────────────────────────────────────────┤
       │  SLICER ZONE (48px)                                      │
       │  [Date Range ▼]  [Region ▼]  [Product ▼]  [🔄 Reset]   │
Y=80   ├─────────────────────────────────────────────────────────┤
       │  KPI ZONE (120px)                                        │
       │  [Card]  │  [Card]  │  [Card]  │  [Card]                │
Y=200  ├─────────────────────────────────────────────────────────┤
       │                     │                                    │
       │  PRIMARY VISUAL     │  SECONDARY VISUAL                  │
       │  (700px wide)       │  (528px wide)                     │
       │                     │                                    │
       │                     ├───────────────────────────────────┤
       │                     │  DETAIL / TABLE                    │
       │                     │                                    │
Y=704  └─────────────────────────────────────────────────────────┘

Bottom margin: 16px
```

### Analytical Layout (Filter-Heavy)

```
Y=0    ┌──────────┬───────────────────────────────────────────────┐
       │  FILTER  │  HEADER (40px)                                │
       │  PANEL   ├───────────────────────────────────────────────┤
       │  (200px) │  KPI ROW (100px)                              │
       │          ├───────────────────────────────────────────────┤
       │  Slicer  │  CHART ROW 1 (180px)                         │
       │  Slicer  ├───────────────────────────────────────────────┤
       │  Slicer  │  CHART ROW 2 (180px)                         │
       │          ├───────────────────────────────────────────────┤
       │          │  DETAIL TABLE (180px)                         │
Y=720  └──────────┴───────────────────────────────────────────────┘
```

---

## Visual Hierarchy Rules

### Size = Importance
- Most important visual: **largest area** (40–60% of main content zone)
- Secondary visuals: **medium** (20–30% each)
- Supporting details: **smallest** (10–15%)
- Never make all visuals the same size — creates visual monotony

### Eye Flow (F-Pattern)
Users scan in this order:
1. **Top-left first** → place most critical KPI or chart here
2. **Top-right** → second most important
3. **Left column** → then scan down
4. **Bottom right** → least important / detail

Place call-to-action slicers at the top where eyes go first.

### Title Hierarchy

```
PAGE TITLE          → 18–20px bold (text box, not visual title)
  SECTION HEADER   → 14px semibold (optional text box)
    VISUAL TITLE   → 12–13px semibold (set in theme JSON)
      DATA LABELS  → 10–11px regular
        AXIS LABELS→ 9–10px light/gray
```

Never let visual titles compete with the page title in size.

---

## Color Zone Rules

Apply consistent background colors to define zones:

```
Page background:    #FFFFFF (white)  or  #F5F5F5 (light gray)
Header zone:        #0078D4 (brand color)  + white text
Slicer zone:        #F5F5F5 (light gray)
KPI zone:           #FFFFFF (same as page, use card borders or spacing)
Main content zone:  #FFFFFF (transparent visuals)
Footer zone:        #F5F5F5 or same as page background
```

**Rule:** Use ONE accent color (brand blue) for the header only. The rest of the page should be white/near-white with data colors only inside the charts.

---

## Header Bar Design

```
┌─────────────────────────────────────────────────────────────────┐
│  [●] Logo      Report Title — Subtitle          🕐 2026-06-25  │
└─────────────────────────────────────────────────────────────────┘
Height: 40px
Background: Brand primary color (e.g., #0078D4)
Text color: #FFFFFF
Logo: Left-aligned, 120–160px wide
Title: Center or left-of-center, 16px bold white
Refresh/date: Right-aligned, 11px white
```

**Implementation in Power BI:**
- Header = Rectangle shape (full width, 40px tall, filled with brand color)
- Logo = Image visual placed on top
- Title = Text box on top
- Last Refresh date = Card visual with DAX: `"Updated: " & FORMAT(NOW(), "YYYY-MM-DD HH:MM")`

---

## KPI Card Design

Standard KPI card dimensions: **240 × 110px**

```
┌──────────────────────────────┐
│  LABEL (11px, gray)          │
│  Total Revenue               │
│                              │
│  VALUE (36px, bold)          │
│  ฿1,234,567                  │
│                              │
│  COMPARISON (10px)           │
│  ▲ 12.4% vs PY              │ ← green or red
└──────────────────────────────┘
```

**DAX for comparison line:**
```dax
KPI Comparison Line =
VAR _val = [Revenue]
VAR _py  = [Revenue PY]
VAR _pct = DIVIDE(_val - _py, ABS(_py))
RETURN
    IF(_pct >= 0,
        "▲ " & FORMAT(_pct, "0.0%") & " vs PY",
        "▼ " & FORMAT(ABS(_pct), "0.0%") & " vs PY"
    )
```

---

## Tooltip Page Design

Tooltip pages replace popup data cards with rich mini-dashboards.

**Setup:**
1. Add new page → Page Information → Allow use as tooltip ✓
2. Set canvas size: 320 × 240px
3. Keep it minimal: 1–2 visuals max
4. Same color theme as main report
5. On main visual: Format → General → Tooltip → Report page → select tooltip page

**Tooltip page layout (320×240px):**
```
┌───────────────────────────────┐
│  Title (12px bold)            │
├───────────────────────────────┤
│  [Mini chart or KPI cards]    │
│                               │
│  [Supporting context]         │
└───────────────────────────────┘
```

---

## Drillthrough Page Design

Drillthrough pages provide detail context from a summary visual.

**Rules:**
- Always add a "← Back" button (bookmarks or built-in back navigation)
- Show the filter context clearly: "Filtered by: [Category] = Electronics"
- Match the header and color theme of the originating page
- Add a breadcrumb-style title: "Sales Overview → Product Detail"

---

## Mobile Layout

Enable in View → Mobile Layout. Principles:
- Stack all visuals vertically (single column)
- KPI cards at the top
- Main chart second
- Table/detail at bottom
- Remove decorative elements that don't add value on small screens
- Font size minimum 12px for readability on phones
- Slicer becomes full-width dropdown automatically

---

## Common Layout Mistakes

| Mistake | Fix |
|---|---|
| Equal-sized visuals everywhere | Size by importance — biggest = most critical |
| Visual titles same size as page title | Page title 18px, visual title 12px |
| Slicers scattered across the page | Group all slicers in one zone (top bar or left panel) |
| No margins — visuals touch canvas edge | 16px margin all sides minimum |
| Too many visuals on one page (> 8) | Split into pages with drill-through |
| Headers with no visual separation | Use thin 1px line or color zone to separate zones |
| Color-coded zones with too many colors | Max 2 structural colors + brand color for headers |
| Inconsistent padding inside visuals | Set global padding in theme JSON |
