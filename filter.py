# ______________________________________________________________________________
#
#  reJARchiver - filter.py
#
#  Uses data from the index created by index.py and removes entries that contain
#  bad keywords (often these are advertisements to sites which add unnecessary
#  modifications to JARs - we want clean JARs)
# ______________________________________________________________________________
#
import os, sys, json

# Counters
total, bad, dupe = 0, 0, 0

removelist = []

# Note: must be in lower case
bad_keywords = ["andrew-lviv", "faint.ru", "masyaka", "mob.ua", "mobigama", "namobilu", "tegos.ru", "teg0s", "yurique"]

def checkEntry(entry, hash, index):
    global bad, dupe

    entryStr = json.dumps(entry).lower()

    for keyword in bad_keywords:
        if keyword in entryStr:
            print(f"BAD: {entry['paths'][0]} has bad keyword {keyword}")

            # Python doesn't allow dictionary item removal during iteration, so
            # we need this dumb workaround of a removelist, everything in the
            # list is removed from the index after iterating
            removelist.append(hash)
            bad += 1

    # Check for dupes (paths of dupes are kept in the index file but the actual
    # files are removed)
    count = len(entry['paths'])
    if count > 1:
        print(f"DUPE: {entry['paths'][0]} has {count - 1} duplicates")
        dupe += count - 1
        for i in range(1, count):
            try:
                os.remove(entry['paths'][i])
            except:
                pass

def filterIndex(indexname):
    global total

    with open(indexname) as indexfile:
        index = json.loads(indexfile.read())

        for hash, jar in index.items():
            checkEntry(jar, hash, index)
            total += 1

    for hash in removelist: index.pop(hash)

    outname = indexname[:indexname.rfind(".")] + '_filtered.json'

    with open(outname, 'w') as out:
        out.write(json.dumps(index))
        out.close()

    print(f"Total: {total},  bad: {bad},  dupes: {dupe}")
    print(f"Wrote result to {outname}")

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: filter.py <indexfile>")
		sys.exit()
	filterIndex(sys.argv[1])