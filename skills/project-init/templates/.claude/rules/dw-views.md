---
paths:
  - "metadata/**"
---

# DW / ETL view rules (auto-loads when metadata/ snapshots are read)

Distilled from knowledge/GOTCHAS.md — cite gotcha numbers (#N) so the full story stays findable. Keep each line one rule; this file loads only when a matching file is read, so it can be specific.

## Snapshots are not live
- metadata/ dumps age silently; check sys.views.modify_date before trusting them.

## View semantics the DAX layer assumes
- 
