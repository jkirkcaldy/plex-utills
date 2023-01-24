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