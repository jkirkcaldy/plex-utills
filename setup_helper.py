from plexapi.server import PlexServer
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")
server = config_object["PLEXSERVER"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
films = plex.library.section(films)

print('This file will help you locate the media path that Plex sees.')
print('Running this will output a file location from your film library set in the config.ini')
print('It will only work properly if you have used the correct plex naming protocols.')
print('Searching...')

media_location = films.search()
filepath = os.path.dirname(os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file)))
print(filepath)