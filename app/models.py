from plexapi.config import reset_base_headers
from app import db


class Plex(db.Model):
    __tablename__ = 'plex_utills'
    # plex and docker config
    id = db.Column(db.Integer, primary_key=True)
    plexurl = db.Column(db.String)
    token = db.Column(db.String)
    filmslibrary = db.Column(db.String)
    library3d = db.Column(db.String)
    plexpath = db.Column(db.String)
    mountedpath = db.Column(db.String)
    # Schedules
    t1 = db.Column(db.String)
    t2 = db.Column(db.String)
   # t3 = db.Column(db.String)
    t4 = db.Column(db.String)
    t5 = db.Column(db.String)
    # Enable various settings
    backup = db.Column(db.Integer)
    posters4k = db.Column(db.Integer)
    mini4k = db.Column(db.Integer)
    hdr = db.Column(db.Integer)
    posters3d = db.Column(db.Integer)
    mini3d = db.Column(db.Integer)
    disney = db.Column(db.Integer)
    pixar = db.Column(db.Integer)
    hide4k = db.Column(db.Integer)
    transcode = db.Column(db.Integer)
    tvlibrary = db.Column(db.String)
    tv4kposters = db.Column(db.Integer)
    films4kposters = db.Column(db.Integer)
    tmdb_api = db.Column(db.String)
    tmdb_restore = db.Column(db.Integer)
    recreate_hdr = db.Column(db.Integer)
    new_hdr = db.Column(db.Integer)
    default_poster = db.Column(db.Integer)
    autocollections = db.Column(db.Integer)
    tautulli_server = db.Column(db.String)
    tautulli_api = db.Column(db.String)
    mcu_collection = db.Column(db.Integer)
    tr_r_p_collection = db.Column(db.Integer)
    audio_posters = db.Column(db.Integer)
    
    def __init__(self, plexurl, token, filmslibrary, library3d, plexpath, mountedpath, t1, t2, t4, t5, backup, posters4k, mini4k, hdr, posters3d, mini3d, disney, pixar, hide4k, transcode, tvlibrary, tv4kposters, films4kposters, tmdb_api, tmdb_restore, recreate_hdr, new_hdr, default_poster, autocollections, tautulli_server, tautulli_api, mcu_collection, tr_r_p_collection, audio_posters):
        self.plexurl = plexurl
        self.token = token
        self.filmslibrary = filmslibrary
        self.library3d = library3d
        self.plexpath = plexpath
        self.mountedpath = mountedpath
        self.t1 = t1
        self.t2 = t2
        #self.t3 = t3
        self.t4 = t4
        self.t5 = t5
        self.backup = backup
        self.posters4k = posters4k
        self.mini4k = mini4k
        self.hdr = hdr
        self.posters3d = posters3d
        self.mini3d = mini3d
        self.disney = disney
        self.pixar = pixar
        self.hide4k = hide4k
        self.transcode = transcode
        self.tvlibrary = tvlibrary
        self.tv4kposters = tv4kposters
        self.films4kposters = films4kposters
        self.tmdb_api = tmdb_api
        self.tmdb_restore = tmdb_restore
        self.recreate_hdr = recreate_hdr
        self.new_hdr = new_hdr
        self.mcu_collection = mcu_collection
        self.default_poster = default_poster
        self.autocollections = autocollections
        self.tautulli_server = tautulli_server
        self.tautulli_api    = tautulli_api
        self.tr_r_p_collection = tr_r_p_collection
        self.audio_posters = audio_posters

class Dev(db.Model):
    __tablename__ = 'plex_utills_dev'
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String)
    hdr = db.Column(db.String)
    res = db.Column(db.String)
    audio = db.Column(db.String)
