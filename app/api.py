import re
from flask import render_template, flash, request, redirect, send_file
from app import app, db
from app.models import Plex, film_table, ep_table, season_table
import threading
import datetime
import os
import requests
import shutil
from app import scripts 
from app.schedule import update_scheduler
from app.routes import log, version
from plexapi.server import PlexServer

date = datetime.datetime.now()
date = date.strftime("%y.%m.%d-%H%M")

def get_library(lib, plexserver):
    log.debug(lib)
    n = len(lib)
    if n <= 2:
        try:
            for l in range(n):
                films = plexserver.library.section(lib[l])
                db.session.close()
                return films
        except IndexError:
            pass
def get_poster(i, table):
    guid = str(i.guid)
    imgdir = './app/static/img/tmp/'
    imgdir_exists = os.path.exists(imgdir)
    if imgdir_exists == False:
        os.mkdir('./app/static/img/tmp')
    #log.debug(i.media[0].parts[0].file)
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    if 'movie' in guid:
        fname = re.sub('plex://movie/', '', guid)+'.png'
    elif 'season' in guid:
        fname = re.sub('plex://season/', '', guid)+'.png'
    elif 'episode' in guid:
        fname = re.sub('plex://episode/', '', guid)+'.png'
    filename = "poster.png"
    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f) 
    shutil.copy(filename, './app/static/img/tmp/'+fname)
    r = table.query.filter(table.guid == guid).all()
    if r:
        backup_poster = r[0].poster
    else:
        backup_poster = '/static/img/404/poster_not_found.png'
    db.session.close()
    return backup_poster, fname

##### DATABASE TASKS #########

@app.route('/delete_row/<path:var>')
def run_delete_row(var=''):
    scripts.delete_row(app, var)
    message = 'Deleted row'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)

@app.route('/restore/film/<path:var>')
def restore_poster(var=""):
    scripts.restore_single(var)
    message = 'Sent poster to be restored.'
    config = Plex.query.filter(Plex.id == '1')
    lib = config[0].filmslibrary.split(',')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    n = len(lib)
    if n >=2:
        for l in range(n):
            library = get_library(l, plexserver)
    else:
        library = get_library(lib, plexserver)
    for i in library.search(guid=var):
        print(i)
        poster = get_poster(i, film_table)
        poster = '/static/img/tmp/'+poster[1]
    return render_template('result.html', message=message, pagetitle='Restored', version=version, poster=poster)

@app.route('/restore/episode/<path:var>')
def restore_episode_poster(var=""):
    scripts.restore_episode_from_database(app, var)
    message = 'Sent poster to be restored.'
    config = Plex.query.filter(Plex.id == '1')
    lib = config[0].tvlibrary.split(',')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    n = len(lib)
    if n >=2:
        for l in range(n):
            library = get_library(l, plexserver)
    else:
        library = get_library(lib, plexserver)
    for i in library.search(guid=var, libtype='episode'):
        poster = get_poster(i, ep_table)
        poster = '/static/img/tmp/'+poster[1]
    return render_template('result.html', message=message, pagetitle='Restored', version=version, poster=poster)

@app.route('/restore/season/<path:var>')
def restore_season_poster(var=""):
    scripts.restore_single_season(app, var)
    message = 'Sent poster to be restored.'
    config = Plex.query.filter(Plex.id == '1')
    lib = config[0].tvlibrary.split(',')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    n = len(lib)
    if n >=2:
        for l in range(n):
            library = get_library(l, plexserver)
    else:
        library = get_library(lib, plexserver)
    for i in library.search(guid=var, libtype='season'):
        print(i)
        poster = get_poster(i, season_table)
        poster = '/static/img/tmp/'+poster[1]
    return render_template('result.html', message=message, pagetitle='Restored', version=version, poster=poster)

