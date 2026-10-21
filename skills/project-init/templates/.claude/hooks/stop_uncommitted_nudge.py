"""Stop hook — one-line nudge when model/report edits are sitting uncommitted.

Why: the repo has lost uncommitted work twice (gotcha #68 `git clean`, #138
export-tmdl wipe) and the recovery path each time was "was it committed?".
Fires at the end of a Claude turn; never blocks (exit 0). Throttled to one
nudge per NUDGE_EVERY seconds via a marker in the scratchpad so it doesn't
nag every turn. Wired in .claude/settings.json under hooks.Stop.
"""
import json
import hashlib
import os
import subprocess
import sys
import time

NUDGE_EVERY = 3600
WATCH = (".tmdl", "visual.json", "page.json", "pages.json", "report.json", ".bookmark.json")

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cwd = data.get("cwd") or os.getcwd()
project_key = hashlib.sha256(os.path.normcase(os.path.realpath(cwd)).encode()).hexdigest()[:16]
marker = os.path.join(data.get("scratchpad_dir") or os.environ.get("TEMP", "."), f"pbi_stop_nudge_{project_key}.stamp")
try:
    if time.time() - os.path.getmtime(marker) < NUDGE_EVERY:
        sys.exit(0)
except OSError:
    pass

try:
    result = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=cwd, capture_output=True, text=True, timeout=20)
    if result.returncode:
        sys.exit(0)
    st = result.stdout
except Exception:
    sys.exit(0)

hits = []
entries = iter(st.split("\0"))
for entry in entries:
    if not entry:
        continue
    status, path = entry[:2], entry[3:]
    if "R" in status or "C" in status:
        next(entries, None)  # porcelain -z lists destination, then original path.
    low = path.lower().replace("\\", "/")
    if low.endswith(WATCH) or (".report/" in low and low.endswith(".json")):
        hits.append(path)
if not hits:
    sys.exit(0)

tmdl = sum(1 for h in hits if h.endswith(".tmdl"))
rep = len(hits) - tmdl
try:
    open(marker, "w").close()
except OSError:
    pass
msg = (f"Uncommitted PBIP edits: {tmdl} TMDL + {rep} report JSON file(s). "
       f"Checkpoint before the next Desktop save/close: "
       f"{'/verify-model then ' if tmdl else ''}git commit. Next nudge in 1 h.")
print(json.dumps({"systemMessage": msg}))
sys.exit(0)
