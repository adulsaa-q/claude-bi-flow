# Power BI Background Design System

สไตล์ powerbidesign7011 — design background ก่อน แล้วค่อยวาง visual ทีหลัง
Sources: lukasreese.com, notjustaprettydashboard.com, figma.com/community

---

## Why Background-First?

ช่อง powerbidesign7011 ทำให้ dashboard สวยเพราะ **background คือ UI shell** ไม่ใช่แค่สี
วิธีคิด: background กำหนด zone → ใส่ visual ลงใน zone → ไม่ต้องปรับ margin ทีหลัง

```
❌ Power BI native shapes → เคลื่อนแล้ว misalign ทุกครั้ง
✅ Figma → export PNG/SVG → import เป็น wallpaper → ไม่มีวันหลุด
```

---

## 4 วิธีสร้าง Background (เรียงจากช้าไปเร็ว)

| Method | Tool | เวลา | ดีสุดสำหรับ |
|---|---|---|---|
| 1. PBI native shapes | Power BI | ช้ามาก | prototype เร็ว |
| 2. PowerPoint | PowerPoint | ปานกลาง | ทีมที่ไม่มี Figma |
| 3. Figma | Figma (free) | เร็ว | design-focused, reusable |
| 4. Background generator | Figma plugin/tool | เร็วมาก | scale หลาย report |

**แนะนำ: Figma (Method 3)** — free, component system, export ได้ทุก format

---

## Figma Workflow (Method 3) — ทีละขั้น

### Step 1: ตั้ง Canvas ให้ตรงกับ Power BI

```
Power BI default canvas = 1280 × 720 px
Figma frame: Width = 1280, Height = 720
```

ถ้าใช้ HD:
```
Power BI HD = 1920 × 1080 px
Figma frame: Width = 1920, Height = 1080
```

**สำคัญ:** ต้องตั้ง canvas ให้ตรงกันก่อน ถ้าผิดจะ misalign เมื่อ import

### Step 2: วาง Grid System ใน Figma

ใช้ Figma Layout Grid:
```
Columns: 12 columns, Gutter: 16px, Margin: 16px
Rows: (optional) Row height: 40px
```

Zone template สำหรับ 1280×720:

```
┌──────────────────────────────────────────────┐ y=0
│  HEADER ZONE  bg=#0078D4  h=40px             │
├──────────────────────────────────────────────┤ y=40
│  SLICER ZONE  bg=#F5F5F5  h=48px             │
├──────────────────────────────────────────────┤ y=88
│  KPI ZONE     bg=transparent  h=110px        │
│  [card bg]  [card bg]  [card bg]  [card bg]  │
├────────────────────────┬─────────────────────┤ y=198
│  MAIN CHART            │  SECONDARY           │
│  bg=white / dark panel │  bg=white / panel    │
│  w=780px               │  w=484px             │
│                        ├─────────────────────┤
│                        │  TABLE / DETAIL      │
│                        │                      │
└────────────────────────┴─────────────────────┘ y=720
```

### Step 3: Design ใน Figma

**Light mode (professional style):**
```
Page bg:        #F5F7FA   (ไม่ใช้ขาวจัด — ลด eye strain)
Header:         #0078D4   + white text
Panel/card bg:  #FFFFFF   + box shadow: 0 2px 8px rgba(0,0,0,0.08)
Divider:        #E8ECF0
Accent:         #0078D4
```

**Dark mode (powerbidesign7011 style):**
```
Page bg:        #0F1117   (dark navy)
Header:         #1A1D2E   (slightly lighter)
Panel/card bg:  #1E2235   + border: 1px solid rgba(255,255,255,0.08)
Accent glow:    #38BDF8   (sky blue neon)
Text primary:   #E5E7EB
Text muted:     #6B7280
```

**Dark + gradient background (competition style):**
- ใส่ radial gradient blobs: สีม่วง/น้ำเงิน/ชมพู opacity 15-25%
- วาง panels ทับ = glassmorphism โดย default
- Export เป็น PNG ขนาด 1280×720 @2x

### Step 4: Export จาก Figma

```
File → Export frame
Format: PNG (ดีที่สุด — crisp, ไม่มี SVG encoding issue)
Scale: 2x (สำหรับ retina/HD screen)
```

หรือ SVG ถ้าต้องการ embed ใน theme JSON:
```
Format: SVG
Include: "id" attributes ปิด
```

### Step 5: Import ใน Power BI

**วิธีที่ 1 — Wallpaper (แนะนำ):**
```
Format pane → Page information → Wallpaper
→ Browse → เลือกไฟล์ PNG
→ Fit = "Fit"
→ Transparency = 0%
```

