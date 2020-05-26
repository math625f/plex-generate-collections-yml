# plex-generate-collections-yml
Used to create YML files for your existing collections in your Plex library.

This script can also automatically download all posters for the movies in your collections, as well as the collection posters.

## Installation
Start by installing the requirements using pip
```
pip install -r requirements.txt
```
Make sure to edit the config file with your correct Plex URL and Plex token, before running main.py.

## Usage
```
usage: main.py [-h] [-s SECTION] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -s SECTION, --section SECTION
                        The section index. 0 to handle all sections
  -p, --posters         Add this flag if you want to download the posters for all movies in your collection(s) as well
```
The above guide was output by writing `python main.py -h` in a terminal.
