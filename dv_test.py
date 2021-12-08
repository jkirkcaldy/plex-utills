from plexapi.server import PlexServer
import re
import sqlite3
from pymediainfo import MediaInfo
import json
import sys

conn = sqlite3.connect('/config/app.db')
c = conn.cursor()
c.execute("SELECT * FROM plex_utills")
config = c.fetchall()

plex = PlexServer(config[0][1], config[0][2])
films = plex.library.section(config[0][3])
var = sys.argv[1]

for i in films.search(title=var):
    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
    tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
    resolution = i.media[0].videoResolution
    file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
    m = MediaInfo.parse(file, output='JSON')
    x = json.loads(m)
    hdr_version = ""
    try:
        hdr_version = x['media']['track'][1]['HDR_Format']
    except KeyError:
        pass
    if "smpte" in str.lower(hdr_version):
        try:
            hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
        except KeyError:
            pass
    audio = ""
    while True:
        for f in range(10):
            if 'Audio' in x['media']['track'][f]['@type']:
                if 'Format_Commercial_IfAny' in x['media']['track'][f]:
                    audio = x['media']['track'][f]['Format_Commercial_IfAny']
                    if 'DTS' in audio:
                        if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                            audio = 'DTS:X'
                    break
                elif 'Format' in x['media']['track'][f]:
                    audio = x['media']['track'][f]['Format']
                    break
        if audio != "":
            break
    if hdr_version != "":
        print(i.title+" - "+hdr_version+" - "+audio)
    else:
        print(i.title+" - SDR - "+audio)
