#gen_type = "units"
gen_type = "heroes"
force_dl = False

input_url = "https://github.com/dotabuff/d2vpkr/raw/master/dota/scripts/npc/npc_"+gen_type+".txt"
input_file = "soundset_"+gen_type+".raw.txt"
output_file = "soundset_"+gen_type+".txt"

# Download file
import os
if not os.path.isfile(input_file) or force_dl:
	print("Downloading input data... ", end="", flush=True)
	import urllib.request, shutil
	with urllib.request.urlopen(input_url) as response, open(input_file, "wb") as outfile:
		shutil.copyfileobj(response, outfile)
	print("done.")

# Extract SoundSets
print("Extracting... ", end="", flush=True)
import re
_ss_regex = re.compile("[\"']SoundSet[\"']\s*[\"']([\w\./]+)[\"']", re.IGNORECASE)
_sf_regex = re.compile("[\"']GameSoundsFile[\"']\s*[\"']([\w\./]+)[\"']", re.IGNORECASE)

_ss_exclude = ["0"]

soundsets = set()
last_soundset = None
with open(input_file, "r") as infile:
	for line in infile:
		match = _ss_regex.search(line)
		if match:
			if last_soundset is not None:
				#print("SoundSet "+last_soundset+" has no GameSoundsFile")
				if last_soundset not in _ss_exclude:
					soundsets.add((last_soundset, None))
			last_soundset = match.group(1)
		else:
			match = _sf_regex.search(line)
			if match:
				if last_soundset is None:
					#print("GameSoundsFile found with no SoundSet")
					continue
				if last_soundset not in _ss_exclude:
					soundsets.add((last_soundset, match.group(1)))
				last_soundset = None

# Process
soundsets = sorted(list(soundsets), key=lambda stup: stup[0].lower())

# Write
with open(output_file, "w") as outfile:
	outfile.write("SoundSet (GameSoundsFile)\n\n")
	for sound in soundsets:
		outfile.write("{} ({})\n".format(sound[0], sound[1]))

print("done.")
