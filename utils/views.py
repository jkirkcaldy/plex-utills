from django.shortcuts import render
from posters.models import film, season, episode, show
from utils.models import Plex, advancedSettings
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Sequence
from sqlalchemy import String, Integer, Float, Boolean, Column
from sqlalchemy.orm import sessionmaker
import logging, shutil, re
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(name='flask2django')
def flask2django():
    logger.info('Migrating to Django now.')
    Base = declarative_base()
    class flaskseason_table(Base):
        __tablename__ = 'seasons'
        id = Column(Integer, primary_key=True)
        title = Column(String, index=True)
        guid = Column(String, index=True)
        poster = Column(String)
        bannered_poster = Column(String)
        checked = Column(Integer)
    class flaskep_table(Base):
        __tablename__ = 'episodes'
        id = Column(Integer, primary_key=True)
        title = Column(String, index=True)
        guid = Column(String, index=True)
        guids = Column(String, index=True)
        size = Column(String)
        res = Column(String)
        hdr = Column(String)
        audio = Column(String)
        poster = Column(String)
        bannered_poster = Column(String)
        checked = Column(Integer)
        blurred = Column(Integer)
        show_season = Column(String, index=True)
    class flaskfilm_table(Base):
        __tablename__ = 'films'
        id = Column(Integer, primary_key=True)
        title = Column(String)
        guid = Column(String)
        guids = Column(String)
        size = Column(String)
        res = Column(String)
        hdr = Column(String)
        audio = Column(String)
        poster = Column(String)
        checked = Column(Integer)
        bannered_poster = Column(String)
        url= Column(String)
    class flaskPlex(Base):
        __tablename__ = 'plex_utills'
        id = Column(Integer, primary_key=True)
        plexurl = Column(String)
        token = Column(String)
        filmslibrary = Column(String)
        library3d = Column(String)
        plexpath = Column(String)
        manualplexpath = Column(Integer)
        mountedpath = Column(String)
        t1 = Column(String)
        t2 = Column(String)
        t3 = Column(String)
        t4 = Column(String)
        t5 = Column(String)
        backup = Column(Integer)
        posters4k = Column(Integer)
        mini4k = Column(Integer)
        hdr = Column(Integer)
        posters3d = Column(Integer)
        mini3d = Column(Integer)
        disney = Column(Integer)
        pixar = Column(Integer)
        hide4k = Column(Integer)
        transcode = Column(Integer)
        tvlibrary = Column(String)
        tv4kposters = Column(Integer)
        films4kposters = Column(Integer)
        tmdb_api = Column(String)
        tmdb_restore = Column(Integer)
        recreate_hdr = Column(Integer)
        new_hdr = Column(Integer)
        default_poster = Column(Integer)
        autocollections = Column(Integer)
        tautulli_server = Column(String)
        tautulli_api = Column(String)
        mcu_collection = Column(Integer)
        tr_r_p_collection = Column(Integer)
        audio_posters = Column(Integer)
        loglevel = Column(Integer)
        manualplexpathfield = Column(String)
        skip_media_info = Column(Integer)
        spoilers = Column(Integer)
        migrated = Column(Integer)

    db_name = '/config/app.db'

    engine = create_engine('sqlite:///'+db_name)
    Session = sessionmaker(bind=engine)
    session = Session()
    Items = json.dumps({
        'films':[],
        'shows': [],
        'seasons': [],
        'episodes': []
    })
    Items = json.loads(Items)
    Config = json.loads(json.dumps({
        'config':[],
        'advanced_settings':[]
    }))
    for item in session.query(flaskseason_table).all():
        s = {}
        s['pk'] = item.id
        s['title'] = item.title
        s['guid'] = item.guid
        s['poster'] = item.poster
        s['bannered_poster'] = item.bannered_poster
        s['checked'] = False
        Items['seasons'].append(s)
    session.close()

    for item in session.query(flaskep_table).all():
        ep = {}
        ep['pk'] = item.id
        ep['title']= item.title
        ep['guid']= item.guid
        ep['guids']= item.guids
        ep['size']= item.size
        ep['res']= item.res
        ep['hdr']= item.hdr
        ep['audio']= item.audio
        ep['poster']= item.poster
        ep['bannered_poster']= item.bannered_poster
        ep['']= item.show_season
        ep['checked'] = True
        ep['blurred'] = False
        Items['episodes'].append(ep)
    session.close()

    for item in session.query(flaskfilm_table).all():
        f = {}
        f['pk'] = item.id
        f['title']= item.title
        f['guid']= item.guid
        f['guids']= item.guids
        f['size']= item.size
        f['res']= item.res
        f['hdr']= item.hdr
        f['audio']= item.audio
        f['poster']= item.poster
        f['bannered_poster']= item.bannered_poster
        f['checked'] = True
        Items['films'].append(f)
    session.close()

    for item in session.query(flaskPlex).all():
        config = {}
        advanced = {}
        config['plexurl'] = item.plexurl
        config['token'] = item.token
        config['filmslibrary'] = item.filmslibrary
        config['library3d'] = item.library3d
        advanced['plexpath'] = item.plexpath
        advanced['manualplexpath'] = item.manualplexpath
        advanced['mountedpath'] = item.mountedpath
        config['t1'] = item.t1
        config['t2'] = item.t2
        config['t3'] = item.t3
        config['t4'] = item.t4
        config['t5'] = item.t5
        config['backup'] = item.backup
        config['posters4k'] = item.posters4k
        config['mini4k'] = item.mini4k
        config['hdr'] = item.hdr
        config['posters3d'] = item.posters3d
        config['mini3d'] = item.mini3d
        config['disney'] = item.disney
        config['pixar'] = item.pixar
        config['hide4k'] = item.hide4k
        config['transcode'] = item.transcode
        config['tvlibrary'] = item.tvlibrary
        config['tv4kposters'] = item.tv4kposters
        config['films4kposters'] = item.films4kposters
        config['tmdb_api'] = item.tmdb_api
        config['tmdb_restore'] = item.tmdb_restore
        config['recreate_hdr'] = item.recreate_hdr
        config['new_hdr'] = item.new_hdr
        config['default_poster'] = item.default_poster
        config['autocollections'] = item.autocollections
        config['tautulli_server'] = item.tautulli_server
        config['tautulli_api'] = item.tautulli_api
        config['mcu_collection'] = item.mcu_collection
        config['tr_r_p_collection'] = item.tr_r_p_collection
        config['audio_posters'] = item.audio_posters
        config['manualplexpathfield'] = item.manualplexpathfield
        config['skip_media_info'] = item.skip_media_info
        config['spoilers'] = item.spoilers
        Config['config'].append(config)
        Config['advanced_settings'].append(advanced)
    session.close()

    djangoConfig = Plex.objects.get(pk=1)
    for item in Config['config']:
        for k, v in item.items():
            logger.info(f'Config: Setting {k} to: {v}')
            setattr(djangoConfig, k, v)
        djangoConfig.save()
    djangoAdvancedConfig = advancedSettings.objects.get(pk=1)
    for item in Config['advanced_settings']:
        for k, v in item.items():
            logger.info(f'Advanced Settings: Setting {k} to: {v}')
            setattr(djangoAdvancedConfig, k, v)   
        djangoAdvancedConfig.save()

    filmdb = film()
    for films in Items['films']:
        for k, v in films.items():
            print(f'Films: Setting {k} to: {v}')
            setattr(filmdb, k, v)
        filmdb.save()
    epdb = episode()
    for ep in Items['episodes']:
        for k, v in ep.items():
            #logger.info
            print(f'Episodes: Setting {k} to: {v}')
            setattr(epdb, k, v)
        epdb.save()   
    sdb = season()
    for s in Items['seasons']:
        for k, v in s.items():
            #logger.info
            print(f'Seasons: Setting {k} to: {v}')
            setattr(sdb, k, v)
        sdb.save()
    shutil.move('/config/app.db', '/config/app.db.bak')
    all_films = film.objects.all()
    for f in all_films:
        try:
            f.poster = re.sub('static/', '', f.poster)
        except: pass
        try:            
            f.bannered_poster = re.sub('static/', '', f.bannered_poster)
        except: pass
        f.save()
    all_eps = episode.objects.all()
    for ep in all_eps:
        try:
            ep.poster = re.sub('static/', '', ep.poster)
        except: pass
        try:
            ep.bannered_poster = re.sub('static/', '', ep.bannered_poster)
        except: pass
        ep.save()
    all_seasons = season.objects.all()
    for s in all_seasons:
        try:
            s.poster = re.sub('static/', '', s.poster)
        except: pass
        try:
            s.bannered_poster = re.sub('static/', '', s.bannered_poster)
        except: pass
        s.save()