@app.route('/restore/bannered_episode/<path:var>')
def restore_bannerred_episode_poster(var=""):
    msg = scripts.restore_single_bannered_episode(app, var)
    config = Plex.query.filter(Plex.id == '1')
    lib = config[0].tvlibrary.split(',')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    n = len(lib)
    if n >=2:
        for l in range(n):
            library = get_library(l, plexserver)
    else:
        library = get_library(lib, plexserver)
    for i in library.search(guid=var, libtype='episode'):
        print(i)
        poster = get_poster(i, ep_table)
        poster = '/static/img/tmp/'+poster[1]
    if 'error' not in str.lower(msg):
        return render_template('result.html', message=msg, pagetitle='Restored', version=version, poster=poster)
    else:
        return render_template('result.html', message=msg, pagetitle='Error', version=version, poster=poster)

@app.route('/restore/bannered_season/<path:var>')
def restore_bannerred_season_poster(var=""):
    msg = scripts.restore_single_bannered_season(app, var)
    config = Plex.query.filter(Plex.id == '1')
    lib = config[0].tvlibrary.split(',')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    n = len(lib)
    if n >=2:
        for l in range(n):
            library = get_library(l, plexserver)
    else:
        library = get_library(lib, plexserver)
    for i in library.search(guid=var, libtype='season'):
        print(i)
        poster = get_poster(i, season_table)
        poster = '/static/img/tmp/'+poster[1]
    if 'error' not in str.lower(msg):
        return render_template('result.html', message=msg, pagetitle='Restored', version=version, poster=poster)
    else:
        return render_template('result.html', message=msg, pagetitle='Error', version=version, poster=poster)

@app.route('/restore/bannered_film/<path:var>')
def restore_bannerred_poster(var=""):
    msg = scripts.restore_single_bannered(app, var)
    print(msg)
    if 'error' not in str.lower(msg):
        return render_template('result.html', message=msg, pagetitle='Restored', version=version)
    else:
        return render_template('result.html', message=msg, pagetitle='Error', version=version)

@app.route('/delete_database')
def delete_database():
    import sqlite3
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    query1 = """DROP TABLE films
        """
    table = """CREATE TABLE "films" (
            	"ID"	INTEGER NOT NULL UNIQUE,
            	"Title"	TEXT NOT NULL,
            	"GUID"	TEXT NOT NULL,
            	"GUIDS"	TEXT NOT NULL,
            	"size"	TEXT,
            	"res"	TEXT,
            	"hdr"	TEXT,
            	"audio"	TEXT,
            	"poster"	TEXT NOT NULL,
            	"checked"	INTEGER,
                "bannered_poster" TEXT,
                "url" TEXT,
            	PRIMARY KEY("ID" AUTOINCREMENT)
            ); """
    c.execute(query1)
    c.execute(table)
    conn.commit()
    c.close()
    file_paths = '/config/backup/films/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f) 
    file_paths = '/config/backup/bannered_films/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f)                 
    return redirect('/films')

@app.route('/delete_tv_database')
def delete_tv_database():
    import sqlite3
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    query1 = """DROP TABLE episodes
        """
    table = """CREATE TABLE "episodes" (
            	"ID"	INTEGER NOT NULL UNIQUE,
                "show_season" TEXT,
            	"Title"	TEXT NOT NULL,
            	"GUID"	TEXT NOT NULL,
            	"GUIDS"	TEXT NOT NULL,
            	"size"	TEXT,
            	"res"	TEXT,
            	"hdr"	TEXT,
            	"audio"	TEXT,
            	"poster"	TEXT NOT NULL,
                "bannered_poster" TEXT,
            	"checked"	INTEGER,
                "blurred"    INTEGER,
            	PRIMARY KEY("ID" AUTOINCREMENT)
            ); """
    c.execute(query1)
    c.execute(table)
    conn.commit()
    c.close()

    file_paths = '/config/backup/tv/episodes/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f)
    file_paths = '/config/backup/tv/bannered_episodes/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f)
    return redirect('/episodes')

