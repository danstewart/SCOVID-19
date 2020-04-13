#!/usr/bin/env python3

# Reads all JSON files and combines the stats for the front end to draw

import os
import json

breakdown = {}
totals    = {}

BASE_PATH ='/code/SCOVID-19'
OUT_PATH = os.path.join(BASE_PATH, 'out') 
BREAKDOWN_PATH = os.path.join(BASE_PATH, 'site', 'breakdown.json')

for file in sorted(os.listdir(OUT_PATH)):
	date = os.path.splitext(file)[0]
	filepath = os.path.join(OUT_PATH, file)
	with open(filepath, 'r') as f:
		contents = f.read()
		parsed = json.loads(contents)

		totals[date] = parsed['totals']

		if 'breakdown' in parsed:
			breakdown[date] = parsed['breakdown']


output = json.dumps(
	breakdown,
	sort_keys=True,
	indent=2,
	separators=(',', ': ')
)

with open(BREAKDOWN_PATH, 'w') as f:
	f.write(output)

