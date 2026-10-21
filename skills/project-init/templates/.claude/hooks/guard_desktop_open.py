"""Guard direct model/report edits and script execution while Desktop is open.

Claude-only tool hook; other clients must follow AGENTS.md. Process-check failure
is unknown, never evidence that Desktop is closed. Shell checks are conservative.
"""
import json
import re
import subprocess
import sys

TREE = re.compile(r"(\.SemanticModel[\\/].*\.tmdl$|\.Report[\\/].*\.json$)", re.I)
SCRIPT = re.compile(r"\.(py|ps1)\b|\b(python\w*|pwsh|powershell)\s+(-c|-command|-file)\b", re.I)
DIRECT_WRITE = re.compile(r"\b(Set-Content|Add-Content|Out-File|WriteAllText|Copy-Item|Move-Item|Remove-Item)\b", re.I)


def desktop_running():
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq PBIDesktop.exe", "/NH"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode:
            return None
        return "pbidesktop.exe" in result.stdout.lower()
    except (OSError, subprocess.SubprocessError):
        return None


def decision(data, running):
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    if running is False:
        return None
    if tool in ("Edit", "Write", "MultiEdit") and TREE.search(ti.get("file_path") or ""):
        return "deny"
    if tool in ("Bash", "PowerShell"):
        cmd = ti.get("command") or ""
        # pbi export writes disk; other simple pbi commands use the live API.
        if re.match(r"^\s*pbi\s+", cmd) and not re.search(r"export-tmdl|[;&|\n]", cmd):
            return None
        if SCRIPT.search(cmd) or DIRECT_WRITE.search(cmd) or "export-tmdl" in cmd:
            return "ask"
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        # A guard that cannot read the request must not allow it (settings.json maps exit 2 = block).
        sys.stderr.write("Blocked: Desktop guard could not read the hook input.")
        sys.exit(2)
    running = desktop_running()
    action = decision(data, running)
    if action:
        status = "running" if running else "in an unknown state (process check failed)"
        reason = (f"Power BI Desktop is {status}. On-disk model/report edits can be overwritten. "
                  "Use the live pbi API, or verify Desktop is closed before disk edits. "
                  "For a script, proceed only after confirming it is read-only or Desktop is closed. "
                  "Do not force-close Desktop.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                         "permissionDecision": action, "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    main()
