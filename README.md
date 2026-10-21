# claude-bi-flow

ชุดตั้งค่า Claude Code สำหรับงาน BI (Power BI / DAX / SQL Server / ETL) ติดตั้งครั้งเดียวได้ skill, กฎการทำงาน และ plugin ครบ โดยไม่ต้องใช้สิทธิ์ admin

## ติดตั้ง (ให้ AI ทำให้)

1. clone repo นี้
2. เปิด Claude Code ในโฟลเดอร์ที่ clone มา แล้วพิมพ์:

   > อ่าน SETUP.md แล้ว setup ให้ครบตามนั้น

AI จะเช็คเครื่อง, รัน `install.ps1 -DryRun` ให้ดูก่อน, ติดตั้งจริง แล้วรัน `doctor.ps1` ยืนยันผล

ทำเองก็ได้:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun   # ดูก่อนว่าจะทำอะไร
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\doctor.ps1            # เปิด terminal ใหม่ก่อน
```

## ได้อะไรบ้าง

| ส่วน | รายละเอียด |
|---|---|
| Power BI skills 13 ตัว | `power-bi-dax`, `-modeling`, `-report`, `-visuals`, `-pages`, `-themes`, `-filters`, `-deployment`, `-docs`, `-diagnostics`, `-partitions`, `-security`, `-custom-visuals` (ติดตั้งผ่าน `pbi-cli`) |
| Skills ของ repo นี้ 9 ตัว | `project-init`, `handoff`, `data-code-review`, `data-debug-troubleshoot`, `data-profiling`, `sql-server-tuning-bi`, `data-warehouse-kimball`, `power-bi-design-advanced`, `power-bi-svg-design` |
| กฎกลางของทีม | block ใน `~/.claude/CLAUDE.md` (ตารางว่าสถานการณ์ไหนใช้ skill ไหน + นิสัยการเขียนโค้ด + กฎทำงานกับ DB) |
| Plugins | `commit-commands`, `code-review`, `remember` |
| Project scaffold | skill `project-init` สร้างโครงโปรเจกต์ใหม่ให้ พร้อม hook กัน `.env` หลุด, กัน Desktop ทับไฟล์, git pre-commit |

ไม่รวม skill Excel / Word / PowerPoint เพราะเป็นของ Anthropic ที่มี license เฉพาะ ให้ดึงจาก https://github.com/anthropics/skills (ขั้นตอนอยู่ใน SETUP.md)

## Flow การทำงานที่ repo นี้ตั้งใจให้ทีมใช้

1. เริ่มโปรเจกต์ใหม่ -> `project-init` วางโครงสร้าง (AGENTS.md, CLAUDE.md, PROJECT_MAP.md, hooks, .env.example)
2. ข้อมูลใหม่ -> `data-profiling` ตรวจก่อนเข้า ETL / model
3. สร้าง model / measure -> `power-bi-modeling`, `power-bi-dax` (AI รัน query เบื้องหลัง คนเป็นคนสร้าง visual)
4. ก่อน commit -> `data-code-review` แล้วค่อย commit เป็นช่วง ๆ
5. เจอสิ่งแปลก ๆ -> จดเข้า gotcha ทันที (เป็นสินทรัพย์ที่โตขึ้นทุกโปรเจกต์)
6. จบวัน -> `handoff` สรุปสถานะให้ session ถัดไป (หรือ AI ตัวอื่น) อ่านแล้วทำต่อได้

## โครงสร้าง repo

```
install.ps1   doctor.ps1   plugins.txt   SETUP.md
global/CLAUDE.team.md     # กฎกลางที่ถูกเขียนลง ~/.claude/CLAUDE.md
skills/                   # skill ที่ copy ไป ~/.claude/skills/
```

## อัปเดต

`git pull` แล้วรัน `install.ps1` อีกครั้ง (idempotent) skill ที่คุณแก้เองจะไม่ถูกทับ เว้นแต่ใส่ `-Force` (มี backup ให้เสมอ)
