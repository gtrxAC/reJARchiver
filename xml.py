# ______________________________________________________________________________
#
#  reJARchiver - xml.py
#
#  Generates an XML database to be submitted for No-Intro.
# ______________________________________________________________________________
#
import os, sys, re, json, hashlib

def calculate_sha1(file_path):
    sha1_hash = hashlib.sha1()

    with open(file_path, 'rb') as file:
        # Read the file in chunks to handle large files efficiently
        chunk = file.read(4096)
        while chunk:
            sha1_hash.update(chunk)
            chunk = file.read(4096)

    return sha1_hash.hexdigest()

def xml(indexname, folder):
	print("Not ready yet")
	return

	with open(indexname) as indexfile:
		illegal_chars = r'[\\/:\*\?"<>\|\u0000]'
		periods_at_end = r'\.*$'
		index = json.loads(indexfile.read())

		
		
		for hash, jar in index.items():
			# Some broken JARs don't have a MIDlet-Name, just skip them
			if "MIDlet-Name" not in jar: continue

			# We do some of the same parsing as we did for the sort step,
			# but we don't do any permanent changes to any files/folders.

			# Get the sanitized filename for this entry
			jar['MIDlet-Name'] = re.sub(illegal_chars, '', jar['MIDlet-Name'])
			if "MIDlet-Vendor" in jar: jar['MIDlet-Vendor'] = re.sub(illegal_chars, '', jar['MIDlet-Vendor'])

			# Get the folder name for this entry
			path = os.path.join(folder, jar["MIDlet-Name"])
			path = re.sub(periods_at_end, '', path)
			
			# If the MIDlet-Name's folder doesn't have any jars, skip
			jars = os.listdir(path)
			if not len(): continue

			# Compose the file name based on the naming scheme:
			# Midlet-Name [Midlet-Vendor] (vX.Y.Z) {MainClass1, MainClass2, ...} md5sum.jar
			name = ""
			if "MIDlet-Name" in jar: name += f"{jar['MIDlet-Name']}"
			if "MIDlet-Vendor" in jar: name += f" [{jar['MIDlet-Vendor']}]"
			if "MIDlet-Version" in jar: name += f" (v{jar['MIDlet-Version']})"

			if "MIDlet-1" in jar and len(jar["MIDlet-1"].split(",")) > 2:
				name += " {" + jar["MIDlet-1"].split(",")[2].strip()

			# Some jars have more than one midlet, get the main class of each one
			i = 2
			while f"MIDlet-{i}" in jar and len(jar[f"MIDlet-{i}"].split(",")) > 2:
				name += ", " + jar[f"MIDlet-{i}"].split(",")[2].strip()
				i += 1

			name += "} " + f"{hash}.jar"
			print(name)

			# Move the first copy of the file to the output folder with the naming scheme
			# Ignore failures (in case file is already moved)
			try:
				os.rename(jar["paths"][0], os.path.join(path, name))
			except:
				pass

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: xml.py <filtered indexfile> <sorted folder>")
		sys.exit()
	xml(sys.argv[1], sys.argv[2])