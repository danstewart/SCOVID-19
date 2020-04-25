# IO module

def read_file(filepath):
	contents = ''

	try:
		with open(filepath, 'r') as fh:
			contents = fh.read()
	except Exception as e:
		raise e
	
	return contents


def write_file(filepath, contents):
	try:
		with open(filepath, 'w') as fh:
			fh.write(contents)
		
		return True
	except Exception as e:
		raise e
