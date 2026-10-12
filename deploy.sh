#!/usr/bin/env bash
# Build nazm.dev from the *committed* docs at a git ref (default HEAD) and deploy it.
# Reads the repo only through `git archive`: never touches its working tree or index.
#   ./deploy.sh            build HEAD and deploy
#   ./deploy.sh <ref>      build another commit/tag
#   NO_DEPLOY=1 ./deploy.sh  build only (output in build/book)
set -euo pipefail

# Machine-specific settings live in deploy.env (git-ignored): REPO, HOST, WEBROOT.
[[ -f "$(dirname "$0")/deploy.env" ]] && source "$(dirname "$0")/deploy.env"
REPO="${REPO:-../nazm}"
HOST="${HOST:-}"
WEBROOT="${WEBROOT:-/var/www/nazm.dev}"
REF="${1:-HEAD}"
cd "$(dirname "$0")"

SHA=$(git -C "$REPO" rev-parse --short "$REF^{commit}")
rm -rf build && mkdir -p build/snapshot
git -C "$REPO" archive "$REF" docs README.md | tar -x -C build/snapshot
# Drop internal pages before prep, so links to them render as plain text.
grep -vE '^(#|$)' exclude.txt | while read -r f; do rm "build/snapshot/docs/$f"; done
python3 prep.py build/snapshot build/src
cp SUMMARY.md build/src/SUMMARY.md
printf '\n---\n\n*Built from commit `%s`.*\n' "$SHA" >> build/src/README.md

bin/mdbook build
echo "built $SHA -> build/book"

if [[ -z "${NO_DEPLOY:-}" ]]; then
  [[ -n "$HOST" ]] || { echo "set HOST (the ssh host) in deploy.env" >&2; exit 2; }
  rsync -az --delete build/book/ "$HOST:$WEBROOT/"
  echo "deployed $SHA -> https://nazm.dev"
fi
