#!/bin/sh
# Full CPU artifact reproduction in a fresh workspace, including REAL4.
# Existing CSVs/raw data/manuscript outputs are never overwritten.
set -eu
exec "${PYTHON:-python3}" "$(dirname "$0")/run_all.py" "$@"
