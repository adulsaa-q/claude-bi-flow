# Advanced SVG Charts (Techniques 5–11)

These are the visuals that make Power BI dashboards look competition-grade.

---

## Technique 5: Circular Progress Ring

**Why it looks great:** The `stroke-dasharray` trick draws only part of a circle's stroke, creating a clean arc. Combined with `stroke-linecap='round'` it gets rounded ends. Color changes at thresholds (green/blue/orange/red).

```dax
Progress Ring SVG =
VAR _val    = [Sales]
VAR _target = [Sales Target]
VAR _pct    = MIN(DIVIDE(_val, _target), 1)        -- cap at 100%

-- Arc math: circumference = 2πr
VAR _r      = 38
VAR _cx     = 55  VAR _cy = 55
VAR _circ   = 2 * 3.14159265 * _r
VAR _dash   = _pct * _circ                          -- filled arc length
VAR _gap    = _circ - _dash                         -- empty arc length

VAR _color  =
    IF(_pct >= 1,    "%23107C10",                   -- green: achieved
    IF(_pct >= 0.75, "%230078D4",                   -- blue: on track
    IF(_pct >= 0.5,  "%23FF8C00",                   -- orange: at risk
                     "%23D13438")))                  -- red: behind

VAR _pct_txt = FORMAT(_pct * 100, "0") & "%25"
VAR _val_txt = FORMAT(_val / 1000000, "0.0") & "M"

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='110' height='110'>" &
    -- Track (background circle)
    "<circle cx='" & _cx & "' cy='" & _cy & "' r='" & _r &
        "' fill='none' stroke='%23F0F0F0' stroke-width='10'/>" &
    -- Progress arc — rotated -90° so it starts from top
    "<circle cx='" & _cx & "' cy='" & _cy & "' r='" & _r &
        "' fill='none' stroke='" & _color & "' stroke-width='10'" &
        " stroke-dasharray='" & FORMAT(_dash,"0.00") & " " & FORMAT(_gap,"0.00") & "'" &
        " stroke-linecap='round'" &
        " transform='rotate(-90 " & _cx & " " & _cy & ")'/>" &
    -- Center text: percentage
    "<text x='" & _cx & "' y='" & (_cy - 5) & "'" &
        " text-anchor='middle' font-size='18' font-weight='bold' fill='" & _color & "'>" & _pct_txt & "</text>" &
    -- Center text: value
    "<text x='" & _cx & "' y='" & (_cy + 13) & "'" &
        " text-anchor='middle' font-size='11' fill='%23888'>" & _val_txt & "</text>" &
    "</svg>"
```

**Setup:** Image visual → paste measure in Image URL field. Set visual to square (110×110px).

---

## Technique 6: Sparkline in Matrix/Table Row

**Why it looks great:** Each row gets its own mini trend line. Shows direction at a glance without leaving the table. Uses `<polyline>` with normalized Y coordinates.

```dax
-- Place in Matrix: rows = Products, columns = nothing, values = this measure
Row Sparkline SVG =
VAR _cat    = SELECTEDVALUE(Products[Category])   -- current row context
VAR _w      = 120  VAR _h = 36
VAR _pad    = 4
VAR _pw     = _w - 2*_pad  VAR _ph = _h - 2*_pad

-- Get 12 monthly values for this category
VAR _monthly =
    CALCULATETABLE(
        ADDCOLUMNS(
            SUMMARIZE('Date', 'Date'[MonthNum]),
            "@v", [Sales]
        ),
        REMOVEFILTERS('Date'[MonthNum]),
        Products[Category] = _cat
    )

VAR _min_v  = MINX(_monthly, [@v])
VAR _max_v  = MAXX(_monthly, [@v])
VAR _range  = _max_v - _min_v

-- Build polyline points string: "x1,y1 x2,y2 ..."
VAR _pts =
    CONCATENATEX(
        _monthly,
        VAR _m  = 'Date'[MonthNum]
        VAR _v  = [@v]
        VAR _x  = FORMAT(_pad + DIVIDE(_m - 1, 11) * _pw, "0.0")
        VAR _y  = FORMAT((_h - _pad) - DIVIDE(_v - _min_v, IF(_range = 0, 1, _range)) * _ph, "0.0")
        RETURN _x & "," & _y,
        " ",
        'Date'[MonthNum], ASC
    )

-- Last point dot (highlight current month)
VAR _last_v = MAXX(FILTER(_monthly, 'Date'[MonthNum] = 12), [@v])
VAR _dot_x  = _pad + _pw
VAR _dot_y  = (_h - _pad) - DIVIDE(_last_v - _min_v, IF(_range = 0, 1, _range)) * _ph
VAR _trend_color = IF(_last_v >= _min_v + _range * 0.5, "%23107C10", "%23D13438")

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & _h & "'>" &
    "<polyline points='" & _pts & "'" &
        " fill='none' stroke='" & _trend_color & "' stroke-width='2' stroke-linejoin='round'/>" &
    "<circle cx='" & FORMAT(_dot_x,"0") & "' cy='" & FORMAT(_dot_y,"0.0") &
        "' r='3' fill='" & _trend_color & "'/>" &
    "</svg>"
```

