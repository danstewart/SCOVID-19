import os
import json

def to_json(struct):
	return json.dumps(
		struct,
		sort_keys=True,
		indent=2,
		separators=(',', ': ')
	)
