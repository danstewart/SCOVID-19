#!/usr/bin/env bash

[[ -z $PROJECT_ROOT ]] && PROJECT_ROOT="$( cd "$(dirname "$0")/.." >/dev/null 2>&1 ; pwd -P )"

# Load the .env
source "$PROJECT_ROOT/src/.env"

today=$(date +%Y-%m-%d)

source "$PROJECT_ROOT/venv/bin/activate"
python3 "$PROJECT_ROOT/src/scrape.py" > "$PROJECT_ROOT/data/${today}.json"
python3 "$PROJECT_ROOT/src/site-gen.py"
deactivate

terser --compress --mangle --output "$PROJECT_ROOT/site/script.js" -- "$PROJECT_ROOT/site/script.js"