@app.route('/delete_season_database')
def delete_season_database():
    import sqlite3
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    query1 = """DROP TABLE seasons
        """
    table = """CREATE TABLE "seasons" (
                    	"ID"	INTEGER NOT NULL UNIQUE,
                    	"Title"	TEXT NOT NULL,
                    	"GUID"	TEXT NOT NULL,
                        "poster" TEXT,
                        "bannered_poster" TEXT,
                        "checked" INTEGER,
                    	PRIMARY KEY("ID" AUTOINCREMENT)
                    ); """
    c.execute(query1)
    c.execute(table)
    conn.commit()
    c.close()

    file_paths = '/config/backup/tv/seasons/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f)
    file_paths = '/config/backup/tv/bannered_seasons/'
    for root, dirs, files in os.walk(file_paths):
        for filename in files:
            f = filename
            if f.endswith('.png'):
                os.remove(file_paths+f)

    return redirect('/seasons')

@app.route('/export_support')
def export_support():

    def export_config():
        import csv
        import shutil
        f = open('/logs/support.csv', 'w')
        out = csv.writer(f)
        out.writerow(['plexurl', 'filmslibrary', 'library3d' ,'plexpath', 'manualplexpath', 'mountedpath', 'backup', 'posters4k', 'mini4k', 'hdr', 'posters3d', 'mini3d', 'disney', 'pixar', 'hide4k', 'transcode', 'tvlibrary', 'tv4kposters', 'films4kposters', 'tmdb_restore', 'recreate_hdr', 'new_hdr', 'default_poster', 'autocollections', 'tautulli_server', 'mcu_collection', 'tr_r_p_collection', 'audio_posters', 'loglevel', 'manualplexpathfield', 'skip_media_info'])

        for item in Plex.query.all():
            out.writerow([item.plexurl, item.filmslibrary, item.library3d, item.plexpath, item.manualplexpath, item.mountedpath, item.backup, item.posters4k, item.mini4k, item.hdr, item.posters3d, item.mini3d, item.disney, item.pixar, item.hide4k, item.transcode, item.tvlibrary, item.tv4kposters, item.films4kposters, item.tmdb_restore, item.recreate_hdr, item.new_hdr, item.default_poster, item.autocollections, item.tautulli_server, item.mcu_collection, item.tr_r_p_collection, item.audio_posters, item.loglevel, item.manualplexpathfield, item.skip_media_info])
        f.close
        shutil.copy('./version', '/logs/version')

    def additional_info():
        import platform
        uname = platform.uname()
        f = open('/logs/system_info.txt', "a")
        mpath = [f for f in os.listdir('/films') if not f.startswith('.')]
        f.write("System Information"+"\n"+"System: "+uname.system+"\n"+"Node Name: "+uname.node+"\n"+"Release: "+uname.release+"\n"+"Version: "+uname.version+"\n"+"Machine: "+uname.machine+"\n"+"/films content: ") 
        f.write(str(mpath))
        f.close() 

    from zipfile import ZipFile
    def get_all_file_paths(directory):
        file_paths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
        return file_paths  


    def zip():
        additional_info()
        export_config()
        directory = '/logs'    
        file_paths = get_all_file_paths(directory)

    
        print('Following files will be zipped:')
        for file_name in file_paths:
            print(file_name)

        with ZipFile('app/support.zip','w') as zip:
            for file in file_paths:
                zip.write(file)
    zip()

    os.remove('/logs/support.csv')
    path = 'support.zip'
    return send_file(path, as_attachment=True)

@app.route("/update_schedules", methods=['GET'])
def update_schedules():
    return update_scheduler()

