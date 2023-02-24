import os, sys, shutil
from zipfile import ZipFile
from unrar.rarfile import RarFile

def extract(path: str):
	"""Extracts a ZIP/7Z/RAR archive to a subdirectory."""
	try:
		extpath = path + '_ext/'
		if path.endswith('.zip'):
			with ZipFile(path) as zip:
				zip.extractall(extpath)
		elif path.endswith('.7z'):
			# py7zr fails on archives containing illegal filenames, so we use the CLI tool
			# On Linux, install it with package manager, on Windows an exe is provided
			os.system(f"7za x -y -o{extpath} {path}")
		elif path.endswith('.rar'):
			with RarFile(path) as rar:
				rar.extractall(extpath)
		return extpath
	except:
		print(f"Failed to extract {path}")
		shutil.rmtree(extpath, True)
		return None

def recursive_extract(path: str):
	if path is None: return

	for dir in os.walk(path):
		[dirname, folders, files] = dir

		for file in files:
			if file.endswith(('.zip', '.7z', '.rar')):
				filepath = os.path.join(dirname, file)
				print(f"extracting {filepath}")
				recursive_extract(extract(filepath))

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: extract.py <directory>")
		sys.exit()
	recursive_extract(sys.argv[1])