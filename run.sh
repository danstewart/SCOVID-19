#!/usr/bin/env bash

APP_ROOT=/code/SCOVID-19

today=$(date +%Y-%m-%d)

source "$APP_ROOT/venv/bin/activate"
python3 "$APP_ROOT/SCOVID-19.py" > "$APP_ROOT/out/${today}.json"
deactivate
