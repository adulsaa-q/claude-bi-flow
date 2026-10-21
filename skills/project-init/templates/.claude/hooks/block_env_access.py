"""PreToolUse hook — keep the real .env out of the model's context.

.env holds the project's live credentials (e.g. SQL_PASS). This
hook prevents (a) accidentally clobbering it and (b) its secret contents being
pulled into the model's context. .env.example (unmasked keys, no secrets) is
the safe reference for connection structure.

Read/Edit/Write/Grep on a file named .env -> blocked (exit 2).
Bash/PowerShell command that names .env -> the user is asked (scripts that load
credentials at runtime do not name the file on the command line, so this is rare).
Unreadable hook input -> blocked: a guard that cannot see the request must not allow it.
settings.json appends `|| exit 2`, so a missing python or a crash also blocks.
"""
import json
import os
import re
import sys

ENV_TOKEN = re.compile(r"(?<![\w.])\.env(?![\w.])", re.I)


def is_env(path: str) -> bool:
    return os.path.basename((path or "").replace("\\", "/").rstrip("/")).lower() == ".env"


def decision(data: dict):
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit") and is_env(ti.get("file_path")):
        return "deny"
    if tool == "Grep" and (is_env(ti.get("path")) or (ti.get("glob") or "").strip().lower() == ".env"):
        return "deny"
    if tool in ("Bash", "PowerShell") and ENV_TOKEN.search(ti.get("command") or ""):
        return "ask"
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.stderr.write("Blocked: .env guard could not read the hook input.")
        return 2
    action = decision(data)
    if action == "deny":
        sys.stderr.write(
            "Blocked: .env holds live credentials (do not read, search, edit, or "
            "clobber it). Use .env.example for the connection-key structure, or ask "
            "the user to change credentials themselves.")
        return 2
    if action == "ask":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": "This command names .env (live credentials). Allow only if "
                                        "it does not print or copy the file's contents."}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
