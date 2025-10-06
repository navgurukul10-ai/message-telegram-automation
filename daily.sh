#!/bin/bash
# Daily Run Wrapper - Easy command!
cd "$(dirname "$0")"
python3 scripts/daily_run.py "$@"

