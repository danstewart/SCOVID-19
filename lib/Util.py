import os

def project_root():
	return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