---

## Technique 7: Lollipop Chart

**Why it looks great:** Stem line + dot replaces a solid bar. Much cleaner, reduces visual weight while keeping readability. Dots emphasize the exact value better than bar endpoints.

```dax
Lollipop SVG =
VAR _n        = 10
VAR _w        = 520  VAR _row_h = 36
VAR _label_w  = 140  VAR _plot_w = _w - _label_w - 60

VAR _data     = TOPN(_n, ALL(Products[Name]), CALCULATE([Sales]), DESC)
VAR _max_v    = MAXX(_data, CALCULATE([Sales]))

VAR _items =
    CONCATENATEX(
        _data,
        VAR _name  = Products[Name]
        VAR _val   = CALCULATE([Sales])
        VAR _rank  = RANKX(_data, CALCULATE([Sales]), , DESC)
        VAR _y     = (_rank - 1) * _row_h + (_row_h / 2)
        VAR _x_dot = _label_w + DIVIDE(_val, _max_v) * _plot_w

        RETURN
            -- Stem
            "<line x1='" & _label_w & "' y1='" & _y & "' x2='" & FORMAT(_x_dot,"0") & "' y2='" & _y &
                "' stroke='%230078D4' stroke-width='2' opacity='0.25'/>" &
            -- Dot
            "<circle cx='" & FORMAT(_x_dot,"0") & "' cy='" & _y & "' r='7' fill='%230078D4'/>" &
            -- Category label (left)
            "<text x='" & (_label_w - 8) & "' y='" & (_y + 4) & "' text-anchor='end'" &
                " font-size='11' fill='%23333'>" & _name & "</text>" &
            -- Value label (right of dot)
            "<text x='" & FORMAT(_x_dot + 12, "0") & "' y='" & (_y + 4) & "'" &
                " font-size='10' fill='%23666'>" & FORMAT(_val, "#,##0") & "</text>",
        ""
    )

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & (_n * _row_h) & "'>" &
    _items & "</svg>"
```

---

## Technique 8: Waffle Chart

**Why it looks great:** 10×10 grid = 100 squares, each represents 1%. Fills from bottom-left. Immediately intuitive for % completion. Color changes by achievement band.

```dax
Waffle SVG =
VAR _pct     = MIN(DIVIDE([Sales], [Sales Target]), 1)
VAR _filled  = ROUND(_pct * 100, 0)              -- number of squares to fill

VAR _sq      = 14  VAR _gap = 2                  -- square size + gap
VAR _cols    = 10  VAR _rows = 10
VAR _w       = _cols * (_sq + _gap) + _gap
VAR _h       = _rows * (_sq + _gap) + _gap

VAR _color   =
    IF(_pct >= 1,    "%23107C10",
    IF(_pct >= 0.75, "%230078D4",
    IF(_pct >= 0.5,  "%23FF8C00",
                     "%23D13438")))

VAR _cells =
    CONCATENATEX(
        GENERATESERIES(1, 100, 1),
        VAR _i    = [Value]
        VAR _col  = MOD(_i - 1, _cols)
        VAR _row  = INT((_i - 1) / _cols)
        -- fill from bottom-left: invert row index
        VAR _x    = _gap + _col * (_sq + _gap)
        VAR _y    = _gap + (_rows - 1 - _row) * (_sq + _gap)
        VAR _fill = IF(_i <= _filled, _color, "%23F0F0F0")
        RETURN
            "<rect x='" & _x & "' y='" & _y & "' width='" & _sq & "' height='" & _sq & "' fill='" & _fill & "' rx='2'/>",
        ""
    )

VAR _label_y = _h + 16
RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & (_h + 20) & "'>" &
    _cells &
    "<text x='" & (_w / 2) & "' y='" & _label_y & "' text-anchor='middle'" &
        " font-size='12' font-weight='bold' fill='" & _color & "'>" &
        FORMAT(_pct, "0%25") & " of target</text>" &
    "</svg>"
```

