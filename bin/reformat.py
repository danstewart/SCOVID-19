#!/usr/bin/env python3

# Reads all JSON files and reformats them to keep them the same

import os
import re
import json

def clean_int(string):
	if not string: return 0
	if string == '*' or string == '<5': return '<5' # A * represents less than 5 cases

	clean = str(string).strip().replace(u'\u00a0', ' ')
	clean = re.sub('\D', '', clean)

	try:
		return int(clean)
	except:
		return 0


outpath = '/code/SCOVID-19/data'
for file in sorted(os.listdir(outpath)):
	filepath = os.path.join(outpath, file)

	with open(filepath, 'r+') as f:
		contents = f.read()
		parsed   = json.loads(contents)

		for total in parsed['totals']:
			parsed['totals'][total] = clean_int(parsed['totals'][total])

		if 'breakdown' in parsed:
			for location in parsed['breakdown']:
				for cat in parsed['breakdown'][location]:
					parsed['breakdown'][location][cat] = clean_int(parsed['breakdown'][location][cat])

		formatted = json.dumps(
			parsed,
			sort_keys=True,
			indent=2,
			separators=(',', ': ')
		)

		# print(formatted)

		f.seek(0)
		f.write(formatted)
		f.truncate()
		f.close()
