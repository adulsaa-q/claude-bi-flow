#!/bin/sh
# Install repo-tracked git hooks into .git/hooks (which git does NOT track/share).
# Run once per clone:  sh scripts/git-hooks/install.sh
root=$(git rev-parse --show-toplevel) || { echo "not a git repo" >&2; exit 1; }
hooks=$(git rev-parse --git-path hooks) || exit 1
mkdir -p "$hooks" || exit 1
cp "$root/scripts/git-hooks/pre-commit" "$hooks/pre-commit" || exit 1
chmod +x "$hooks/pre-commit" || exit 1
echo "Installed: $hooks/pre-commit (staged .env + PBIR JSON BOM guard)"
