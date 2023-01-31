import logging
from flask import render_template, flash, request, redirect, send_file, url_for
from flask_paginate import Pagination, get_page_args
from app import db
from app import app
import os
import sqlite3
from app.forms import AddRecord_config, AddRecord_config_options, admin_config
from app.models import Plex, film_table, ep_table, season_table
import threading
from threading import Thread
import datetime
from app import scripts
date = datetime.datetime.now()
date = date.strftime("%y.%m.%d-%H%M")
poster_url_base = 'https://www.themoviedb.org/t/p/original'


scripts.setup_logger('SYS', r"/logs/application_log.log")
log = logging.getLogger('SYS')

def get_version():
    with open('./version') as f: s = f.read()
    return s
version = get_version()
@app.before_first_request
def update_plex_path():

    import requests
    import re
    from plexapi.server import PlexServer
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        config = c.fetchall()
        plex = PlexServer(config[0][1], config[0][2])
        lib = config[0][3].split(',')
        if len(lib) <= 2:
            try:
                films = plex.library.section(lib[0])
            except IndexError:
                pass
        else:
            films = plex.library.section(config[0][3])
        media_location = films.search(limit='1')
        if config[0][37] == 1:
            plexpath = config[0][38]
            c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
            conn.commit()
            c.close()
        elif config[0][37] == 0:
            filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
            try:
                plexpath = '/'+filepath.split('/')[2]
                plexpath = '/'+filepath.split('/')[1]
            except IndexError as e:
                plexpath = '/'
            c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
            conn.commit()
            c.close()
    except Exception:
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM plex_utills")
            config = c.fetchall()
            plex = PlexServer(config[0][1], config[0][2])
            lib = config[0][3].split(',')
            if len(lib) <= 2:
                try:
                    films = plex.library.section(lib[0])
                except IndexError:
                    pass
            else:
                films = plex.library.section(config[0][3])     
            media_location = films.search(limit='1')
            for i in media_location:
                if config[0][37] == 1:
                    newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                elif config[0][37] == 0:
                    if config[0][5] == '/':
                        newdir = '/films'+i.media[0].parts[0].file
                    else:
                        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        except:pass

@app.route('/')
@app.route('/index', methods=["GET"])
def index():
    plex = Plex.query.filter(Plex.id == '1').all()
    if plex[0].migrated == 0:
        return render_template('migrate.html', pagetitle='Home', version=version)
        #Thread(target=scripts.fill_database).start()
    else:
        return render_template('index.html', plex=plex, pagetitle='Home', version=version)

######### SITE ##############

@app.route('/run_scripts', methods=["GET"])
def run_scripts():
    return render_template('scripts.html', pagetitle='Scripts', version=version)

@app.route('/films')
def get_db_films():
    return render_template('films.html', pagetitle='Films', version=version)

@app.route('/episodes')
def get_db_episodes():
    return render_template('episodes_db.html', pagetitle='Episodes', version=version)

@app.route('/seasons')
def get_db_seasons():
    return render_template('seasons_db.html', pagetitle='Seasons', version=version)


####### Error PAGES ########
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e, version=version), 404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e, version=version), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e, version=version), 500


####### LOG PAGES ##########

@app.route('/view_script_logs')
def script_logs():
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route("/script_log_stream", methods=["GET"])
def script_stream():
    def script_generate():
        with open('/logs/script_log.log', "rb") as f:
            for line in reversed(list(f)):
                yield line
    return app.response_class(script_generate(), mimetype='text/plain')

@app.route('/view_application_logs')
def application_logs():
    return render_template('application_log_viewer.html', pagetitle='Application Logs', version=version)
@app.route("/application_log_stream", methods=["GET"])
def stream():
    def generate():
        with open('/logs/application_log.log', "rb") as f:
            for line in reversed(list(f)):
                yield line
    return app.response_class(generate(), mimetype='text/plain') 

#@app.route('/view_system_logs')
#def system_logs():
#    return render_template('syslog.html', pagetitle='System Logs', version=version)
#@app.route("/system_log_stream", methods=["GET"])
#def syslog_stream():
#    def generate():
#        with open('/logs/SYSTEM.log', "rb") as f:
#            for line in reversed(list(f)):
#                yield line
#        return app.response_class(generate(), mimetype='text/plain')

########## SCRIPTS ###################


#### FILMS ####
@app.route('/posters4k', methods=['GET'])
def run_posters4k():
    webhooktitle = ''
    t = Thread(target=scripts.posters4k, name='4K Poster Script', args=[app, webhooktitle, ''])
    t.start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/rerun-posters4k/<path:var>', methods=['GET'])
