---
name: power-bi-svg-design
description: Advanced Power BI visual design using SVG-via-DAX technique. Use when the user wants custom visuals, pixel-perfect dashboards, SVG charts in Power BI, bullet charts, bubble charts, scatter plots with images, IBCS-style variance charts, progress rings, lollipop charts, waffle charts, sparklines, dumbbell charts, traffic lights, or wants to go beyond native Power BI visuals.
argument-hint: "[visual-type] [context]"
---

# Power BI SVG Design — Full Skill

Custom visuals via SVG generated dynamically in DAX. Read all references before coding.

## Style Inspiration

| Channel | สไตล์ | Reference หลัก |
|---|---|---|
| **powerbidesign7011** | Dark/neon, Figma backgrounds, glassmorphism, competition-grade | `references/background-system.md` |
| **HowtoPowerBI (Wyn Hopkins)** | Responsive SVG, CSS variables, IBCS, HTML Content Visual | `references/responsive-svg.md` |

---

## Quick Decision Guide

| User wants | Technique | Reference |
|---|---|---|
| Ranked bar list | Bullet / Bar | `references/basic-charts.md` → T1 |
| Circles sized by value in matrix | Bubble Matrix | `references/basic-charts.md` → T2 |
| X/Y scatter with logos/images | Scatter + Images | `references/basic-charts.md` → T3 |
| Actual vs Budget (IBCS) | IBCS Variance | `references/basic-charts.md` → T4 |
| Circular % / ring KPI | Progress Ring | `references/advanced-charts.md` → T5 |
| Mini trend line per table row | Sparkline | `references/advanced-charts.md` → T6 |
| Dot + stem chart (cleaner bars) | Lollipop | `references/advanced-charts.md` → T7 |
| 100-square % grid | Waffle Chart | `references/advanced-charts.md` → T8 |
| PY vs AC connected dots | Dumbbell | `references/advanced-charts.md` → T9 |
| Glowing status indicator | Traffic Light | `references/advanced-charts.md` → T10 |
| Gradient progress bar in table | Progress Bar | `references/advanced-charts.md` → T11 |
| ⭐ Star rating (1–5) | Star Rating SVG | `references/background-system.md` |
| 🎯 3-zone bullet chart | Full Bullet | `references/responsive-svg.md` |
| Dark panel KPI card | Dark KPI HTML | `references/background-system.md` |
| Background zones (Figma workflow) | Background System | `references/background-system.md` |
| CSS animation, glassmorphism | HTML hybrid | `references/pro-techniques.md` |
| SVG ที่ resize ได้ตาม container | Responsive SVG | `references/responsive-svg.md` |
| Media query ใน SVG | foreignObject CSS | `references/responsive-svg.md` |
| Animated ring (count-up) | CSS Animation | `references/responsive-svg.md` |

---

## Core Pattern: SVG-via-DAX

```dax
My Visual =
VAR _content =
    "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='200'>" &
    "<!-- dynamic elements -->" &
    "</svg>"
RETURN "data:image/svg+xml;utf8," & _content
```

**3 render options:**

| Method | Setup | Best for |
|---|---|---|
| **Image visual** | Paste measure into Image URL field | Full-page standalone charts |
| **HTML Content Visual + `<img>`** | `"<img src='" & [measure] & "'/>"` | Charts inside HTML layout |
| **HTML Content Visual direct** | Return `"<svg ...>"` without `data:` prefix | Animations, CSS, full control |

### Normalization Formula (required for all size/position mapping)

```dax
VAR _min_v   = MINX(ALLSELECTED('Table'), [Measure])
VAR _max_v   = MAXX(ALLSELECTED('Table'), [Measure])
VAR _px      = _px_min + (DIVIDE([Measure] - _min_v, _max_v - _min_v) * (_px_max - _px_min))
```

Use `ALLSELECTED` — not `ALL` — so ranges update with slicers.

### URL Encoding Rules (critical)

When returning `"data:image/svg+xml;utf8,..."`:

| Character | Encode as | Where |
|---|---|---|
| `#` in hex colors | `%23` | `fill='%230078D4'` |
| `%` in FORMAT output | `%25` | `FORMAT(_pct,"0%25")` |
| `&` in text | `%26` | rare, text content only |
| `<` / `>` in text | `%3C` / `%3E` | rare, text content only |

**Safe shortcut:** Use HTML Content Visual with direct SVG (no `data:` prefix) → no encoding needed, `#` works as-is.

---

## References

- Basic charts (4 techniques): `references/basic-charts.md`
- Advanced charts (7 techniques): `references/advanced-charts.md`
- Pro techniques (gradients, glow, animation, HTML): `references/pro-techniques.md`
- Background system (Figma workflow, dark mode, star rating): `references/background-system.md`
- Responsive SVG (viewBox, foreignObject, CSS vars, animation): `references/responsive-svg.md`

---

## Design Principles

**Typography**
- Labels: `font-size='11'`, `font-family='Segoe UI,sans-serif'`
- Values: `font-weight='bold'`
- Muted: `fill='%23666666'`
- Minimum legible size: 9px

**Color semantics** (consistent across all SVG visuals)
- Good / positive: `%23107C10`
- Bad / negative: `%23D13438`
- Neutral / primary: `%230078D4`
- Warning: `%23FF8C00`
- Background track: `%23F0F0F0`
- Text dark: `%23252423`
- Text muted: `%23888888`

**Spacing**
- Padding inside SVG: 8px minimum
- Row height in lists: multiples of 30px
- Text offset from bar edge: 5px

**Performance**
- Pre-calculate expensive measures in `VAR` before `CONCATENATEX`
- Use `CALCULATETABLE` to pre-filter before iterating
- Keep Base64 images ≤ 5KB per image
- Avoid nested `FILTER()` inside iterator — use `CALCULATE` with filter args instead
