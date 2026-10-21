# Responsive SVG — Wyn Hopkins (HowtoPowerBI) Style

เทคนิคขั้นสูงจากช่อง HowtoPowerBI — SVG ที่ปรับขนาดและรูปแบบตาม container จริง
Source: powerofbi.org, Wyn Hopkins DAX techniques

---

## ทำไม Responsive SVG ถึงสำคัญ

ปัญหา SVG ปกติ: กำหนด `width='400' height='200'` ตายตัว → ถ้า visual ถูก resize → ล้น หรือ เล็กเกิน
Responsive SVG: ใช้ `viewBox` + CSS media queries → scale ได้เองตาม container size

---

## Method 1: viewBox (พื้นฐาน responsive)

```dax
Responsive Bar SVG =
-- ไม่ใส่ width/height ตายตัว — ใช้ viewBox แทน
-- SVG จะ scale เต็ม container โดยอัตโนมัติ
VAR _items = "..." -- elements ทั้งหมดใน 0-500 x 0-300 space

RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' " &
    "viewBox='0 0 500 300' " &
    "preserveAspectRatio='xMidYMid meet'>" &
_items &
"</svg>"
```

**Behavior:**
- `xMidYMid meet` → scale proportionally, center ทั้ง X และ Y
- `xMinYMin meet` → scale proportionally, align top-left
- `none` → stretch เต็ม container (อาจ distort)

---

## Method 2: `<foreignObject>` + CSS Variables (Wyn Hopkins technique)

เทคนิค advance ที่สุด: ใส่ `<foreignObject>` ไว้ใน SVG เพื่อ inject CSS ที่ SVG elements อื่นอ่านได้

```dax
-- ใช้ใน HTML Content Visual เท่านั้น (ไม่ใช้ data: URI)
Responsive IBCS SVG =
VAR _ac     = [Sales AC]
VAR _bu     = [Sales BU]
VAR _delta  = _ac - _bu
VAR _is_pos = _delta >= 0
VAR _pct    = DIVIDE(_delta, ABS(_bu))

RETURN
"<svg xmlns='http://www.w3.org/2000/svg' " &
    "xmlns:xhtml='http://www.w3.org/1999/xhtml' " &
    "width='100%' height='100%' viewBox='0 0 400 80'>" &

-- ① inject CSS เข้า SVG ผ่าน foreignObject
"<foreignObject width='1' height='1' style='overflow:visible'>" &
    "<xhtml:style>" &
        ":root {" &
            "--ac-color: " & IF(_is_pos, "#107C10", "#D13438") & ";" &
            "--bar-w: " & FORMAT(DIVIDE(_ac, [Sales Max]) * 320, "0") & "px;" &
            "--bu-x: " & FORMAT(DIVIDE(_bu, [Sales Max]) * 320 + 60, "0") & "px;" &
        "}" &
        -- Media query: เมื่อ container แคบกว่า 300px ซ่อน label
        "@media (max-width: 300px) { .label { display:none; } }" &
        "@media (max-height: 60px)  { .sub-label { display:none; } }" &
    "</xhtml:style>" &
"</foreignObject>" &

-- ② SVG elements ใช้ CSS variables ผ่าน style attribute
"<rect x='60' y='20' width='0' height='20' style='width:var(--bar-w);fill:%231A1A1A;'/>" &
"<rect style='x:var(--bu-x)' y='14' width='3' height='32' fill='%23888888'/>" &
"<text class='label' x='54' y='34' text-anchor='end' font-size='10' fill='%23333'>AC</text>" &
"<text class='sub-label' x='60' y='56' font-size='9' style='fill:var(--ac-color)'>" &
    (IF(_is_pos, "▲ +", "▼ ")) & FORMAT(ABS(_pct), "0.0%") & " vs BU" &
"</text>" &
"</svg>"
```

**ทำไมใช้ CSS variables:**
- ค่าจาก DAX ถูก inject เป็น CSS variable ครั้งเดียวใน `:root`
- SVG elements ทั้งหมดใช้ variable ร่วมกัน → เปลี่ยนที่เดียว update ทุกที่
- Media query ทำงานได้ใน foreignObject → responsive จริงๆ

