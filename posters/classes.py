class Film:
    def __init__(self, title, guid, poster, backup_poster):
        self.title = title
        self.guid = guid
        self.poster = poster
        self.backup_poster = backup_poster
class Episode:
    def __init__(self, title, parentTitle, grandparentTitle, guid, poster, backup_poster, parent_poster, parent_guid):
        self.title = title
        self.parentTitle = parentTitle
        self.grandparentTitle = grandparentTitle
        self.guid = guid
        self.poster = poster
        self.backup_poster = backup_poster 
        self.parent_poster = parent_poster 
        self.parent_guid = parent_guid
class Season:
    def __init__(self, title, parentTitle, guid, poster, backup_poster, parent_poster, parent_guid):
        self.title = title
        self.parentTitle = parentTitle
        self.guid = guid
        self.poster = poster
        self.backup_poster = backup_poster  
        self.parent_poster = parent_poster 
        self.parent_guid = parent_guid
class Shows:
    def __init__(self, title, guid, poster, backup_poster):
        self.title = title
        self.guid = guid
        self.poster = poster
        self.backup_poster = backup_poster        
class Banners:
    def __init__(self, wide_banner, mini_banner, hdr_banner, audio_banner):
        self.wide_banner = wide_banner
        self.mini_banner = mini_banner
        self.hdr_banner = hdr_banner
        self.audio_banner = audio_banner
class film_processing:
    def __init__(self, title, guid, guids, size, resolution, hdr, audio, file):
        self.title = title
        self.guid = guid
        self.guids = guids
        self.size = size
        self.resolution = resolution
        self.hdr = hdr
        self.audio = audio
        self.file = file

class show_processing:
    def __init__(self, title, guid, guids, resolution, hdr):
        self.title = title
        self.guid = guid
        self.guids = guids
        self.resolution = resolution
        self.hdr = hdr


class tv_processing:
    def __init__(self, title, guid, guids, show, episode_number, season_number, size, resolution, hdr, audio, file):
        self.title = title
        self.guid = guid
        self.guids = guids
        self.show = show
        self.episode_number = episode_number
        self.season_number = season_number
        self.size = size
        self.resolution = resolution
        self.hdr = hdr
        self.audio = audio
        self.file = file

