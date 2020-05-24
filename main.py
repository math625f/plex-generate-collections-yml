import json
import urllib.request
from plexapi.server import PlexServer
import argparse
import yaml

parser = argparse.ArgumentParser()
# parser.add_argument("-s", "--server", type=int, help="The server index")
parser.add_argument("-s", "--section", type=str, help="The section index. 0 to handle all sections")
args = parser.parse_args()

with open('config.json') as f:
	config = json.loads(f.read())

plex = PlexServer(config['URL'], config['TOKEN'])
sections = plex.library.sections()

def parse_all():
	for sec in sections:
		parse_section(sec)

def parse_section(sec, path="./out/"):
	out = ""
	for collection in sec.collection():
		movies = {collection.title : [movie.title for movie in collection.children]}
		out = out + yaml.dump(movies) + "\n"
	with open(path + sec.title + ".yml", "w") as f:
		f.write(out)
	

if args.section is None:
	print('Please select the section from which you want to parse collections from the list below, by entering the number inside the square brackets')
	print('[0] - Parse collections from all sections')
	print()
	for section in sections:
		print('[{}] - {}'.format(section.key, section.title))
	section_selection = input()
else:
	section_selection = args.section

if section_selection != "0":
	try:
		parse_section(plex.library.sectionByID(section_selection))
	except KeyError:
		print("That's an invalid section ID! Try again with another ID:")
		print('[0] - Parse collections from all sections')
		print()
		for section in sections:
			print('[{}] - {}'.format(section.key, section.title))
		section_selection = input()
		while int(section_selection) > len(sections) or int(section_selection) < 0:
			print("Try again: ")
			section_selection = input()
		if section_selection != "0":
			parse_section(plex.library.sectionByID(section_selection))
		else:
			parse_all()
else:
	parse_all()
	