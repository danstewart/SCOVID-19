import os
import json

def project_root():
	return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

def to_json(struct):
	return json.dumps(
		struct,
		sort_keys=True,
		indent=2,
		separators=(',', ': ')
	)
