# Basic SVG Charts (Techniques 1–4)

Source: Dashboard-Design/Power-BI-Design-Files

---

## Technique 1: Dynamic Bullet / Bar Chart

**Use case:** Top-N ranked list with horizontal bars + labels.

```dax
Top Products SVG =
VAR _topn     = 5
VAR _bar_max  = 300
VAR _max_val  = MAXX(TOPN(_topn, ALL(Products[Name]), [Sales], DESC), CALCULATE([Sales]))

VAR _items =
    CONCATENATEX(
        TOPN(_topn, ALL(Products[Name]), [Sales], DESC),
        VAR _name  = Products[Name]
        VAR _val   = CALCULATE([Sales])
        VAR _w     = DIVIDE(_val, _max_val) * _bar_max
        VAR _rank  = RANKX(TOPN(_topn, ALL(Products[Name]), [Sales], DESC), CALCULATE([Sales]), , DESC)
        VAR _y     = (_rank - 1) * 32
        RETURN
            "<rect x='130' y='" & _y & "' width='" & FORMAT(_w,"0") & "' height='22' fill='%230078D4' rx='3'/>" &
            "<text x='125' y='" & (_y+15) & "' text-anchor='end' font-size='11' fill='%23333'>" & _name & "</text>" &
            "<text x='" & (135 + _bar_max) & "' y='" & (_y+15) & "' font-size='10' fill='%23666'>" & FORMAT(_val,"#,##0") & "</text>",
        ""
    )

RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' " &
    "width='500' height='" & (_topn * 32 + 8) & "'>" & _items & "</svg>"
```

---

## Technique 2: Matrix Bubble Chart

**Use case:** Sized circles in each matrix cell — size = metric magnitude.

Place this measure in a Matrix visual's Values field.

```dax
Bubble Cell SVG =
VAR _val       = [Sales]
VAR _min_v     = MINX(ALLSELECTED('Date'), [Sales])
VAR _max_v     = MAXX(ALLSELECTED('Date'), [Sales])
VAR _r_min     = 4
VAR _r_max     = 22
VAR _r         = _r_min + (DIVIDE(_val - _min_v, _max_v - _min_v) * (_r_max - _r_min))
VAR _color     = IF(_val >= [Sales Target], "%23107C10", "%23D13438")
VAR _label     = SELECTEDVALUE('Date'[MonthShort])

RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='52' height='52'>" &
    "<defs><radialGradient id='rg' cx='35%25' cy='35%25'>" &
        "<stop offset='0%25' stop-color='" & _color & "' stop-opacity='1'/>" &
        "<stop offset='100%25' stop-color='" & _color & "' stop-opacity='0.5'/>" &
    "</radialGradient></defs>" &
    "<circle cx='26' cy='26' r='" & FORMAT(_r,"0.0") & "' fill='url(%23rg)'/>" &
    "<text x='26' y='30' text-anchor='middle' font-size='9' font-weight='bold' fill='white'>" & _label & "</text>" &
    "</svg>"
```

---

## Technique 3: Scatter Plot with Images (Logo Plot)

**Use case:** Brand/entity plotted on X-Y axes with their logo as the data point.

Requires a `[Logo Base64]` column in the Brands table with Base64-encoded PNG strings.