---

## Technique 9: Dumbbell Chart (Range / PY vs AC)

**Why it looks great:** Two dots connected by a line. Instantly shows direction and magnitude of change between two periods. Far more readable than side-by-side bars for comparison.

```dax
Dumbbell SVG =
VAR _n       = 8
VAR _w       = 560  VAR _row_h = 40
VAR _label_w = 140  VAR _plot_w = _w - _label_w - 60

VAR _data    = TOPN(_n, ALL('Region'), CALCULATE([Sales]), DESC)

-- Combined min/max across both AC and PY for consistent axis
VAR _min_v   = MINX(_data, MIN(CALCULATE([Sales]), CALCULATE([Sales PY])))
VAR _max_v   = MAXX(_data, MAX(CALCULATE([Sales]), CALCULATE([Sales PY])))

VAR _items =
    CONCATENATEX(
        _data,
        VAR _region  = 'Region'[Region]
        VAR _ac      = CALCULATE([Sales])
        VAR _py      = CALCULATE([Sales PY])
        VAR _rank    = RANKX(_data, CALCULATE([Sales]), , DESC)
        VAR _y       = (_rank - 1) * _row_h + (_row_h / 2)
        VAR _x_ac    = _label_w + DIVIDE(_ac - _min_v, _max_v - _min_v) * _plot_w
        VAR _x_py    = _label_w + DIVIDE(_py - _min_v, _max_v - _min_v) * _plot_w
        VAR _x_left  = IF(_x_ac < _x_py, _x_ac, _x_py)
        VAR _x_right = IF(_x_ac > _x_py, _x_ac, _x_py)
        VAR _grew    = _ac >= _py
        VAR _c_conn  = IF(_grew, "%2300B050", "%23D13438")   -- green/red connector
        VAR _c_ac    = IF(_grew, "%230078D4", "%23D13438")

        RETURN
            -- Connector line
            "<line x1='" & FORMAT(_x_left,"0") & "' y1='" & _y &
                "' x2='" & FORMAT(_x_right,"0") & "' y2='" & _y &
                "' stroke='" & _c_conn & "' stroke-width='2.5' opacity='0.35'/>" &
            -- PY dot (gray, smaller)
            "<circle cx='" & FORMAT(_x_py,"0") & "' cy='" & _y & "' r='6' fill='%23AAAAAA'/>" &
            -- AC dot (colored, larger)
            "<circle cx='" & FORMAT(_x_ac,"0") & "' cy='" & _y & "' r='9' fill='" & _c_ac & "'/>" &
            -- Label
            "<text x='" & (_label_w - 8) & "' y='" & (_y + 4) & "' text-anchor='end'" &
                " font-size='11' fill='%23333'>" & _region & "</text>",
        ""
    )

-- Legend
VAR _leg_y = _n * _row_h + 14
RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & (_n * _row_h + 24) & "'>" &
    _items &
    "<circle cx='" & (_w - 90) & "' cy='" & _leg_y & "' r='6' fill='%230078D4'/>" &
    "<text x='" & (_w - 81) & "' y='" & (_leg_y + 4) & "' font-size='9' fill='%23666'>AC</text>" &
    "<circle cx='" & (_w - 55) & "' cy='" & _leg_y & "' r='5' fill='%23AAAAAA'/>" &
    "<text x='" & (_w - 46) & "' y='" & (_leg_y + 4) & "' font-size='9' fill='%23666'>PY</text>" &
    "</svg>"
```

---

