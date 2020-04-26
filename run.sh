#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Load the .env
source "$SCRIPTPATH/.env"

today=$(date +%Y-%m-%d)

source "$PROJECT_ROOT/venv/bin/activate"
python3 "$PROJECT_ROOT/bin/scrape.py" > "$PROJECT_ROOT/data/${today}.json"
python3 "$PROJECT_ROOT/bin/site-gen.py"
deactivate
