import json
import requests
from plexapi.server import PlexServer
import argparse
import yaml
import os
from tqdm import tqdm

#Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--section", type=str, help="The section index. 0 to handle all sections")
parser.add_argument("-p", "--posters", action='store_true', help="Add this flag if you want to download the posters for all movies in your collection(s) as well")
args = parser.parse_args()


# Load config and setup the plex instance
with open('config.json') as f:
	config = json.loads(f.read())
try:
	plex = PlexServer(config['URL'], config['TOKEN'])
except:
	print("An error occured with connecting to your plex instance. Ensure that your Plex is online, and that your config file is configured correctly")
	exit()
sections = plex.library.sections()


# Returns a valid filename representation of a given string
def string_to_valid_filename(str):
	return ''.join(c for c in str if c.isalnum() or c in ['\'', '_', '-', ',', ' '])


# Downloads an image from Plex, by utilizing the URL and Token from the config. 
# Thumb is image location in the plex xml api, and file_name is what it will be saved as.
#  Collection title is used to divide collections into folders
def download_image(thumb, file_name, collection_title):
	collection_title = string_to_valid_filename(collection_title)
	file_name = string_to_valid_filename(file_name)
	if not os.path.exists('./out/{}_posters'.format(collection_title)):
		os.mkdir('./out/{}_posters'.format(collection_title))
	with open("./out/{}_posters/{}.jpg".format(collection_title, file_name), 'wb') as out_image:
		q_or_a = "&" if len(thumb.split("?")) > 1 else "?" #Collection poster usually don't have any get attributes set, while it's the opposite for movie posters
		response = requests.get('{}{}{}X-Plex-Token={}'.format(config['URL'], thumb, q_or_a, config['TOKEN']), stream=True)
		if not response.ok:
			print('The following error occured while attempting to download the poster for {}'.format(file_name))
			print(response)
		
		for block in response.iter_content(1024):
			if not block:
				break
			out_image.write(block)


# Parse all section
def parse_all():
	for sec in sections:
		parse_section(sec)
	


# Parse a given section
def parse_section(sec, path="./out/"):
	total_movies = 0
	for i in sec.collection():
		total_movies = total_movies + len(i.children)
	pbar = tqdm(total=total_movies)
	pbar.set_description(sec.title)
	out = ""
	for collection in sec.collection():
		movies = {collection.title : [movie.title for movie in collection.children]}
		out = out + yaml.dump(movies) + "\n"
		if args.posters:
			download_image(collection.thumb, '__{}-collection__'.format(collection.title), collection.title)
			for movie in collection.children:
				download_image(movie.posters()[0].thumb, movie.title, collection.title)
				pbar.update(1)
		else:
			pbar.update(len(collection.children))
	with open(path + sec.title + ".yml", "w") as f:
		f.write(out)
	pbar.close()
	

# It's messy, I know - but it works
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
	