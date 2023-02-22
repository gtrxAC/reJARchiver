import os
import zipfile
import py7zr
import unrar
import chardet
import hashlib
import sys

#Input: filename string
def md5sum(filename, blocksize=65536):
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

# bad_keywords: List of keywords to filter out
bad_keywords = ["andrew-lviv", "faint.ru", "masyaka", "mob.ua", "mobigama", "namobilu", "tegos.ru", "teg0s", "yurique"]

def extract_archives(file_path):
    """
    Recursively extract archives inside a zip, 7z, or rar file into subdirectories named after their parent archive,
    and print the file names of all extracted archives and files.
    """
    base_dir = os.path.splitext(os.path.basename(file_path))[0]
    os.makedirs(base_dir, exist_ok=True)

    if file_path.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            for file_info in zip_file.infolist():
                if file_info.filename.endswith('.zip') or file_info.filename.endswith('.7z') or file_info.filename.endswith('.rar'):
                    archive_path = os.path.join(base_dir, file_info.filename)
                    print(f'Extracting {file_info.filename} into {archive_path[:archive_path.rfind(".")]}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    with zip_file.open(file_info) as archive_file:
                        with open(file_info.filename, 'wb') as output_file:
                            output_file.write(archive_file.read())
                    extract_archives(file_info.filename)
                    os.remove(file_info.filename)
                    os.chdir('..')
                else:
                    file_path = os.path.join(base_dir, file_info.filename)
                    print(f'Extracting {file_info.filename} into {file_path}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    zip_file.extract(file_info)
                    os.chdir('..')

    elif file_path.endswith('.7z'):
        with py7zr.SevenZipFile(file_path, mode='r') as archive:
            for name in archive.getnames():
                if name.endswith('.zip') or name.endswith('.7z') or name.endswith('.rar'):
                    archive_path = os.path.join(base_dir, name)
                    print(f'Extracting {name} into {archive_path[:archive_path.rfind(".")]}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    archive.extract(name)
                    extract_archives(name)
                    os.remove(name)
                    os.chdir('..')
                else:
                    file_path = os.path.join(base_dir, name)
                    print(f'Extracting {name} into {file_path}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    archive.extractall()
                    os.chdir('..')

    elif file_path.endswith('.rar'):
        with unrar.RarFile(file_path, 'r') as archive:
            for entry in archive.infolist():
                if entry.filename.endswith('.zip') or entry.filename.endswith('.7z') or entry.filename.endswith('.rar'):
                    archive_path = os.path.join(base_dir, entry.filename)
                    print(f'Extracting {entry.filename} into {archive_path[:archive_path.rfind(".")]}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    archive.extract(entry.filename, path=base_dir, pwd=None)
                    extract_archives(entry)
                    os.remove(entry)
                    os.chdir('..')
                else:
                    file_path = os.path.join(base_dir, entry.filename)
                    print(f'Extracting {entry.filename} into {file_path}')
                    os.chdir(base_dir)
                    print(os.getcwd())
                    archive.extract(entry, base_dir)
                    os.chdir('..')

def explore(path):
	# Tasks to be done in a recursive function:
	# 1. If a 7z file is present, traverse every subdirectory and do these:
	# 1.1 If any form of archive is found, extract it, and then go into that subdirectory
	# 1.2 If jar is found, parse the manifest file and get the string in format:
	# MIDlet-Name (MIDlet-Version) (MIDlet-Vendor) (MD5) (List of source diectories it was found in, comma-separated, using the order from the first part)
	# 1.2.1 Get the MD5 of the jar file and store it in a dictionary with the key being the MD5 and the value being the path to the jar file
	# 1.2.2 Filter out bad keywords from the manifest by bad_keywords, if there isn't any bad keywords, continue
	# 1.2.3 If the MD5 is already present in the dictionary, add the path to the jar file to the list of paths in the dictionary
	# 1.3 If some other format is found, check if it's in the ignored_formats list. If not, add it to the list.

	#Get the directory to search for 7z, zip, jars
	search_dir = path

	#Get the subdirectories of the search directory
	subdirs = [x[0] for x in os.walk(search_dir)]

	#Get the list of files in the search directory
	files = [x[2] for x in os.walk(search_dir)]

	for subdir in subdirs:
		explore(subdir)
	
	for file in files:
		# Test if the file can be opened with zipfile and check if there is a MANIFEST.MF file
		try:
			jar = zf.ZipFile(file)
			manifest_file = manifest_find(jar)
			if manifest_file:
				_, manifest = text_decode(manifest_file)
				if manifest == None:
					continue
				manifest_dict = manifest_read(manifest)
				if manifest_dict:
					print(manifest_dict)
		except:
			continue

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: reJARchiver.py <directory>")
		sys.exit()