---

## Method 3: Responsive Sparkline (adaptive detail level)

ซ่อน/แสดง element ตามขนาด container จริง:

```dax
-- HTML Content Visual — ส่งคืน HTML string โดยตรง
Adaptive Sparkline =
VAR _pts = "..." -- polyline points string

RETURN
"<svg xmlns='http://www.w3.org/2000/svg' " &
    "xmlns:xhtml='http://www.w3.org/1999/xhtml' " &
    "width='100%' height='100%' viewBox='0 0 200 60'>" &

"<foreignObject width='1' height='1' style='overflow:visible'>" &
    "<xhtml:style>" &
        -- แสดง dot เฉพาะตอน container สูงพอ
        "@media (max-height: 50px) { .end-dot { display:none } }" &
        -- ซ่อน labels ตอนแคบ
        "@media (max-width: 150px) { .axis-label { display:none } }" &
        -- เปลี่ยนสี stroke ตาม height
        "@media (min-height: 80px) { .spark-line { stroke-width:2.5 } }" &
    "</xhtml:style>" &
"</foreignObject>" &

"<polyline class='spark-line' points='" & _pts & "' fill='none' stroke='%230078D4' stroke-width='1.5'/>" &
"<circle class='end-dot' cx='195' cy='30' r='4' fill='%230078D4'/>" &
"<text class='axis-label' x='0' y='12' font-size='8' fill='%23888'>HIGH</text>" &
"<text class='axis-label' x='0' y='58' font-size='8' fill='%23888'>LOW</text>" &
"</svg>"
```

---

## Method 4: Full Bullet Chart (3-zone, IBCS+ style)

HowtoPowerBI นิยม bullet chart แบบมี 3 zones (poor/ok/good) + bar + target marker:

```dax
Full Bullet Chart SVG =
VAR _ac       = [Sales]
VAR _target   = [Sales Target]
VAR _max_ref  = [Sales Reference Max]

-- Normalize to pixel range
VAR _bar_w    = 320
VAR _x_start  = 80
VAR _h        = 48

VAR _ac_px    = DIVIDE(_ac,     _max_ref) * _bar_w
VAR _tg_px    = DIVIDE(_target, _max_ref) * _bar_w

-- 3 quality zones (poor=0-50%, ok=50-80%, good=80-100% of max)
VAR _z1_w     = _bar_w * 0.50   -- poor zone
VAR _z2_w     = _bar_w * 0.30   -- ok zone
VAR _z3_w     = _bar_w * 0.20   -- good zone

VAR _color    = IF(_ac >= _target, "%23107C10", IF(_ac >= _target * 0.8, "%23FF8C00", "%23D13438"))

RETURN
"data:image/svg+xml;utf8," &
"<svg xmlns='http://www.w3.org/2000/svg' width='440' height='" & _h & "'>" &

-- Zone backgrounds (light → medium → dark gray)
"<rect x='" & _x_start & "' y='14' width='" & FORMAT(_z1_w,"0") & "' height='20' fill='%23E5E7EB'/>" &
"<rect x='" & FORMAT(_x_start + _z1_w,"0") & "' y='14' width='" & FORMAT(_z2_w,"0") & "' height='20' fill='%23D1D5DB'/>" &
"<rect x='" & FORMAT(_x_start + _z1_w + _z2_w,"0") & "' y='14' width='" & FORMAT(_z3_w,"0") & "' height='20' fill='%23BDBDBD'/>" &

-- AC performance bar (narrow, centered vertically)
"<rect x='" & _x_start & "' y='18' width='" & FORMAT(_ac_px,"0") & "' height='12' fill='%231A1A1A' rx='1'/>" &

-- Target marker (thick vertical line)
"<rect x='" & FORMAT(_x_start + _tg_px - 2,"0") & "' y='10' width='4' height='28' fill='%23374151'/>" &

-- Labels
"<text x='" & (_x_start - 6) & "' y='27' text-anchor='end' font-size='10' font-weight='bold' fill='%23374151'>" &
    SELECTEDVALUE(Products[Category], "Category") & "</text>" &
"<text x='" & FORMAT(_x_start + _ac_px + 6, "0") & "' y='27' font-size='10' fill='%231A1A1A'>" &
    FORMAT(_ac, "#,##0") & "</text>" &
"<text x='" & FORMAT(_x_start + _tg_px, "0") & "' y='44' text-anchor='middle' font-size='8' fill='%236B7280'>" &
    "Target: " & FORMAT(_target, "#,##0") & "</text>" &

"</svg>"
```

