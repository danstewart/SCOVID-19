import os
import json

def to_json(struct, min=False):
	if min:
		return json.dumps(struct)

	return json.dumps(
		struct,
		sort_keys=True,
		indent=2,
		separators=(',', ': ')
	)
