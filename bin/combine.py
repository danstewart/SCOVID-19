#!/usr/bin/env python3

# Reads all JSON files and combines the stats for the front end to draw

import os
import json

breakdown = {}
totals    = {}

outpath = '/code/SCOVID-19/out'
for file in sorted(os.listdir(outpath)):
	date = os.path.splitext(file)[0]
	filepath = os.path.join(outpath, file)
	with open(filepath, 'r') as f:
		contents = f.read()
		parsed = json.loads(contents)

		totals[date] = parsed['totals']

		if 'breakdown' in parsed:
			breakdown[date] = parsed['breakdown']


# TODO: Write to file
print(json.dumps(
	breakdown,
	sort_keys=True,
	indent=2,
	separators=(',', ': ')
))
