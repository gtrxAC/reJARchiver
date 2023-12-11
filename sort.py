# ______________________________________________________________________________
#
#  reJARchiver - sort.py
#
#  Moves the JARs to an output directory, sorted into folders by MIDlet name and
#  named according to the naming scheme.
# ______________________________________________________________________________
#
import os, sys, json, re, shutil

def sort(indexname, folder):
	os.makedirs(folder, exist_ok=True)
	
	with open(indexname) as indexfile:
		illegal_chars = r'[\\/:\*\?"<>\|\u0000]'
		periods_at_end = r'\.*$'
		index = json.loads(indexfile.read())
		
		for hash, jar in index.items():
			# Sanitize the fields for illegal chars just to be sure (won't be saved to the json)
			if "MIDlet-Name" in jar: jar['MIDlet-Name'] = re.sub(illegal_chars, '', jar['MIDlet-Name'])
			if "MIDlet-Vendor" in jar: jar['MIDlet-Vendor'] = re.sub(illegal_chars, '', jar['MIDlet-Vendor'])

			# Some broken JARs don't have a MIDlet-Name, just skip them
			if "MIDlet-Name" not in jar: continue

			# Make a folder for this MIDlet-Name (one folder can have many jars w same name)
			# If already exists (another jar w same name has been scanned) that's fine
			# Note: '.' at the end of a folder name isn't allowed?
			path = os.path.join(folder, jar["MIDlet-Name"])
			path = re.sub(periods_at_end, '', path)
			os.makedirs(path, exist_ok=True)

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
				# os.rename(jar["paths"][0], os.path.join(path, name))
				shutil.copy(jar["paths"][0], os.path.join(path, name))
			except:
				pass

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: sort.py <filtered indexfile> <dest folder>")
		sys.exit()
	sort(sys.argv[1], sys.argv[2])