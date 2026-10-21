---
paths:
  - "**/*.Report/**/*.json"
---

# PBIR report-layer rules (auto-loads when a visual.json / page.json / bookmark is read)

Distilled from knowledge/GOTCHAS.md — cite gotcha numbers (#N) so the full story stays findable. Keep each line one rule; this file loads only when a matching file is read, so it can be specific.

## Before writing any report JSON
- Desktop closed, or go through pbi-cli.
- Save UTF-8 WITHOUT BOM (hooks + git pre-commit block it).

## Positions and groups
- Grouped visuals store position relative to the parent group.

## Bookmarks
- Show/hide bookmarks: suppressData + applyOnlyToTargetVisuals.

## Cards / formatting
- 