def rerun_posters4k(var):
    log.debug(var)
    Thread(target=scripts.guid_to_title, name='4K Poster Script', args=[app, var]).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/hide4k', methods=['GET'])
def run_hide4k():   
    Thread(target=scripts.hide4k, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/sync_ratings')
def sync_ratings():
    Thread(target=scripts.sync_ratings).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/posters3d', methods=['GET'])
def run_posters3d():   
    Thread(target=scripts.posters3d, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


#### SHOWS ####
@app.route('/rerun-tv-posters/<path:var>', methods=['GET'])
def rerun_tv_posters(var):
    log.debug(var)
    Thread(target=scripts.guid_to_title, name='TV Poster Script', args=[app, var]).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/tvposters4k', methods=['GET'])
def run_tvposters4k():
    epwebhook = ''
    poster = ''
    Thread(target=scripts.tv_episode_poster, args=[app, epwebhook, poster]).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)    

@app.route('/restore_seasons')
def restore_seasons():
    Thread(target=scripts.restore_seasons).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)  


@app.route('/remove_backups', methods=['GET'])
def run_remove_backups():
    Thread(target=scripts.remove_unused_backup_files).start()   
    return script_logs()

@app.route('/test')
def run_test():
    Thread(target=scripts.test_script).start()
    return script_logs()


