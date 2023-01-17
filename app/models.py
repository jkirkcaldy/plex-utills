from app import db


class Plex(db.Model):
    __tablename__ = 'plex_utills'
    __bind_key__ = 'db1'
    # plex and docker config
    id = db.Column(db.Integer, primary_key=True)
    plexurl = db.Column(db.String)
    token = db.Column(db.String)
    filmslibrary = db.Column(db.String)
    library3d = db.Column(db.String)
    plexpath = db.Column(db.String)
    manualplexpath = db.Column(db.Integer)
    mountedpath = db.Column(db.String)
    # Schedules
    t1 = db.Column(db.String)
    t2 = db.Column(db.String)
    t3 = db.Column(db.String)
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
    loglevel = db.Column(db.Integer)
    manualplexpathfield = db.Column(db.String)
    skip_media_info = db.Column(db.Integer)
    spoilers = db.Column(db.Integer)
    
    def __init__(self, plexurl, token, filmslibrary, library3d, plexpath, mountedpath, t1, t2, t4, t5, backup, posters4k, mini4k, hdr, posters3d, mini3d, disney, pixar, hide4k, transcode, tvlibrary, tv4kposters, films4kposters, tmdb_api, tmdb_restore, recreate_hdr, new_hdr, default_poster, autocollections, tautulli_server, tautulli_api, mcu_collection, tr_r_p_collection, audio_posters, loglevel, manualplexpath, manualplexpathfield, skip_media_info, spoilers):
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
        self.loglevel = loglevel
        self.manualplexpath = manualplexpath
        self.manualplexpathfield = manualplexpathfield
        self.skip_media_info = skip_media_info
        self.spoilers = spoilers

class film_table(db.Model):
    __tablename__ = 'films'
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    guid = db.Column(db.String)
    guids = db.Column(db.String)
    size = db.Column(db.String)
    res = db.Column(db.String)
    hdr = db.Column(db.String)
    audio = db.Column(db.String)
    poster = db.Column(db.String)
    checked = db.Column(db.Integer)
    bannered_poster = db.Column(db.String)
    url= db.Column(db.String)
    



    def to_dict(self):
        rerun = '/rerun-posters4k/'+self.guid
        rerun_btn =  """<a href="""+rerun+""" class="btn btn-secondary btn-icon-split" id="rerun">
            <span class="icon text-white-50">
              <i class="fas fa-undo-alt"></i>
          </span>
        </a>
        """
        #<span class="text">"""+self.title+"""</span>
        #restore = '/restore/film/'+self.guid
        #restore_btn =  """<a href="""+restore+""" class="btn btn-secondary btn-icon-split" id="rerun">
        #    <span class="icon text-white-50">
        #      <i class="fas fa-undo-alt"></i>
        #  </span>

        #</a>
        #"""
        delete = '/delete_row/film/'+self.guid
        delete_btn = """<a href="""+delete+""" class="btn btn-danger btn-icon-split" id="rerun">
            <span class="icon text-white-50">
              <i class="fas fa-exclamation-triangle"></i>
          </span>
        </a>
        """
        try:
            url_link = """<a href="""+self.url+""">"""+self.title+"""</a>"""
        except:
            url_link = self.title
        #title = 
        if self.bannered_poster == None:
            return {
            'title': rerun_btn,
            'res': self.res,
            'hdr': self.hdr,
            'audio': self.audio,
            'poster': "<a href='restore/film/"+self.guid+"'><img height=100px src='"+self.poster+"'></a>",
            'checked': self.checked,
            'bannered_poster': "<a href='restore/bannered_film/"+self.guid+"'><img height=100px src=''></a>" ,               
            'delete': delete_btn,
            'url': url_link
            }
        elif self.bannered_poster != None:
            return {
                'title': rerun_btn,
                'res': self.res,
                'hdr': self.hdr,
                'audio': self.audio,
                'poster': "<a href='restore/film/"+self.guid+"'><img    height=100px src='"+self.poster+"'></a>",
                'checked': self.checked,
                'bannered_poster': "<a href='restore/bannered_film/"+self.guid  +"'><img height=100px src='"+self.bannered_poster+"'></a>", 
                'delete': delete_btn,
                'url': url_link              
            }

class ep_table(db.Model):
    __tablename__ = 'episodes'
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    guid = db.Column(db.String, index=True)
    guids = db.Column(db.String, index=True)
    size = db.Column(db.String)
    res = db.Column(db.String)
    hdr = db.Column(db.String)
    audio = db.Column(db.String)
    poster = db.Column(db.String)
    bannered_poster = db.Column(db.String)
    checked = db.Column(db.Integer)
    blurred = db.Column(db.Integer)
    show_season = db.Column(db.String, index=True)

    def to_dict(self):
        poster = "<a href='restore/episode/"+self.guid+"'><img height=100px src='"+self.poster+"'></a>"
        rerun = '/rerun-tv-posters/'+self.guid
        restore_btn =  """<a href="""+rerun+""" class="btn btn-secondary btn-icon-split" id="rerun">
            <span class="icon text-white-50">
              <i class="fas fa-undo-alt"></i>
          </span>
            <span class="text">"""+self.title+"""</span>
        </a>
        """
        delete = '/delete_row/episode/'+self.guid
        delete_btn = """<a href="""+delete+""" class="btn btn-danger btn-icon-split" id="rerun">
            <span class="icon text-white-50">
              <i class="fas fa-exclamation-triangle"></i>
          </span>
        </a>
        """
        if self.bannered_poster == None:
            return {
                'show_season': self.show_season,
                'title': restore_btn,
                'res': self.res,
                'hdr': self.hdr,
                'audio': self.audio,
                'poster': poster,
                'bannered_poster': "<a href='restore/bannered_poster/"+self.guid+"'><img height=100px src=''></a>",
                'checked': self.checked,
                'blurred': self.blurred,
                'delete': delete_btn
            }
        else:
            bannered_poster = "<a href='restore/episode/"+self.guid+"'><img height=100px src='"+self.bannered_poster+"'></a>"
            return {
                'show_season': self.show_season,
                'title': restore_btn,
                'res': self.res,
                'hdr': self.hdr,
                'audio': self.audio,
                'poster': poster,
                'bannered_poster': bannered_poster,
                'checked': self.checked,
                'blurred': self.blurred,
                'delete': delete_btn
            }            

class season_table(db.Model):
    __tablename__ = 'seasons'
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    guid = db.Column(db.String, index=True)
    poster = db.Column(db.String)
    bannered_season = db.Column(db.String)
    checked = db.Column(db.Integer)

    def to_dict(self):
        delete = '/delete_row/season/'+self.guid
        delete_btn = """<a href="""+delete+""" class="btn btn-danger btn-icon-split" id="rerun">
            <span class="icon text-white-50">
              <i class="fas fa-exclamation-triangle"></i>
          </span>
        </a>
        """
        bannered_poster = "<a href='restore/bannered_season/"+self.guid+"'><img height=100px src='"+self.bannered_season+"'></a>"
        poster = "<a href='restore/season/"+self.guid+"'><img height=100px src='"+self.poster+"'></a>"
        return {
            'title': self.title,
            'poster': poster,
            'bannered_season': bannered_poster,
            'checked': self.checked,
            'delete': delete_btn
        }        