## Technique 10: Traffic Light with Glow Effect

**Why it looks great:** SVG `<filter>` with `feGaussianBlur` creates a real glow around the circle. Used in matrix rows to show status at a glance. The glow color matches the status color.

```dax
Traffic Light SVG =
VAR _val    = [Sales]
VAR _target = [Target]
VAR _pct    = DIVIDE(_val, _target)

VAR _status =
    IF(_pct >= 1,    "green",
    IF(_pct >= 0.8,  "amber",
                     "red"))

VAR _fill =
    SWITCH(_status,
        "green", "%23107C10",
        "amber", "%23FF8C00",
        "red",   "%23D13438")

VAR _label =
    SWITCH(_status,
        "green", "On Track",
        "amber", "At Risk",
        "red",   "Behind")

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='44'>" &
    -- Glow filter definition
    "<defs>" &
        "<filter id='glow' x='-50%25' y='-50%25' width='200%25' height='200%25'>" &
            "<feGaussianBlur stdDeviation='4' result='blur'/>" &
            "<feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge>" &
        "</filter>" &
    "</defs>" &
    -- Outer glow circle (larger, more transparent)
    "<circle cx='22' cy='22' r='16' fill='" & _fill & "' opacity='0.2'/>" &
    -- Main dot with glow filter
    "<circle cx='22' cy='22' r='11' fill='" & _fill & "' filter='url(%23glow)'/>" &
    -- Status text
    "<text x='42' y='18' font-size='12' font-weight='bold' fill='" & _fill & "'>" & _label & "</text>" &
    "<text x='42' y='33' font-size='10' fill='%23888'>" & FORMAT(_pct, "0.0%25") & " of target</text>" &
    "</svg>"
```

**Note:** `filter='url(%23glow)'` — the `%23` encodes `#` for the fragment identifier. This is required even when using HTML Content Visual direct mode.

---

## Technique 11: Gradient Progress Bar (for Table/Matrix cells)

**Why it looks great:** Rounded pill shape with gradient fill + text overlay. Much richer than a native data bar. Color changes by % band. Text inside bar when ≥ 40% full, outside when smaller.

```dax
Progress Bar SVG =
VAR _val     = [Sales]
VAR _target  = [Sales Target]
VAR _pct     = MIN(DIVIDE(_val, _target), 1)

VAR _w       = 160  VAR _h = 26
VAR _fill_w  = _pct * _w
VAR _r       = 6                                   -- border radius

VAR _color   =
    IF(_pct >= 1,    "%23107C10",
    IF(_pct >= 0.75, "%230078D4",
    IF(_pct >= 0.5,  "%23FF8C00",
                     "%23D13438")))

-- Text inside bar when it's wide enough, outside when narrow
VAR _txt_x   = IF(_fill_w >= 50, _fill_w / 2, _fill_w + 6)
VAR _txt_anchor = IF(_fill_w >= 50, "middle", "start")
VAR _txt_fill   = IF(_fill_w >= 50, "white", _color)
VAR _pct_txt    = FORMAT(_pct, "0%25")

RETURN
    "data:image/svg+xml;utf8," &
    "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & _h & "'>" &
    "<defs>" &
        "<linearGradient id='lg' x1='0' y1='0' x2='1' y2='0'>" &
            "<stop offset='0%25' stop-color='" & _color & "' stop-opacity='0.7'/>" &
            "<stop offset='100%25' stop-color='" & _color & "' stop-opacity='1'/>" &
        "</linearGradient>" &
    "</defs>" &
    -- Track
    "<rect x='0' y='3' width='" & _w & "' height='" & (_h-6) & "' rx='" & _r & "' fill='%23F0F0F0'/>" &
    -- Fill with gradient
    "<rect x='0' y='3' width='" & FORMAT(_fill_w,"0.0") & "' height='" & (_h-6) & "' rx='" & _r & "' fill='url(%23lg)'/>" &
    -- Percentage label
    "<text x='" & FORMAT(_txt_x,"0") & "' y='" & (_h/2 + 4) & "' text-anchor='" & _txt_anchor &
        "' font-size='10' font-weight='bold' fill='" & _txt_fill & "'>" & _pct_txt & "</text>" &
    "</svg>"
```
