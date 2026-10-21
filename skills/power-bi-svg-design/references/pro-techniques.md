# Pro SVG Techniques

The difference between "good" and "YouTube-grade" Power BI visuals.

---

## 1. SVG `<defs>` — Reusable Gradients & Filters

Define once, reference many times inside the same SVG. Always place `<defs>` as the first child of `<svg>`.

### Linear Gradient (horizontal fill)

```dax
-- In DAX string:
"<defs>" &
    "<linearGradient id='bar-fill' x1='0' y1='0' x2='1' y2='0'>" &
        "<stop offset='0%25'   stop-color='%230078D4' stop-opacity='0.6'/>" &
        "<stop offset='100%25' stop-color='%230078D4' stop-opacity='1'/>" &
    "</linearGradient>" &
"</defs>" &
"<rect ... fill='url(%23bar-fill)'/>"
```

### Radial Gradient (sphere/bubble effect)

```dax
"<defs>" &
    "<radialGradient id='sphere' cx='35%25' cy='30%25' r='65%25'>" &
        "<stop offset='0%25'   stop-color='white'     stop-opacity='0.6'/>" &
        "<stop offset='60%25'  stop-color='%230078D4' stop-opacity='0.9'/>" &
        "<stop offset='100%25' stop-color='%23004578' stop-opacity='1'/>" &
    "</radialGradient>" &
"</defs>" &
"<circle ... fill='url(%23sphere)'/>"
```

### Glow Filter (feGaussianBlur)

```dax
"<defs>" &
    "<filter id='glow' x='-60%25' y='-60%25' width='220%25' height='220%25'>" &
        "<feGaussianBlur in='SourceGraphic' stdDeviation='4' result='blur'/>" &
        "<feMerge>" &
            "<feMergeNode in='blur'/>" &          -- blurred glow layer
            "<feMergeNode in='SourceGraphic'/>" & -- original on top
        "</feMerge>" &
    "</filter>" &
"</defs>" &
"<circle ... filter='url(%23glow)'/>"
```

**Tip:** `stdDeviation` controls glow radius. 2–3 = subtle. 5–8 = dramatic neon.

### Drop Shadow Filter

```dax
"<defs>" &
    "<filter id='shadow' x='-20%25' y='-20%25' width='140%25' height='140%25'>" &
        "<feDropShadow dx='2' dy='2' stdDeviation='3' flood-color='%23000000' flood-opacity='0.2'/>" &
    "</filter>" &
"</defs>" &
"<rect ... filter='url(%23shadow)'/>"
```

---

## 2. `viewBox` — Responsive Scaling

Makes the SVG scale to fit any visual size without pixel math.

```dax
-- Instead of fixed width/height:
"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 200' " &
    "preserveAspectRatio='xMidYMid meet'>" &
-- Draw everything in 0-400 x 0-200 space
-- Power BI scales it to the visual container automatically
"</svg>"
```

**When to use:** Full-page charts that should fill the visual regardless of container size. For matrix cells, use fixed px sizes instead.

---

## 3. HTML Content Visual — CSS Animations

The HTML Content Visual can render raw HTML+CSS+SVG. Return the measure as a full HTML string (no `data:` prefix).

### Animated Counter (number counts up on load)

```dax
Animated KPI =
VAR _val   = FORMAT([Sales] / 1000000, "0.0")
VAR _label = "Total Revenue"
VAR _color = "%230078D4"

RETURN
"<div style='font-family:Segoe UI,sans-serif;padding:20px;'>" &
"<style>" &
"@keyframes countup{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}" &
".kpi-val{animation:countup 0.6s ease forwards;}" &
"</style>" &
"<div style='font-size:11px;color:%23888;text-transform:uppercase;letter-spacing:1px;'>" & _label & "</div>" &
"<div class='kpi-val' style='font-size:40px;font-weight:300;color:" & _color & ";margin:6px 0;'>$" & _val & "M</div>" &
"</div>"
```

### Glassmorphism Card (frosted glass effect)

```dax
Glass Card HTML =
VAR _title = "Revenue"
VAR _val   = FORMAT([Sales] / 1000000, "#,##0.0") & "M"
VAR _delta = FORMAT(DIVIDE([Sales] - [Sales PY], [Sales PY]), "+0.0%25;-0.0%25")
VAR _is_up = [Sales] >= [Sales PY]
VAR _arrow = IF(_is_up, "▲", "▼")
VAR _d_col = IF(_is_up, "%2300B050", "%23ee4444")

RETURN
"<div style='" &
    "font-family:Segoe UI,sans-serif;" &
    "background:rgba(255,255,255,0.15);" &
    "backdrop-filter:blur(12px);" &
    "-webkit-backdrop-filter:blur(12px);" &
    "border:1px solid rgba(255,255,255,0.3);" &
    "border-radius:16px;" &
    "padding:20px 24px;" &
    "box-shadow:0 4px 24px rgba(0,0,0,0.08);" &
"'>" &
"<div style='font-size:11px;color:%23888;letter-spacing:0.5px;'>" & _title & "</div>" &
"<div style='font-size:36px;font-weight:300;color:%23252423;margin:8px 0 4px;'>$" & _val & "</div>" &
"<div style='font-size:12px;color:" & _d_col & ";'>" & _arrow & " " & _delta & " vs PY</div>" &
"</div>"
```

**Note:** `backdrop-filter` (glassmorphism) requires the report background to have actual content/image behind the card. Works best on dashboard with background image.

### Dark Mode Neon Card