```dax
Logo Scatter SVG =
VAR _w   = 700  VAR _h   = 420  VAR _pad = 55

VAR _x_min = MINX(ALLSELECTED('Brands'), [Avg Price])
VAR _x_max = MAXX(ALLSELECTED('Brands'), [Avg Price])
VAR _y_min = MINX(ALLSELECTED('Brands'), [Sales Volume])
VAR _y_max = MAXX(ALLSELECTED('Brands'), [Sales Volume])

VAR _grid =
    "<line x1='" & _pad & "' y1='" & (_h*0.33) & "' x2='" & (_w-_pad) & "' y2='" & (_h*0.33) & "' stroke='%23eeeeee' stroke-width='1'/>" &
    "<line x1='" & _pad & "' y1='" & (_h*0.66) & "' x2='" & (_w-_pad) & "' y2='" & (_h*0.66) & "' stroke='%23eeeeee' stroke-width='1'/>" &
    "<line x1='" & (_w*0.33) & "' y1='" & _pad & "' x2='" & (_w*0.33) & "' y2='" & (_h-_pad) & "' stroke='%23eeeeee' stroke-width='1'/>" &
    "<line x1='" & (_w*0.66) & "' y1='" & _pad & "' x2='" & (_w*0.66) & "' y2='" & (_h-_pad) & "' stroke='%23eeeeee' stroke-width='1'/>"

VAR _points =
    CONCATENATEX(
        ALLSELECTED('Brands'),
        VAR _b64 = CALCULATE(MAX('Brands'[Logo Base64]))
        VAR _xv  = CALCULATE([Avg Price])
        VAR _yv  = CALCULATE([Sales Volume])
        VAR _cx  = _pad + DIVIDE(_xv - _x_min, _x_max - _x_min) * (_w - 2*_pad)
        VAR _cy  = (_h - _pad) - DIVIDE(_yv - _y_min, _y_max - _y_min) * (_h - 2*_pad)
        RETURN
            "<image href='data:image/png;base64," & _b64 & "' " &
                "x='" & FORMAT(_cx-18,"0") & "' y='" & FORMAT(_cy-18,"0") & "' width='36' height='36'/>",
        ""
    )

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='" & _w & "' height='" & _h & "'>" &
    _grid & _points &
    "<text x='" & (_w/2) & "' y='" & (_h-8) & "' text-anchor='middle' font-size='11' fill='%23888'>Avg Price →</text>" &
    "<text x='12' y='" & (_h/2) & "' text-anchor='middle' font-size='11' fill='%23888' transform='rotate(-90 12 " & (_h/2) & ")'>↑ Sales Volume</text>" &
    "</svg>"
```

---

## Technique 4: IBCS Variance Bar

**Use case:** Actual vs Budget with semantic colors (IBCS standard).

```dax
IBCS Variance SVG =
VAR _ac          = [Sales AC]
VAR _bu          = [Sales BU]
VAR _delta       = _ac - _bu
VAR _max_ref     = MAXX(ALLSELECTED('Periods'), [Sales BU])
VAR _bar_area    = 360
VAR _ac_w        = DIVIDE(_ac, _max_ref) * _bar_area
VAR _bu_x        = 80 + DIVIDE(_bu, _max_ref) * _bar_area
VAR _is_pos      = _delta >= 0
VAR _d_color     = IF(_is_pos, "%23107C10", "%23D13438")
VAR _d_symbol    = IF(_is_pos, "▲ ", "▼ ")
VAR _d_label     = _d_symbol & FORMAT(ABS(_delta), "#,##0") & "  (" & FORMAT(DIVIDE(_delta, _bu), "+0.0%25;-0.0%25") & ")"

RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='64'>" &
    -- AC bar (solid dark)
    "<rect x='80' y='14' width='" & FORMAT(_ac_w,"0") & "' height='22' fill='%231A1A1A'/>" &
    -- BU reference line (gray)
    "<rect x='" & FORMAT(_bu_x,"0") & "' y='7' width='3' height='36' fill='%23888888'/>" &
    -- Labels
    "<text x='74' y='29' text-anchor='end' font-size='10' font-weight='bold' fill='%231A1A1A'>AC</text>" &
    "<text x='" & FORMAT(80 + _ac_w + 6, "0") & "' y='29' font-size='10' fill='%23333'>" & FORMAT(_ac,"#,##0") & "</text>" &
    "<text x='80' y='56' font-size='10' fill='" & _d_color & "'>" & _d_label & "</text>" &
    "</svg>"
```