#### COLLECTIONS #####
@app.route('/autocollections')
def run_autocollections():   
    Thread(target=scripts.autocollections, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/disney', methods=['GET'])
def run_disney():   
    Thread(target=scripts.autocollections.disney, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/pixar', methods=['GET'])
def run_pixar():
    Thread(target=scripts.autocollections.pixar, args=[app]).start()
    return(render_template('script_log_viewer.html', pagetitle='Script Logs', version=version))



@app.route('/preseed')
def preseed():
    Thread(target=scripts.fill_database, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/add_labels')
def start_add_labels():
    Thread(target=scripts.add_labels, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/spoilers', methods=['GET'])
def run_tvspoilers():
    Thread(target=scripts.spoilers_scheduled, args=[app]).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)  


@app.route('/restore', methods=['GET'])
def run_restore():   
    Thread(target=scripts.restore_posters, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/restore_from_database', methods=['GET'])
def run_restore_from_database():   
    Thread(target=scripts.restore_from_database, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
      
@app.route('/restore_tv', methods=['GET'])
def run_episode_restore():   
    Thread(target=scripts.restore_episodes_from_database, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/recreate_hdr')
def run_recreate_hdr():   
    return render_template("/recreate_hdr.html", pagetitle='Recreate HDR Posters', version=version)

@app.route('/recreate_hdr_script')
def run_recreate_hdr_script():   
    Thread(target=scripts.fresh_hdr_posters, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/maintenance')
def run_maintenance():
    Thread(target=scripts.maintenance).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/check_backup_posters')
def run_backup_poster_check():
    Thread(target=scripts.backup_poster_check, args=[app]).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

#@app.route('/search', methods=['GET', 'POST'])
#def search():
#    if request.method == 'POST':
#        F_results = E_results = S_results = ''
#        try:
#            F_results = db.session.execute(db.select(film_table).where(film_table.title.contains(request.form['search']))).scalars()
#        except: pass
#        try:
#            E_results = db.session.execute(db.select(ep_table).where(ep_table.title.contains(request.form['search']))).scalars()
#        except: pass
#        try:
#            S_results = db.session.execute(db.select(season_table).where(season_table.title.contains(request.form['search']))).scalars()
#        except: pass
#        return render_template('search_results.html', pagetitle='search', F_results=F_results, E_results=E_results, S_results=S_results, version=version)
#    return render_template('search.html', pagetitle='search', version=version)

@app.route('/info/<path:var>')
def info(var=''):
    guid = ''
    if 'movie' in var:
        i = db.session.execute(db.select(film_table).filter_by(guid=var)).scalar()
        if i:
            item = i
        else: 
            item = ''
            guid = var
        posters = scripts.get_tmdb_film_posters(var)
        return render_template('/info.html', pagetitle='Info', guid=guid, item=item, poster_url=poster_url_base, posters=posters, version=version)
    elif 'show' in var:
        item = ''
        posters = ''
        return render_template('/info.html', pagetitle='Info', guid=guid, item=item, poster_url=poster_url_base, posters=posters, version=version)
    elif 'season' in var:
        i = db.session.execute(db.select(season_table).filter_by(guid=var)).scalar()
        if i:
            item = i
        else: 
            item = ''
            guid = var
        item = db.session.execute(db.select(season_table).filter_by(guid=var)).scalar()
        posters = scripts.get_tmdb_season_posters(var)
        return render_template('/info.html', pagetitle='Info', guid=guid, item=item, poster_url=poster_url_base, posters=posters, version=version)
    elif 'episode' in var:
        i = db.session.execute(db.select(ep_table).filter_by(guid=var)).scalar()
        if i:
            item = i
        else: 
            item = ''
            guid = var
        item = db.session.execute(db.select(ep_table).filter_by(guid=var)).scalar()
        posters = scripts.get_tmdb_episode_posters(var)
        return render_template('/info.html', pagetitle='Info', guid=guid, item=item, poster_url=poster_url_base, posters=posters, version=version)


@app.route('/film_library')
def get_films():
    from app import scripts
    films = scripts.get_film_posters()
    print(films)
    def get_films(offset=0, per_page=8):
        return films[offset: offset + per_page]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(films)
    pagination_films = get_films(offset=offset, per_page=48)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('/library.html', pagetitle='Films', version=version, films=pagination_films, page=page, per_page=per_page, pagination=pagination)

@app.route('/shows')
def get_shows():
    from app import scripts
    shows = scripts.get_shows()
    def get_show(offset=0, per_page=8):
        return shows[offset: offset + per_page]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(shows)
    pagination_films = get_show(offset=offset, per_page=48)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    return render_template('/library.html', pagetitle='Shows', version=version, show=pagination_films, page=page, per_page=per_page, pagination=pagination)

@app.route('/seasons/<path:var>')
def get_seasons(var=''):
    from app import scripts
    seasons = scripts.get_tv_seasons(var)
    def get_season(offset=0, per_page=8):
        return seasons[offset: offset + per_page]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(seasons)
    pagination_films = get_season(offset=offset, per_page=48)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    
    return render_template('/show.html', pagetitle='Shows', version=version, show=pagination_films, page=page, per_page=per_page, pagination=pagination)

@app.route('/episode/<path:var>')
def get_episodes(var=''):
    from app import scripts
    episodes = scripts.get_tv_episodes(var)
    def get_episodes(offset=0, per_page=8):
        return episodes[offset: offset + per_page]
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(episodes)
    pagination_films = get_episodes(offset=offset, per_page=48)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')
    posters = scripts.get_tmdb_episode_posters(var)
    return render_template('/season.html', pagetitle='Shows', version=version, show=pagination_films, page=page, per_page=per_page, pagination=pagination, posters=posters)


@app.route('/search', methods=['GET', 'POST'])
def search():
    from plexapi.server import PlexServer
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)   
    from app.items import Film, Episode, Season
    if request.method == 'POST':
        F_results = E_results = S_results = ''
        lib = config[0].filmslibrary.split(',')
        n = len(lib)
        tvlib = config[0].tvlibrary.split(',')
        tvn = len(tvlib)
 
        F_results =[]
        E_results = []
        S_results = []            
        for l in range(n):
            F= plex.library.section(lib[l]).search(title=request.form['search'])
            for F in F:
                fdb = db.session.execute(db.select(film_table).where(film_table.title.contains(F.title))).scalars()
                poster =''
                for row in fdb:
                    poster = row.poster
                F_results.append(Film(F.title, F.guid, F.thumbUrl, poster))
        for l in range(tvn):
            ep = plex.library.section(tvlib[l]).search(title=request.form['search'], libtype='episode')
            for ep in ep:
                epdb = db.session.execute(db.select(ep_table).where(ep_table.title.contains(ep.title))).scalars()
                print(ep.title)
                ep_poster = ''
                for row in epdb:
                    ep_poster = row.poster
                E_results.append(Episode(ep.title, ep.parentTitle, ep.grandparentTitle, ep.guid, ep.thumbUrl, ep_poster))
            
            season = plex.library.section(tvlib[l]).search(title=request.form['search'], libtype='season')
            for s in season:
                sdb = db.session.execute(db.select(season_table).where(season_table.title.contains(ep.title))).scalars()
                s_poster =''
                for row in sdb:
                    s_poster = row.poster
                S_results.append(Season(s.title, s.parentTitle, s.guid, s.thumbUrl, s_poster))


        return render_template('results.html', pagetitle='search', F_results=F_results, S_results=S_results, E_results=E_results, version=version)
    return render_template('search.html', pagetitle='search', version=version)