```dax
Neon KPI =
VAR _val   = FORMAT([Sales] / 1000000, "0.0") & "M"
VAR _pct   = FORMAT(DIVIDE([Sales], [Sales Target]), "0%25")
VAR _r     = 38  VAR _cx = 60  VAR _cy = 60
VAR _circ  = 2 * 3.14159265 * _r
VAR _dash  = MIN(DIVIDE([Sales], [Sales Target]), 1) * _circ
VAR _gap   = _circ - _dash

RETURN
"<div style='background:%23111827;border-radius:12px;padding:20px;font-family:Segoe UI,sans-serif;'>" &
"<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' style='float:left;margin-right:16px;'>" &
"<defs>" &
    "<filter id='n'><feGaussianBlur stdDeviation='3' result='b'/>" &
        "<feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge>" &
    "</filter>" &
"</defs>" &
"<circle cx='" & _cx & "' cy='" & _cy & "' r='" & _r & "' fill='none' stroke='%231a2744' stroke-width='10'/>" &
"<circle cx='" & _cx & "' cy='" & _cy & "' r='" & _r & "' fill='none' stroke='%2338bdf8' stroke-width='10'" &
    " stroke-dasharray='" & FORMAT(_dash,"0.0") & " " & FORMAT(_gap,"0.0") & "'" &
    " stroke-linecap='round' filter='url(%23n)'" &
    " transform='rotate(-90 " & _cx & " " & _cy & ")'/>" &
"<text x='" & _cx & "' y='" & (_cy+6) & "' text-anchor='middle' font-size='20' font-weight='bold' fill='%2338bdf8'>" & _pct & "</text>" &
"</svg>" &
"<div style='color:%23e5e7eb;font-size:11px;letter-spacing:1px;margin-top:8px;'>TOTAL REVENUE</div>" &
"<div style='color:white;font-size:32px;font-weight:200;margin:4px 0;'>$" & _val & "</div>" &
"<div style='color:%2338bdf8;font-size:11px;'>▲ 12.4% vs PY</div>" &
"</div>"
```

---

## 4. Multi-Column HTML Layout

HTML Content Visual supports flexbox — use it to arrange SVG visuals side by side.

```dax
Side-by-Side KPIs =
VAR _rev  = [Sales Measure SVG]      -- returns SVG string
VAR _cost = [Cost Measure SVG]
VAR _profit = [Profit Measure SVG]

RETURN
"<div style='display:flex;gap:12px;font-family:Segoe UI,sans-serif;'>" &
    "<div style='flex:1;'><img src='" & _rev    & "' style='width:100%;'/></div>" &
    "<div style='flex:1;'><img src='" & _cost   & "' style='width:100%;'/></div>" &
    "<div style='flex:1;'><img src='" & _profit & "' style='width:100%;'/></div>" &
"</div>"
```

---

## 5. Performance Optimization Patterns

### Pre-filter before CONCATENATEX

```dax
-- Slow: FILTER inside the loop
BAD =
CONCATENATEX(
    FILTER(ALL(Products), [Sales] > 1000),  -- filters every iteration
    ...
)

-- Fast: CALCULATETABLE pre-filters once
GOOD =
VAR _filtered = CALCULATETABLE(ALL(Products), [Sales] > 1000)
RETURN CONCATENATEX(_filtered, ...)
```

### Cache heavy calculations outside the loop

```dax
-- Calculate axis bounds ONCE, before entering CONCATENATEX
VAR _min_v = MINX(ALLSELECTED('Table'), [Measure])
VAR _max_v = MAXX(ALLSELECTED('Table'), [Measure])
VAR _range = _max_v - _min_v    -- pre-computed

VAR _items =
    CONCATENATEX(
        ALLSELECTED('Table'),
        -- _min_v, _max_v, _range are captured as closures — fast
        VAR _normalized = DIVIDE([Measure] - _min_v, _range)
        RETURN ...,
        ""
    )
```

### Limit rows for complex SVG

```dax
-- Use TOPN to cap iterations — complex SVG × 500 rows = slow render
VAR _data = TOPN(20, ALLSELECTED('Table'), [Measure], DESC)
RETURN CONCATENATEX(_data, ..., "")
```

---

## 6. Common Encoding Issues & Fixes

| Problem | Cause | Fix |
|---|---|---|
| Colors show as literal `%23FF0000` | Double-encoded | Use `#` directly in HTML Content Visual (non-data: URI) |
| Glow filter not showing | `url(#glow)` not encoded | Use `url(%23glow)` in data: URI mode |
| `%` in FORMAT shows as `%25` | Over-encoding | Use `FORMAT(_val,"0%")` directly in HTML mode; use `"0%25"` in data: URI mode |
| Gradient not rendering | `id` conflict across matrix rows | Make gradient `id` unique per row: `"id='g" & [RowKey] & "'"` |
| SVG too small in matrix | Fixed px too small for cell | Use `viewBox` with `width='100%25'` or set visual column width to match |
| Apostrophe breaks DAX string | `'` in text data | Replace with `"` in SVG attributes, or use `SUBSTITUTE([col],"'","&#39;")` |

### Unique ID pattern for matrix cells

When the same measure renders in multiple matrix rows, gradient/filter IDs collide. Make them unique:

```dax
VAR _id_suffix = SUBSTITUTE(SELECTEDVALUE(Products[Name]), " ", "_")
VAR _grad_id   = "g_" & _id_suffix

-- In defs:
"<linearGradient id='" & _grad_id & "' ...>"

-- In usage:
"fill='url(%23" & _grad_id & ")'"
```
