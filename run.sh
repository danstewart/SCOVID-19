#!/usr/bin/env bash

APP_ROOT=/code/SCOVID-19

today=$(date +%Y-%m-%d)

source "$APP_ROOT/venv/bin/activate"
python3 "$APP_ROOT/bin/scrape.py" > "$APP_ROOT/out/${today}.json"
python3 "$APP_ROOT/bin/combine.py"
deactivate