@app.route('/help')
def help():
    import os
    from plexapi.server import PlexServer
    import re
    import requests
    import shutil 
    from pathlib import PureWindowsPath, PurePosixPath
    file_paths = './app/static/img/tmp/'
    config = Plex.query.filter(Plex.id == '1')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    lib = config[0].filmslibrary.split(',')
    for root, dirs, files in os.walk(file_paths):
        for f in files:
            if f.endswith('.png'):# and 'poster_not_found' not in f):
                print(f)
                os.remove(file_paths+f)   
    try:
        os.remove("app/support.zip")
        os.remove('./app/static/img/poster.png')
        os.remove('./app/static/img/poster_bak.png')
    except FileNotFoundError as e:
        pass
        
    mpath = [f for f in os.listdir('/films') if not f.startswith('.')]
    try:
        films = get_library(lib, plexserver)   
    except requests.exceptions.ConnectionError as e:
        log.error(e)
        message = "Can not connect to your plex server, please check your config"
        return render_template('error.html', pagetitle="Error - Connection Error", pageheading="Connection Error", error=e, message=message, version=version), 500

    advanced_filter = {
        'or': [
            {'resolution': '4k'},
            {'hdr': True}
        ]
    }
    for i in films.search(sort='random', limit='1', filters=advanced_filter):
        p = get_poster(i, film_table)
        backup_poster = p[0]
        current_poster = '/static/img/tmp/'+p[1]
        log.debug('Running help script')
        plex_filepath = i.media[0].parts[0].file
        filmtitle = i.title
        try:
            p = PureWindowsPath(i.media[0].parts[0].file)
            p1 = re.findall('[A-Z]', p.parts[0])
            if p1 != []:
                log.debug(p1)
                newdir = PurePosixPath('/films', *p.parts[1:])
                log.debug(newdir)
            elif config[0].manualplexpath == 1:
                newdir = re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file)
            else:
                newdir = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
        except:
            newdir = 'Can not be converted'
        log.debug(newdir)
        if os.path.exists(newdir) == True:
            exists = 'True'
            log.debug("PATH EXISTS")
        else:
            exists = 'False'
            log.debug("PATH DOES NOT EXIST")
    return render_template('help.html', exists=exists, pagetitle='Help', plex=config, plex_filepath=plex_filepath, filmtitle=filmtitle, newdir=newdir, mpath=mpath, backup_poster=backup_poster, current_poster=current_poster, pageheadding='Help', version=version)


@app.route('/webhook',methods=['POST'])
def recently_added():
    if request.method == 'POST':
        data = request.json
        log.debug(data)
        try:
            if 'tautulli' in str.lower(data['server']):
                title = data['title']
                mediatype = data['type']
                guid = data['id']
                action = data['action']
                log.debug(title+" "+mediatype+" "+guid+" "+action)
                if (mediatype == 'episode' and action != 'watched'):
                    log.debug('running episode webhook')
                    threading.Thread(target=scripts.tv_episode_poster, args=[app, guid, ''],    name='TV_webhook').start()
                    return 'ok', 200
                #elif (mediatype == 'episode' and action == 'watched'):
                #    from time import sleep
                #    sleep(600)
                #    threading.Thread(target=scripts.spoilers(guid), name='Spoiler_webhook').start   ()                    
                #    return 'ok', 200
                else:
                    #threading.Thread(target=scripts.hide4k,  args=[app], name='hide4K_Webhook').start()
                    threading.Thread(target=scripts.posters4k, args=[app, title], name='4k_posters_webhook').start()
                    return 'ok', 200
        except:
            if 'series' in data:
                tv_show = data['series']['title']
                mediatype = 'episode'
                season = data['episodes'][0]['seasonNumber']
                episode = data['episodes'][0]['episodeNumber']
                guid = scripts.get_tv_guid(tv_show, season, episode)
                log.debug(guid)
                threading.Thread(target=scripts.tv_episode_poster, args=[app, guid, ''], name='TV_webhook').    start()
                return 'ok', 200
            elif 'movie' in data:
                movie = data['movie']['title']
                threading.Thread(target=scripts.posters4k, args=[app, movie], name='4k_posters_webhook').   start()
                return 'ok', 200
            else:
                log.error("Webhook not running")
                return 'Error', 500