**Usage:** Place in Matrix — rows = categories, values = this measure. Each row = one bullet chart.

---

## Method 5: CSS Animation ใน HTML Content Visual

HowtoPowerBI ใช้ animation เพื่อ draw attention ไปที่ KPI สำคัญ:

```dax
Animated Progress Ring =
VAR _pct   = DIVIDE([Sales], [Sales Target])
VAR _r     = 45
VAR _circ  = 2 * 3.14159265 * _r
VAR _dash  = MIN(_pct, 1) * _circ
VAR _color = IF(_pct >= 1, "#34D399", IF(_pct >= 0.75, "#38BDF8", "#F87171"))

RETURN
-- ใช้ HTML Content Visual โดยตรง (ไม่ใช้ data: URI)
"<div style='display:flex;align-items:center;justify-content:center;height:100%;background:#1A1D2E;border-radius:12px;'>" &
"<style>" &
"@keyframes ring-fill {" &
    "from { stroke-dasharray: 0 " & FORMAT(_circ,"0.0") & "; }" &
    "to   { stroke-dasharray: " & FORMAT(_dash,"0.0") & " " & FORMAT(_circ - _dash,"0.0") & "; }" &
"}" &
".ring-progress { animation: ring-fill 1.2s cubic-bezier(0.4,0,0.2,1) forwards; }" &
"</style>" &
"<svg width='120' height='120'>" &
"<circle cx='60' cy='60' r='" & _r & "' fill='none' stroke='rgba(255,255,255,0.1)' stroke-width='10'/>" &
"<circle class='ring-progress' cx='60' cy='60' r='" & _r &
    "' fill='none' stroke='" & _color & "' stroke-width='10'" &
    " stroke-dasharray='0 " & FORMAT(_circ,"0.0") & "'" &
    " stroke-linecap='round'" &
    " transform='rotate(-90 60 60)'/>" &
"<text x='60' y='56' text-anchor='middle' font-size='20' font-weight='bold' fill='" & _color & "'>" &
    FORMAT(_pct, "0%") & "</text>" &
"<text x='60' y='72' text-anchor='middle' font-size='9' fill='rgba(255,255,255,0.5)'>of target</text>" &
"</svg>" &
"</div>"
```

---

## เปรียบเทียบ: HTML Content Visual vs Image Visual

| Feature | Image visual (`data:` URI) | HTML Content Visual |
|---|---|---|
| Colors | ต้อง `%23` encode | `#` ใช้ได้ตรงๆ |
| CSS animations | ❌ ไม่ได้ | ✅ ได้ |
| Media queries | ❌ ไม่ได้ | ✅ ได้ |
| CSS variables | ❌ ไม่ได้ | ✅ ได้ (`foreignObject`) |
| `backdrop-filter` | ❌ | ✅ glassmorphism |
| Flexbox layout | ❌ | ✅ |
| Gradient background | ❌ (SVG gradient เท่านั้น) | ✅ CSS gradient |
| Performance | เร็วกว่าเล็กน้อย | ดีพอสำหรับทุก use case |
| Setup | ง่าย (set Image URL category) | ต้องติดตั้ง HTML Content visual |

**Rule of thumb:**
- Simple chart ใน matrix → Image visual + `data:` URI
- KPI card, animated, glassmorphism, responsive → HTML Content Visual
