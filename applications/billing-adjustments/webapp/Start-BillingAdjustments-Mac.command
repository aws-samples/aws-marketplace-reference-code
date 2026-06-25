#!/bin/bash
# Double-click this file in Finder to start the Billing Adjustments app.
# First run sets everything up automatically; later runs start instantly.

# Move to the folder this script lives in (so it works no matter where it's launched)
cd "$(dirname "$0")" || exit 1

echo "============================================================"
echo "  AWS Marketplace Billing Adjustments"
echo "============================================================"
echo ""

# 1. Find Python 3
PYTHON=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then
    if "$c" -c 'import sys; exit(0 if sys.version_info[:2] >= (3,8) else 1)' >/dev/null 2>&1; then
      PYTHON="$c"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: Python 3.8+ was not found on this Mac."
  echo ""
  echo "Please install Python from https://www.python.org/downloads/ "
  echo "then double-click this file again."
  echo ""
  read -r -p "Press ENTER to close."
  exit 1
fi

echo "Using Python: $($PYTHON --version)"

# 2. Create a private virtual environment on first run
VENV_DIR=".venv_billing"
if [ ! -d "$VENV_DIR" ]; then
  echo "First-time setup: creating environment (this happens only once)..."
  "$PYTHON" -m venv "$VENV_DIR" || { echo "Failed to create environment."; read -r -p "Press ENTER to close."; exit 1; }
fi

# 3. Activate it
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 4. Install / update dependencies (quiet; fast if already installed)
echo "Checking dependencies..."
pip install --quiet --upgrade pip >/dev/null 2>&1
pip install --quiet -r ../requirements.txt || pip install --quiet flask werkzeug "boto3>=1.42.80"

# 5. Start the app (it will open your browser automatically)
echo ""
echo "Starting the app and opening your browser..."
echo "Keep this window open while you work. Close it to stop the app."
echo ""
python app.py

# If the server stops, keep the window open so the user can read any message
read -r -p "The app has stopped. Press ENTER to close."
