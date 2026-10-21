"""PostToolUse hook — flag a UTF-8 BOM written to any PBIR JSON file (Gotcha #7).

Power BI Desktop REJECTS report-layer JSON (visual.json, page.json, bookmarks)
that starts with a UTF-8 BOM (bytes EF BB BF). This is the project's #1
recurring failure mode: batch find-replace across visual.json after a TOM
rename can silently write a BOM if the wrong encoder is used.

Two modes, wired in .claude/settings.json under hooks.PostToolUse
(matcher Edit|Write|Bash|PowerShell):
  * Edit/Write  -> tool_input.file_path is known: check that one file.
  * Bash/PowerShell -> no file_path (most batch edits arrive this way, which the
    old Edit|Write-only matcher never saw): scan every PBIR JSON under
    every *.Report / *.SemanticModel folder in the project (located via the *.pbip
    files, max depth 2) whose mtime is within RECENT_SECONDS and report any with a BOM.
Exit 2 = feed the message back to Claude so it re-saves without a BOM.
"""
import json
import re
import os
import sys
import time

RECENT_SECONDS = 180
PBIR_NAMES = ("visual.json", "page.json", "pages.json", "report.json")
BOM = b"\xef\xbb\xbf"


def has_bom(path):
    try:
        with open(path, "rb") as f:
            return f.read(3) == BOM
    except Exception:
        return False


try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
path = (data.get("tool_input") or {}).get("file_path", "") or ""
bad = []

if path:
    low = path.replace("\\", "/").lower()
    if low.endswith(".json") and ("/definition/" in low or low.endswith(PBIR_NAMES)) and has_bom(path):
        bad.append(path)
elif tool in ("Bash", "PowerShell"):
    # Only pay for the tree walk when the command could have written report JSON:
    # it ran a script (.py/.ps1), or names the report tree / a .json path directly.
    cmd = (data.get("tool_input") or {}).get("command", "") or ""
    if not re.search(r"\.(py|ps1)\b|\.pbip\b|\.json\b|\.Report\b|\.SemanticModel\b", cmd, re.I):
        sys.exit(0)
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    cutoff = time.time() - RECENT_SECONDS
    for dirpath, dirnames, filenames in os.walk(proj):
        # prune: only descend into *.Report / *.SemanticModel trees (and the dirs leading to them, depth<=2)
        depth = os.path.relpath(dirpath, proj).count(os.sep)
        in_tree = any(seg.endswith((".Report", ".SemanticModel")) for seg in os.path.relpath(dirpath, proj).split(os.sep))
        if not in_tree:
            if depth >= 2:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("archive", "deliverables", "reference", "docs", "node_modules")]
        if ".pbi" in dirnames:
            dirnames.remove(".pbi")  # Desktop cache, not report definition
        for fn in filenames:
            if not fn.endswith(".json"):
                continue
            if fn not in PBIR_NAMES and "bookmarks" not in dirpath.replace("\\", "/"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                if os.path.getmtime(full) < cutoff:
                    continue
            except OSError:
                continue
            if has_bom(full):
                bad.append(full)

if bad:
    shown = "\n".join(bad[:10]) + (f"\n... +{len(bad) - 10} more" if len(bad) > 10 else "")
    sys.stderr.write(
        f"UTF-8 BOM detected in {len(bad)} PBIR JSON file(s) - Power BI Desktop will REJECT them (Gotcha #7):\n{shown}\n"
        "Re-save as UTF-8 WITHOUT BOM: PowerShell -> New-Object System.Text.UTF8Encoding $False "
        "(never [System.Text.Encoding]::UTF8); Python -> encoding='utf-8' (never 'utf-8-sig' on write)."
    )
    sys.exit(2)

sys.exit(0)
