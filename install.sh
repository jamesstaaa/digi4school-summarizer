#!/usr/bin/env bash
# digi4school-summarizer — one-command installer (macOS / Linux)
# Copies the skill into ~/.claude/skills/ and installs the Python deps used for
# the Word-document output. After this, restart Claude and type /digi4school-summarizer.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/skills/digi4school-summarizer"
DEST_ROOT="$HOME/.claude/skills"
DEST="$DEST_ROOT/digi4school-summarizer"

echo "Installing digi4school-summarizer…"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "✗ Could not find skills/digi4school-summarizer/SKILL.md next to this script." >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"
rm -rf "$DEST"
cp -R "$SRC" "$DEST_ROOT/"
echo "✓ Skill installed to $DEST"

# Python deps (only needed for Word/PDF output)
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import docx, PIL" >/dev/null 2>&1; then
    echo "✓ Python deps (python-docx, Pillow) already present"
  else
    echo "Installing Python deps (python-docx, Pillow)…"
    if python3 -m pip install --user --quiet python-docx Pillow >/dev/null 2>&1; then
      echo "✓ Python deps installed"
    else
      echo "⚠ Could not auto-install Python deps. Run manually:  pip3 install python-docx Pillow"
    fi
  fi
else
  echo "⚠ python3 not found. Install Python 3, then:  pip3 install python-docx Pillow"
  echo "  (only needed for Word/PDF output — summaries in chat work without it)"
fi

echo ""
echo "Done ✅  Restart Claude, then type:  /digi4school-summarizer"
