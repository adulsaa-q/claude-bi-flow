---
name: data-profiling
description: >
  Profile a new or unfamiliar data file (CSV, Excel, Parquet) or SQL table BEFORE
  it goes into ETL, a Power BI model, or a dashboard. Trigger proactively whenever
  the user hands over a new data file, says "ดูข้อมูลนี้หน่อย", "ไฟล์ใหม่", "data ชุดใหม่",
  "เช็ค data ก่อน", "โหลดเข้า model ได้ไหม", or whenever Claude itself is about to
  build ETL/measures on top of data it has never inspected. Produces a compact
  profile: shape, dtypes, nulls, duplicates, key candidates, value ranges, red flags.
  Do NOT trigger for data already profiled this session, or for code review
  (use data-code-review) or broken pipelines (use data-debug-troubleshoot).
---

# Data Profiling — สำรวจข้อมูลก่อนใช้จริง

เป้าหมาย: รู้จักข้อมูลก่อนเขียน ETL/measure ทับลงไป จะได้ไม่เจอ surprise ตอน dashboard ตัวเลขเพี้ยน

## วิธีทำ

**เลือกเครื่องมือ:** ไฟล์ใหญ่หรือหลายไฟล์ → `duckdb` (เร็วสุด ไม่ต้องโหลดเข้า memory ทั้งก้อน)
ไฟล์เล็กหรือต้องการ logic ซับซ้อน → python + pandas ผ่าน scratchpad script

### DuckDB one-liners (CSV/Parquet/Excel*)

```sql
-- shape + schema
DESCRIBE SELECT * FROM 'file.csv';
SELECT COUNT(*) FROM 'file.csv';

-- nulls ต่อคอลัมน์
SELECT column_name, count(*) - count(column_value) AS nulls
FROM (UNPIVOT (SELECT * FROM 'file.csv') ON COLUMNS(*) INTO NAME column_name VALUE column_value)
GROUP BY column_name ORDER BY nulls DESC;

-- duplicates ตาม key ที่สงสัย
SELECT key_col, COUNT(*) c FROM 'file.csv' GROUP BY key_col HAVING c > 1 LIMIT 20;

-- numeric summary
SUMMARIZE SELECT * FROM 'file.csv';
```
*Excel: `INSTALL spatial; LOAD spatial;` แล้ว `st_read('file.xlsx')` หรือแปลงผ่าน markitdown/pandas ก่อน

### Checklist ที่ต้องรายงานทุกครั้ง

1. **Shape:** rows × columns, ขนาดไฟล์
2. **Schema:** dtype ต่อคอลัมน์ — ระวังตัวเลขที่มาเป็น string (มี comma, "-", วงเล็บบัญชี)
3. **Nulls:** % ต่อคอลัมน์ — เกิน 5% ในคอลัมน์สำคัญ = ธงแดง
4. **Duplicates:** ทั้ง full-row และตาม key candidate
5. **Key candidates:** คอลัมน์ไหน unique พอเป็น key / join ได้
6. **ช่วงค่า:** min/max ของ numeric + date range (มีวันที่อนาคต? ปี 1900?)
7. **Categorical:** top 10 ค่า + จำนวน distinct — สะกดไม่ตรงกัน ("ABC" vs "abc ") = ธงแดง
8. **เครื่องหมายบัญชี:** ค่าติดลบมาแบบไหน — `-100`, `(100)`, หรือคอลัมน์ sign แยก (สำคัญมากกับงาน Balance Sheet)

## Output format

สรุปเป็นภาษาไทย กระชับ: ตาราง profile สั้น ๆ + หัวข้อ **🚩 ธงแดง** (สิ่งที่จะทำให้ ETL/measure ผิด) + หัวข้อ **ข้อเสนอ** (dtype ที่ควร cast, key ที่ควรใช้, filter ที่ควรใส่) ถ้าข้อมูลสะอาดดีก็บอกตรง ๆ ไม่ต้องหาเรื่อง
