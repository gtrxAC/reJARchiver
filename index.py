# ______________________________________________________________________________
#
#  reJARchiver - index.py
#
#  Creates a JSON index of JAR files found in a directory, including their
#  hashes and manifests. This index is used for deduping and keyword filtering.
# ______________________________________________________________________________
#
import os, sys
import json, hashlib, chardet
from zipfile import ZipFile

list = {}

#Input: filename string
def md5sum(filename, blocksize=65536):
	"""Gets the MD5 hash of a file."""
	hash = hashlib.md5()
	with open(filename, "rb") as f:
		for block in iter(lambda: f.read(blocksize), b""):
			hash.update(block)
	return hash.hexdigest()

#Find the MANIFEST.MF file. If it's not found in the standard path, search for it case-insensitively.
#Input: zf object
#Output: bytes if manifest found, None if no manifest found
def manifest_find(jar):
	manifestfilepath = "META-INF/MANIFEST.MF"
	manifest_file = None
	try:
		manifest_file = jar.read(manifestfilepath)
	except KeyError:
		for i in jar.namelist():
			if i.upper() == manifestfilepath:
				manifest_file = jar.read(i)
				break
	return manifest_file

#Decode a text file into a string
#Input: bytes
#Output: (text's encoding as string, text as string) 
def text_decode(manifest_file):
	#Try to decode as UTF-8
	try:
		manifest_encoding = "UTF-8"
		manifest = manifest_file.decode(encoding=manifest_encoding)
		#If decoding as UTF-8 fails, ask chardet for help
	except UnicodeDecodeError:
		try:
			manifest_encoding = chardet.detect(manifest_file)['encoding']
			#If no encoding is detected chardet returns None, and a TypeError will be raised
			manifest = manifest_file.decode(encoding=manifest_encoding)
		#If chardet's guess fails, return the text with all non-ASCII characters escaped as a last resort
		except (UnicodeDecodeError , TypeError):
			manifest_encoding = "Unknown"
			manifest=str()
			for b in manifest_file:
				if b <= 127:
					manifest += b.to_bytes(length=1,byteorder='little').decode(encoding='ascii')
				else:
					manifest += "\\x" + "{0:x}".format(b)
	return (manifest_encoding, manifest)
	
#Read the manifest's key:value pairs onto a dictionary
#Input: string
#Output: dictionary
def manifest_read(manifest):
	#ToDo: proper error handling
	manifest_dict=dict()
	field_key=None
	for field in manifest.splitlines():
		if field != '':
			field_split = field.split(":",maxsplit=1)
			if len(field_split) == 2:
				field_key = field_split[0].encode(encoding='ascii',errors="ignore").decode().strip() #Ugly hack to clean some garbage bytes at the beginning of the file getting into the key string
				manifest_dict[field_key] = field_split[1].strip()
			elif len(field_split) == 1 :#and field_split[0][0] == " ": 
			#Handle the "split lines" quirk. https://docs.oracle.com/javase/7/docs/technotes/guides/jar/jar.html#Notes_on_Manifest_and_Signature_Files
				if not field_key:
					#~ print("Error parsing MANIFEST.MF:", jar_path)
					return None
				manifest_dict[field_key] += field_split[0].strip()
			else:
				#~ print("Error parsing MANIFEST.MF:", jar_path)
				return None
	return manifest_dict

def index(path, outfile):
	"""Creates a JSON index of JAR files based on their MD5 hashes and manifest info."""
	for dir in os.walk(path):
		[dirname, folders, files] = dir

		for file in files:
			if file.endswith('.jar'):
				filepath = os.path.join(dirname, file)
				print(f"Reading {filepath}")

				try:
					with ZipFile(filepath) as zip:
						mf = manifest_find(zip)
						if not mf:
							print("No manifest found")
							continue

						_, mf = text_decode(mf)
						mf = manifest_read(mf)

						if 'MIDlet-1' not in mf:
							print("Doesn't seem to be a J2ME midlet")
							continue

						md5 = md5sum(filepath)
						if md5 not in list:
							list[md5] = mf
							list[md5]["paths"] = []
						list[md5]["paths"].append(filepath)
				except:
					print("Invalid zip file")

	with open(outfile, 'w') as out:
		out.write(json.dumps(list))
		out.close()

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: index.py <directory> <output>")
		sys.exit()
	index(sys.argv[1], sys.argv[2])