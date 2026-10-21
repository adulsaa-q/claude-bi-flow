"""Reject staged credentials and BOM-bearing report JSON, including renames.

Credentials: any file named .env, plus credential-shaped content in any staged
text file (KEY=value for password/secret/token keys, connection-string passwords,
private-key blocks). Values that are references or placeholders pass ($VAR, {x},
<x>, quotes, fixture/example/fake...). Findings print path:line only, never the
value. `python check_staged.py --all` scans every tracked file (audit mode).
"""
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

BROAD = r"(pass|pwd|secret|token|api[_-]?key|private key)"
CREDENTIAL = re.compile(
    r"(?i)(?:^|[^A-Za-z0-9])((?:[A-Z0-9_]*_)?(?:PASS(?:WORD)?|PASSWD|PWD|SECRET|TOKEN|API_?KEY))"
    r"[ \t]*[=:][ \t]*([^\s;'\"`$<{(%\[,)]{4,})(?=$|[\s;'\"`,)])")  # not followed by ( or [ = code
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
PLACEHOLDER = re.compile(r"(?i)fixture|example|fake|dummy|placeholder|changeme|redacted|xxx|\*\*\*|your[_-]|test")


def git(*args):
    return subprocess.run(["git", "--literal-pathspecs", *args], capture_output=True)


def secret_lines(paths, cached=True):
    """[(path, line_no)] of credential-shaped lines; None if git grep failed."""
    found = []
    for start in range(0, len(paths), 200):
        batch = paths[start:start + 200]
        args = ["grep", "-n", "-I", "-i", "-z", "-E", "-e", BROAD, "--"] + batch
        result = git(*(args[:1] + (["--cached"] if cached else []) + args[1:]))
        if result.returncode not in (0, 1):
            return None
        for record in result.stdout.split(b"\n"):
            parts = record.split(b"\0", 2)
            if len(parts) != 3:
                continue
            path, number, text = os.fsdecode(parts[0]), parts[1].decode(), parts[2].decode("utf-8", "replace")
            hit = PRIVATE_KEY.search(text) or next(
                (m for m in CREDENTIAL.finditer(text) if not PLACEHOLDER.search(m.group(2))), None)
            if hit:
                found.append((path, int(number)))
    return found


def main():
    if sys.argv[1:] == ["--all"]:
        tracked = [os.fsdecode(p) for p in git("ls-files", "-z").stdout.split(b"\0") if p]
        hits = secret_lines(tracked)
        for path, number in hits or []:
            print(f"{ascii(path)}:{number}")
        return 2 if hits is None else (1 if hits else 0)
    result = git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT")
    if result.returncode:
        print("BLOCKED: cannot inspect the Git index", file=sys.stderr)
        return 2
    paths = [os.fsdecode(p) for p in result.stdout.split(b"\0") if p]
    bad = [p for p in paths if PurePosixPath(p).name.casefold() == ".env"]
    reports = [p for p in paths if p.casefold().endswith(".json") and (
        any(part.casefold().endswith((".report", ".semanticmodel")) for part in PurePosixPath(p).parts)
        or PurePosixPath(p).name in ("visual.json", "page.json", "pages.json", "report.json")
        or "bookmarks" in PurePosixPath(p).parts)]
    batch, length = [], 0
    for path in reports + [None]:
        if batch and (path is None or length + len(path) > 16000):
            result = git("grep", "--cached", "-l", "-z", "-a", "-e", "^\ufeff", "--", *batch)
            if result.returncode not in (0, 1):
                print("BLOCKED: staged JSON scan failed", file=sys.stderr)
                return 2
            bad.extend(os.fsdecode(p) for p in result.stdout.split(b"\0") if p)
            batch, length = [], 0
        if path is not None:
            batch.append(path)
            length += len(path) + 3
    secrets = secret_lines(paths)
    if secrets is None:
        print("BLOCKED: staged secret scan failed", file=sys.stderr)
        return 2
    if bad or secrets:
        print("BLOCKED: staged .env, credential-shaped content or BOM-bearing PBIR JSON:", file=sys.stderr)
        for path in bad:
            print("  " + ascii(path), file=sys.stderr)
        for path, number in secrets:
            print(f"  {ascii(path)}:{number} (credential-shaped value; value not shown)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