@app.route('/api/data')
def data():
    query = film_table.query
 
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            film_table.title.like(f'%{search}%'),
            film_table.res.like(f'%{search}%'),
            film_table.hdr.like(f'%{search}%'),
            film_table.audio.like(f'%{search}%'),
        ))
 
    total_filtered = query.count()
 
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['title', 'res', 'hdr', 'audio']:
            col_name = 'title'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(film_table, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)
 
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)
 
 
    return {
        'data': [films.to_dict() for films in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': film_table.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/api/episodes')
def ep_data():
    query = ep_table.query
 
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            ep_table.show_season.like(f'%{search}%'),
            ep_table.title.like(f'%{search}%'),
            ep_table.res.like(f'%{search}%'),
            ep_table.hdr.like(f'%{search}%'),
            ep_table.audio.like(f'%{search}%')
        ))
 
    total_filtered = query.count()
 
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['title', 'res', 'hdr', 'audio', 'show_season']:
            col_name = 'title'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(ep_table, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)
 
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)
 
 
    return {
        'data': [title.to_dict() for title in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': ep_table.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/api/seasons')
def season_data():
    query = season_table.query
 
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            season_table.title.like(f'%{search}%'),
        ))
 
    total_filtered = query.count()
 
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['title']:
            col_name = 'title'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(season_table, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)
 
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)
 
 
    return {
        'data': [title.to_dict() for title in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': season_table.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/api/upload/<path:var>')
def upload_tmdb_posters(var=''):
    config = Plex.query.filter(Plex.id == '1')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    guid = var.split('&')
    guid = guid[1]
    poster=''
    print(var)
    #print(guid)
    if 'movie' in guid:
        scripts.upload_tmdb_film(app, var)
        lib = config[0].filmslibrary.split(',')
        n = len(lib)
        if n >=2:
            for l in range(n):
                library = get_library(l, plexserver)
        else:
            library = get_library(lib, plexserver)
        for i in library.search(guid=guid):
            print(i)
            poster = get_poster(i, film_table)
            poster = '/static/img/tmp/'+poster[1]
    if 'season' in guid:
        scripts.upload_tmdb_season(app, var)
        lib = config[0].tvlibrary.split(',')
        n = len(lib)
        if n >=2:
            for l in range(n):
                library = get_library(l, plexserver)
        else:
            library = get_library(lib, plexserver)
        for i in library.search(guid=guid, libtype='season'):
            print(i)
            poster = get_poster(i, season_table)
            poster = '/static/img/tmp/'+poster[1]
    if 'episode' in guid:
        scripts.upload_tmdb_episode(app, var)
        lib = config[0].tvlibrary.split(',')
        n = len(lib)
        if n >=2:
            for l in range(n):
                library = get_library(l, plexserver)
        else:
            library = get_library(lib, plexserver)
        for i in library.search(guid=guid, libtype='episode'):
            poster = get_poster(i, ep_table)
            poster = '/static/img/tmp/'+poster[1]        
    return render_template('result.html', pagetitle='Upload', version=version, poster=poster)

@app.route('/api/process/<path:var>')
def api_process(var=''):
    config = Plex.query.filter(Plex.id == '1')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    print(var)
    if 'movie' in var:
        scripts.guid_to_title(app, var)
        lib = config[0].filmslibrary.split(',')
        n = len(lib)
        if n >=2:
            for l in range(n):
                library = get_library(l, plexserver)
        else:
            library = get_library(lib, plexserver)
        for i in library.search(guid=var):
            print(i)
            poster = get_poster(i, film_table)
            poster = '/static/img/tmp/'+poster[1]
    if 'season' in var:
        scripts.upload_tmdb_season(app, var)
    if 'episode' in var:
        scripts.upload_tmdb_episode(app, var)
    return render_template('result.html', pagetitle='Upload', version=version, poster=poster)