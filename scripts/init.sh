#!/usr/bin/env bash
# Rename this scaffold into a real package. Run once, right after creating the repo
# from this template, then delete this script.
#
# Usage: scripts/init.sh <repo-name> "<one-line description>"
# Example: scripts/init.sh my-cool-tool "A cool tool that does things."
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <repo-name> \"<description>\"" >&2
  echo "Example: $0 my-cool-tool \"A cool tool that does things.\"" >&2
  exit 1
fi

export REPO_NAME="$1"
export DESCRIPTION="$2"
export IMPORT_NAME="${REPO_NAME//-/_}"

git mv src/package_name "src/${IMPORT_NAME}"

# The /e modifier evaluates the replacement as Perl code (here, just an %ENV lookup), so the
# description/name text is substituted as a literal value -- safe even if it contains
# characters (&, \, $, /) that would otherwise be special in a replacement string.
grep -rl "REPLACE_ME\|package_name" --exclude-dir=.git --exclude-dir=scripts . | while IFS= read -r file; do
  perl -pi -e 's/REPLACE_ME_DESCRIPTION/$ENV{DESCRIPTION}/ge; s/REPLACE_ME/$ENV{REPO_NAME}/ge; s/package_name/$ENV{IMPORT_NAME}/ge' "$file"
done

echo "Renamed to ${REPO_NAME} (import name: ${IMPORT_NAME})."
echo "Review the diff, run 'uv sync', then delete scripts/init.sh and commit."
