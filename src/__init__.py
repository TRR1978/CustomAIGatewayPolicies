
import os

def get_version():
	version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'VERSION')
	with open(version_path, 'r') as f:
		return f.read().strip()

__version__ = get_version()