**วิธีที่ 2 — ใส่ใน Theme JSON (ใช้ทุกหน้าอัตโนมัติ):**
```json
{
  "name": "Corporate Dark",
  "background": "#0F1117",
  "visualStyles": {
    "page": {
      "*": {
        "background": [{
          "image": {
            "url": "data:image/svg+xml;base64,<base64_string>",
            "scaling": "Fit"
          },
          "transparency": 0
        }]
      }
    }
  }
}
```

---

## Dark Mode Color Palette Templates

### Navy (powerbidesign7011 style)
```
Background:     #0F1117
Surface:        #1A1D2E
Surface hover:  #252840
Border:         rgba(255,255,255,0.08)
Accent:         #38BDF8   (sky blue)
Accent glow:    rgba(56,189,248,0.15)
Text:           #E5E7EB
Text muted:     #6B7280
Good:           #34D399   (emerald)
Bad:            #F87171   (coral red)
Warning:        #FBBF24   (amber)
```

### Charcoal (executive dark style)
```
Background:     #1C1C1E
Surface:        #2C2C2E
Border:         rgba(255,255,255,0.12)
Accent:         #FF9F0A   (amber)
Text:           #FFFFFF
Text muted:     #8E8E93
Good:           #30D158
Bad:            #FF453A
```

### Midnight (deep dark, neon style)
```
Background:     #070B14
Surface:        #0D1526
Border:         rgba(99,179,237,0.2)
Accent:         #63B3ED + glow
Text:           #EDF2F7
Text muted:     #718096
Good:           #48BB78
Bad:            #FC8181
```

---

## Star Ratings SVG (bonus visual)

Popular ใน powerbidesign7011 style สำหรับ review/score dashboards:

```dax
Star Rating SVG =
VAR _rating  = ROUND([Score], 0)           -- 1–5 integer
VAR _max     = 5
VAR _filled  = "%23FFB900"                 -- gold
VAR _empty   = "%23D1D5DB"                 -- gray

-- Star polygon points (centered in 20×20 box per star)
VAR _star_path = "M10,2 L12.4,7.8 L18.5,8.2 L14,12.4 L15.5,18.5 L10,15.2 L4.5,18.5 L6,12.4 L1.5,8.2 L7.6,7.8 Z"

VAR _stars =
    CONCATENATEX(
        GENERATESERIES(1, _max, 1),
        VAR _i    = [Value]
        VAR _x    = (_i - 1) * 22           -- 20px star + 2px gap
        VAR _fill = IF(_i <= _rating, _filled, _empty)
        RETURN
            "<g transform='translate(" & _x & ",0)'>" &
            "<polygon points='10,2 12.4,7.8 18.5,8.2 14,12.4 15.5,18.5 10,15.2 4.5,18.5 6,12.4 1.5,8.2 7.6,7.8' " &
                "fill='" & _fill & "'/>" &
            "</g>",
        ""
    )

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & (_max * 22) & "' height='20'>" &
    _stars & "</svg>"
```

---

## Panel Card SVG Background

สำหรับ KPI cards ที่มี gradient background แบบ powerbidesign7011:

```dax
-- ใช้ใน HTML Content Visual
KPI Card HTML =
VAR _title  = "Total Revenue"
VAR _val    = FORMAT([Sales] / 1E6, "#,##0.0") & "M"
VAR _delta  = DIVIDE([Sales] - [Sales PY], [Sales PY])
VAR _is_up  = _delta >= 0
VAR _d_txt  = (IF(_is_up, "▲ +", "▼ ")) & FORMAT(ABS(_delta), "0.0%")
VAR _d_col  = IF(_is_up, "#34D399", "#F87171")

RETURN
"<div style='" &
    "background:linear-gradient(135deg,#1E2235 0%,#252840 100%);" &
    "border:1px solid rgba(255,255,255,0.08);" &
    "border-radius:12px;padding:16px 20px;" &
    "font-family:Segoe UI,sans-serif;" &
    "box-shadow:0 4px 20px rgba(0,0,0,0.3);" &
"'>" &
"<div style='font-size:10px;color:#6B7280;letter-spacing:1.5px;text-transform:uppercase;'>" & _title & "</div>" &
"<div style='font-size:32px;font-weight:300;color:#E5E7EB;margin:8px 0 4px;'>$" & _val & "</div>" &
"<div style='font-size:11px;color:" & _d_col & ";'>" & _d_txt & " vs PY</div>" &
"</div>"
```

---

## Theme-First Workflow (notjustaprettydashboard.com style)

สร้างทุกอย่างใน JSON ก่อนเปิด report:

```
1. Brand colors → dataColors array
2. Figma background → export SVG/PNG
3. ฝัง background ใน theme JSON (page wallpaper)
4. Typography → textClasses
5. Visual defaults → visualStyles (remove borders, shadows)
6. Export .json → import ใน Power BI
7. วาง visual ลง zone — ไม่ต้องปรับสี/font อีกเลย
```

ข้อดี: ทีม 5 คน ทำ report แล้ว look & feel เหมือนกัน 100% โดยไม่ต้อง coordinate
