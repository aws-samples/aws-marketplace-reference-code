#!/bin/bash
# Build the external-partner deliverable (a single zip) from tracked sources.
#
# Sources (all tracked in git):
#   partner-kit/   - authored kit files (START-HERE, walkthrough, sample input, README)
#   README.md      - the main README (common reference: input format, statuses, errors)
#   core/          - the shared engine package (used by both webapp and cli)
#   webapp/        - the web application
#   cli/           - the command-line scripts (for engineers who prefer the CLI)
#   deploy/        - Dockerfile + CloudFormation templates
#   requirements.txt
#
# Output (gitignored, regenerate any time):
#   resource/partner-kit/                       - assembled kit
#   resource/BillingAdjustments-Partner-Kit.zip - the file you deliver
#
# Usage:  ./build-partner-kit.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

OUT="resource"
KIT="$OUT/partner-kit"

echo "Cleaning $OUT/ ..."
rm -rf "$OUT"
mkdir -p "$KIT"

echo "Copying authored kit files ..."
cp partner-kit/START-HERE.md             "$KIT/START-HERE.md"
cp partner-kit/CROSS-ACCOUNT-WALKTHROUGH.md "$KIT/CROSS-ACCOUNT-WALKTHROUGH.md"
cp partner-kit/sample_input.csv          "$KIT/sample_input.csv"
cp partner-kit/README.md                 "$OUT/README.md"
cp requirements.txt                      "$KIT/requirements.txt"

echo "Copying the main README (common reference) into the kit ..."
cp README.md                             "$KIT/README.md"

echo "Copying application source ..."
cp -R core   "$KIT/core"
cp -R webapp "$KIT/webapp"
cp -R deploy "$KIT/deploy"
cp -R cli    "$KIT/cli"

echo "Stripping build artifacts / local files ..."
rm -rf "$KIT/webapp/dist" "$KIT/webapp/dist_package" "$KIT/webapp/build" \
       "$KIT/webapp/jobs" "$KIT/webapp/uploads" "$KIT/webapp/__pycache__" \
       "$KIT/webapp/.venv_billing" 2>/dev/null || true
# CLI: drop caches, generated outputs, and any real input data (keep the dummy sample)
rm -rf "$KIT/cli/__pycache__" 2>/dev/null || true
rm -f "$KIT/cli/"adjustment_results_*.json "$KIT/cli/"list_adjustment_requests_*.csv 2>/dev/null || true
find "$KIT/cli/adjustmentFiles" -type f ! -name 'sample_company.csv' -delete 2>/dev/null || true
find "$KIT" -name ".DS_Store" -delete 2>/dev/null || true
find "$KIT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f "$KIT/webapp/"*.spec "$KIT/webapp/_test"*.py "$KIT/webapp/_livetest.txt" 2>/dev/null || true

echo "Creating zip ..."
( cd "$OUT" && zip -r -X BillingAdjustments-Partner-Kit.zip partner-kit -x "*.DS_Store" >/dev/null )

echo ""
echo "Done:"
echo "  $OUT/BillingAdjustments-Partner-Kit.zip   <- deliver this file"
echo "  $OUT/partner-kit/                          <- unzipped contents (for review)"
echo ""
echo "Deliver the zip via a secure channel (e.g. an S3 pre-signed link or internal"
echo "file share). Do not commit it to git; regenerate with this script when sources change."
