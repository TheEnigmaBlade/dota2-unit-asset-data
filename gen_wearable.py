force_dl = False
only_default = False
sort_by_type = False

input_url = "https://github.com/dotabuff/d2vpkr/raw/master/dota/scripts/items/items_game.txt"
input_file = "wearables.raw.txt"
output_file = "wearables.txt"

# Download file
import os
if not os.path.isfile(input_file) or force_dl:
	print("Downloading input data... ", end="", flush=True)
	import urllib.request, shutil
	with urllib.request.urlopen(input_url) as response, open(input_file, "wb") as outfile:
		shutil.copyfileobj(response, outfile)
	print("done.")

# Parse input
import kv1
print("Parsing input data... ", end="", flush=True)
items_data = kv1.parse(input_file, encoding="utf-8")
print("done.")

# Extract items
print("Processing items... ", end="", flush=True)
_items_exclude = ["default"]

items = dict()
for item_id, item_data in items_data["items_game"]["items"].items():
	if item_id in _items_exclude:
		continue
	if "prefab" in item_data:
		prefab = item_data["prefab"]
		if (prefab == "wearable" and not only_default) or prefab == "default_item":
			item_name = item_data["name"]
			
			if prefab == "default_item":
				item_slot = "Default"
			elif "item_slot" in item_data:
				item_slot = item_data["item_slot"]
			else:
				#print("Item {} doesn't specify an item slot".format(item_id))
				item_slot = None
			
			item_heroes = set()
			if "used_by_heroes" in item_data:
				item_heroes_data = item_data["used_by_heroes"]
				for hero in item_heroes_data:
					if item_heroes_data[hero] == "1":
						if hero not in items:
							items[hero] = list()
						items[hero].append((item_id, item_name, item_slot))

# Write
with open(output_file, "w") as outfile:
	heroes = list(items.keys())
	heroes.sort()
	for hero in heroes:
		hero_items = items[hero]
		outfile.write(hero+"\n")
		
		items_sorted = sorted(hero_items, key=lambda i: (i[0] if i[2] is None else i[2]+i[0]) if sort_by_type else i[0])
		for item in items_sorted:
			outfile.write("\t{}: {} ({})\n".format(item[0], item[1], item[2]))
		
		outfile.write("\n")

print("done.")
