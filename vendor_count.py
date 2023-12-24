# ______________________________________________________________________________
#
#  reJARchiver - vendor_count.py
#
#  Outputs a list of all MIDlet vendors found in the JSON index, sorted by
#  frequency.
# ______________________________________________________________________________
#
import json, sys

def vendor_count(file_path, output_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Count the occurrences of each MIDlet vendor
    vendor_count = {}
    for obj_id, obj_data in data.items():
        vendor = obj_data.get('MIDlet-Vendor', '(unknown)')
        vendor_count[vendor] = vendor_count.get(vendor, 0) + 1

    # Create a list of dictionaries for each vendor and count
    result = [{"Vendor": vendor, "Count": count} for vendor, count in vendor_count.items()]

    # Sort the list in descending order by count
    result.sort(key=lambda x: x['Count'], reverse=True)

    # Convert list of dictionaries to just a dictionary
    result_list = {}
    for r in result:
        result_list[r["Vendor"]] = r["Count"]

    # Convert the result to JSON and write it to file
    with open(output_path, 'w') as file:
        file.write(json.dumps(result_list, indent=2))

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: vendor_count.py <index json> <output json>")
		sys.exit()
	vendor_count(sys.argv[1], sys.argv[2])