import logging
from flask import render_template, flash, request, redirect, send_file
from app import db
from app import app
from app.forms import AddRecord_config, AddRecord_config_options, admin_config
from app.models import Plex, film_table, ep_table, season_table
import threading
import datetime
from app import update_scheduler
import os
from app import scripts
date = datetime.datetime.now()
date = date.strftime("%y.%m.%d-%H%M")



scripts.setup_logger('SYS', r"/logs/application_log.log")
log = logging.getLogger('SYS')

def get_version():
    with open('./version') as f: s = f.read()
    return s
version = get_version()

@app.route('/')
@app.route('/index', methods=["GET"])
def index():
    plex = Plex.query.filter(Plex.id == '1').all()
    return render_template('index.html', plex=plex, pagetitle='Home', version=version)

@app.route('/view_script_logs')
def script_logs():
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route("/script_log_stream", methods=["GET"])
def script_stream():
    def script_generate():
        with open('/logs/script_log.log', "rb") as f:
            while chunk := f.read(1024 * 10):
                yield chunk
    return app.response_class(script_generate(), mimetype='text/plain')

@app.route('/run_scripts', methods=["GET"])
def run_scripts():
    return render_template('scripts.html', pagetitle='Scripts', version=version)


@app.route('/remove_backups', methods=['GET'])
def run_remove_backups():
    threading.Thread(target=scripts.remove_unused_backup_files).start()   
    return script_logs()

@app.route('/test')
def run_test():
    threading.Thread(target=scripts.test_script).start()
    return script_logs()


@app.route('/posters4k', methods=['GET'])
def run_posters4k():
    threading.Thread(target=scripts.posters4k_thread, name='4K Poster Script').start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/rerun-posters4k/<path:var>', methods=['GET'])
def rerun_posters4k(var):
    log.debug(var)
    threading.Thread(target=scripts.guid_to_title(var), name='4K Poster Script').start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/rerun-tv-posters/<path:var>', methods=['GET'])
def rerun_tv_posters(var):
    log.debug(var)
    threading.Thread(target=scripts.guid_to_title(var), name='TV Poster Script').start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/tvposters4k', methods=['GET'])
def run_tvposters4k():
    threading.Thread(target=scripts.tvposters4k_thread()).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)    
@app.route('/posters3d', methods=['GET'])
def run_posters3d():   
    threading.Thread(target=scripts.posters3d()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/hide4k', methods=['GET'])
def run_hide4k():   
    threading.Thread(target=scripts.hide4k()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/disney', methods=['GET'])
def run_disney():   
    threading.Thread(target=scripts.autocollections.disney).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/pixar', methods=['GET'])
def run_pixar():
    threading.Thread(target=scripts.autocollections.pixar).start()
    return(render_template('script_log_viewer.html', pagetitle='Script Logs', version=version))

@app.route('/preseed')
def preseed():
    threading.Thread(target=scripts.fill_database()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/add_labels')
def start_add_labels():
    threading.Thread(target=scripts.add_labels()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
@app.route('/spoilers', methods=['GET'])
def run_tvspoilers():
    threading.Thread(target=scripts.spoilers_scheduled()).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)  


@app.route('/restore', methods=['GET'])
def run_restore():   
    threading.Thread(target=scripts.restore_posters()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/restore_from_database', methods=['GET'])
def run_restore_from_database():   
    threading.Thread(target=scripts.restore_from_database()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
      
@app.route('/restore_tv', methods=['GET'])
def run_episode_restore():   
    threading.Thread(target=scripts.restore_episodes_from_database()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)


@app.route('/recreate_hdr')
def run_recreate_hdr():   
    return render_template("/recreate_hdr.html", pagetitle='Recreate HDR Posters', version=version)

@app.route('/recreate_hdr_script')
def run_recreate_hdr_script():   
    threading.Thread(target=scripts.fresh_hdr_posters()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/autocollections')
def run_autocollections():   
    threading.Thread(target=scripts.autocollections()).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)




@app.route('/view_application_logs')
def application_logs():
    return render_template('application_log_viewer.html', pagetitle='Application Logs', version=version)
@app.route("/application_log_stream", methods=["GET"])
def stream():
    def generate():
        with open('/logs/application_log.log', "rb") as f:
            while chunk := f.read(1024):
                yield chunk
    return app.response_class(generate(), mimetype='text/plain') 

@app.route('/view_system_logs')
def system_logs():
    return render_template('syslog.html', pagetitle='System Logs', version=version)
@app.route("/system_log_stream", methods=["GET"])
def syslog_stream():
    def generate():
        with open('/logs/SYSTEM.log', "rb") as f:
            while chunk := f.read(1024):
                yield chunk
    return app.response_class(generate(), mimetype='text/plain')


@app.route("/update_schedules", methods=['GET'])
def update_schedules():
    return update_scheduler()

@app.route('/config', methods=['POST', 'GET'])
def config():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config()
        form.backup.default = plex.backup
        form.restore_from_tmdb.default = plex.tmdb_restore
        form.process()
        return render_template('config.html', plex=plex, form=form, pagetitle='Config', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config()
        plex.plexurl = request.form['plexurl']
        plex.token = request.form['token']
        plex.filmslibrary = request.form['filmslibrary']
        plex.tvlibrary = request.form['tvlibrary']
        plex.library3d = request.form['library3d']
        plex.t1 = request.form['t1']
        plex.t5 = request.form['t5']
        plex.t2 = request.form['t2']
        plex.t3 = request.form['t3']
        plex.t4 = request.form['t4']
        plex.backup = request.form['backup']
        plex.tmdb_restore = request.form['restore_from_tmdb']
        plex.tmdb_api = request.form['tmdb_api']
        plex.tautulli_server = request.form['tautulli_server']
        plex.tautulli_api = request.form['tautulli_api']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            update_scheduler()
            return render_template('result.html', message=message, pagetitle='Config Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config.html', plex=plex, form=form, pagetitle='Error', version=version)

@app.route('/config_options', methods=['POST', 'GET'])
def config_options():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config_options()
        form.skip_media_info.default = plex.skip_media_info
        form.posters4k.default = plex.posters4k
        form.mini4k.default = plex.mini4k
        form.hdr.default = plex.hdr
        form.recreate_hdr.default = plex.recreate_hdr
        form.posters3d.default = plex.posters3d
        form.tv4kposters.default = plex.tv4kposters
        form.films4kposters.default = plex.films4kposters
        form.mini3d.default = plex.mini3d
        form.hide4k.default = plex.hide4k
        form.transcode.default = plex.transcode
        form.pixar.default = plex.pixar
        form.disney.default = plex.disney
        form.default_poster.default = plex.default_poster
        form.mcu_collection.default = plex.mcu_collection
        form.autocollections.default = plex.autocollections
        form.tr_r_p_collection.default = plex.tr_r_p_collection
        form.audio_posters.default = plex.audio_posters
        form.spoilers.default = plex.spoilers
        form.process()
        return render_template('config_options.html', plex=plex, form=form, pagetitle='Config Options', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config_options()
        plex.posters4k = request.form['posters4k']
        plex.films4kposters = request.form['films4kposters']
        plex.tv4kposters = request.form['tv4kposters']
        plex.mini4k = request.form['mini4k']
        plex.hdr  = request.form['hdr']
        plex.recreate_hdr = request.form['recreate_hdr']
        plex.posters3d = request.form['posters3d']
        plex.mini3d = request.form['mini3d']
        plex.hide4k = request.form['hide4k']
        plex.transcode = request.form['transcode']
        plex.disney = request.form['disney']
        plex.pixar = request.form['pixar']
        plex.mcu_collection = request.form['mcu_collection']
        plex.default_poster = request.form['default_poster']
        plex.autocollections = request.form['autocollections']
        plex.tr_r_p_collection = request.form['tr_r_p_collection']
        plex.audio_posters = request.form['audio_posters']
        plex.skip_media_info = request.form['skip_media_info']
        plex.spoilers = request.form['spoilers']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            update_scheduler()
            return render_template('result.html', message=message, pagetitle='Config Options Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config_options.html', plex=plex, form=form, pagetitle='Error', version=version)


@app.route('/admin_config', methods=['POST', 'GET'])
def admin_config_form():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = admin_config()
        form.skip_media_info.default = plex.skip_media_info
        form.manualplexpath.default = plex.manualplexpath
        form.loglevel.default = plex.loglevel
        form.backup.default = plex.backup
        form.restore_from_tmdb.default = plex.tmdb_restore
        form.posters4k.default = plex.posters4k
        form.mini4k.default = plex.mini4k
        form.hdr.default = plex.hdr
        form.recreate_hdr.default = plex.recreate_hdr
        form.posters3d.default = plex.posters3d
        form.tv4kposters.default = plex.tv4kposters
        form.films4kposters.default = plex.films4kposters
        form.mini3d.default = plex.mini3d
        form.hide4k.default = plex.hide4k
        form.transcode.default = plex.transcode
        form.pixar.default = plex.pixar
        form.disney.default = plex.disney
        form.default_poster.default = plex.default_poster
        form.mcu_collection.default = plex.mcu_collection
        form.autocollections.default = plex.autocollections
        form.tr_r_p_collection.default = plex.tr_r_p_collection
        form.audio_posters.default = plex.audio_posters
        form.spoilers.default = plex.spoilers
        form.process()
        return render_template('admin_config.html', plex=plex, form=form, pagetitle='Config Options', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = admin_config()
        plex.loglevel = request.form['loglevel']
        plex.posters4k = request.form['posters4k']
        plex.films4kposters = request.form['films4kposters']
        plex.tv4kposters = request.form['tv4kposters']
        plex.mini4k = request.form['mini4k']
        plex.hdr  = request.form['hdr']
        plex.recreate_hdr = request.form['recreate_hdr']
        plex.posters3d = request.form['posters3d']
        plex.mini3d = request.form['mini3d']
        plex.hide4k = request.form['hide4k']
        plex.transcode = request.form['transcode']
        plex.disney = request.form['disney']
        plex.pixar = request.form['pixar']
        plex.mcu_collection = request.form['mcu_collection']
        plex.default_poster = request.form['default_poster']
        plex.autocollections = request.form['autocollections']
        plex.tr_r_p_collection = request.form['tr_r_p_collection']
        plex.audio_posters = request.form['audio_posters']
        plex.plexurl = request.form['plexurl']
        plex.token = request.form['token']
        plex.filmslibrary = request.form['filmslibrary']
        plex.tvlibrary = request.form['tvlibrary']
        plex.library3d = request.form['library3d']
        plex.t1 = request.form['t1']
        plex.t5 = request.form['t5']
        plex.t2 = request.form['t2']
        plex.t3 = request.form['t3']
        plex.t4 = request.form['t4']
        plex.backup = request.form['backup']
        plex.tmdb_restore = request.form['restore_from_tmdb']
        plex.tmdb_api = request.form['tmdb_api']
        plex.tautulli_server = request.form['tautulli_server']
        plex.tautulli_api = request.form['tautulli_api']
        plex.manualplexpath = request.form['manualplexpath']
        plex.manualplexpathfield = request.form['manualplexpathfield']
        plex.mountedpath = request.form['mountedpath']
        plex.skip_media_info = request.form['skip_media_info']
        plex.spoilers = request.form['spoilers']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            scripts.logger_start()
            update_scheduler()
            return render_template('result.html', message=message, pagetitle='Config Options Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config_options.html', plex=plex, form=form, pagetitle='Error', version=version)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e, version=version), 404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e, version=version), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e, version=version), 500


@app.route('/help')
def help():
    import os
    from plexapi.server import PlexServer
    import re
    import requests
    import shutil 
    from pathlib import PureWindowsPath, PurePosixPath
    file_paths = './app/static/img/tmp/'
    for root, dirs, files in os.walk(file_paths):
        #print(files)
        for f in files:
            #print(f)
            #f = filename
            
            if f.endswith('.png'):# and 'poster_not_found' not in f):
                print(f)
                os.remove(file_paths+f)   
    try:
        os.remove("app/support.zip")
     
        os.remove('./app/static/img/poster.png')
        os.remove('./app/static/img/poster_bak.png')
    except FileNotFoundError as e:
        pass

    config = Plex.query.filter(Plex.id == '1')
    plexserver = PlexServer(config[0].plexurl, config[0].token)
    mpath = [f for f in os.listdir('/films') if not f.startswith('.')]

    try:
        def get_library():
            lib = config[0].filmslibrary.split(',')
            log.debug(lib)
            if len(lib) <= 2:
                try:
                    while True:
                        for l in range(10):
                            films = plexserver.library.section(lib[l])
                            return films
                except IndexError:
                    pass     
        films = get_library()   
    except requests.exceptions.ConnectionError as e:
        log.error(e)
        message = "Can not connect to your plex server, please check your config"
        return render_template('error.html', pagetitle="Error - Connection Error", pageheading="Connection Error", error=e, message=message, version=version), 500

    
    def get_poster():
        guid = str(i.guid)
        imgdir = './app/static/img/tmp/'
        imgdir_exists = os.path.exists(imgdir)
        if imgdir_exists == False:
            os.mkdir('./app/static/img/tmp')

        log.debug(i.media[0].parts[0].file)
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        fname = re.sub('plex://movie/', '', guid)+'.png'
        filename = "poster.png"
        if img.status_code == 200:
            img.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img.raw, f) 
        shutil.copy(filename, './app/static/img/tmp/'+fname)
        
        r = film_table.query.filter(film_table.guid == guid).all()
        if r:
            backup_poster = r[0].poster
        else:
            backup_poster = '/static/img/404/poster_not_found.png'
        return backup_poster, fname

    advanced_filter = {
        'or': [
            {'resolution': '4k'},
            {'hdr': True}
        ]
    }

    for i in films.search(sort='random', limit='1', filters=advanced_filter):
        p = get_poster()
        backup_poster = p[0]
        current_poster = '/static/img/tmp/'+p[1]
        log.debug('Running help script')
        plex_filepath = i.media[0].parts[0].file
        filmtitle = i.title
        log.debug(config[0].manualplexpath)
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
                    threading.Thread(target=scripts.tv_episode_poster(guid, ''),    name='TV_webhook').start()
                    return 'ok', 200
                elif (mediatype == 'episode' and action == 'watched'):
                    from time import sleep
                    sleep(600)
                    threading.Thread(target=scripts.spoilers(guid), name='Spoiler_webhook').start   ()                    
                    return 'ok', 200
                else:
                    threading.Thread(target=scripts.hide4k, name='hide4K_Webhook').start()
                    threading.Thread(target=scripts.posters4k(title), name='4k_posters_webhook').   start()
                    return 'ok', 200
        except:
            if 'series' in data:
                tv_show = data['series']['title']
                mediatype = 'episode'
                season = data['episodes'][0]['seasonNumber']
                episode = data['episodes'][0]['episodeNumber']
                guid = scripts.get_tv_guid(tv_show, season, episode)
                log.debug(guid)
                threading.Thread(target=scripts.tv_episode_poster(guid, ''), name='TV_webhook').    start()
                return 'ok', 200
            elif 'movie' in data:
                movie = data['movie']['title']
                threading.Thread(target=scripts.posters4k(movie), name='4k_posters_webhook').   start()
                return 'ok', 200
            else:
                log.error("Webhook not running")
                return 'Error', 500


@app.route('/films')
def get_films():
    return render_template('films.html', pagetitle='Films', version=version)#, films=films)

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


@app.route('/episodes')
def get_episodes():
    return render_template('episodes.html', pagetitle='Episodes', version=version)


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

@app.route('/seasons')
def get_seasons():
    return render_template('seasons.html', pagetitle='Seasons', version=version)


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


@app.route('/delete_row/<path:var>')
def run_delete_row(var=''):
    scripts.delete_row(var)
    message = 'Deleted row'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)

@app.route('/restore/film/<path:var>')
def restore_poster(var=""):
    #print(var)
    scripts.restore_single(var)
    message = 'Sent poster to be restored.'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)
@app.route('/restore/episode/<path:var>')
def restore_episode_poster(var=""):
    #print(var)
    scripts.restore_episode_from_database(var)
    message = 'Sent poster to be restored.'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)
@app.route('/restore/season/<path:var>')
def restore_season_poster(var=""):
    #print(var)
    scripts.restore_single_season(var)
    message = 'Sent poster to be restored.'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)
@app.route('/restore_seasons')
def restore_seasons():
    #print(var)
    scripts.restore_seasons()
    message = 'Sent posters to be restored.'
    return render_template('result.html', message=message, pagetitle='Restored', version=version)    
@app.route('/restore/bannered_season/<path:var>')
def restore_bannerred_season_poster(var=""):
    #print(var)
    msg = scripts.restore_single_bannered_season(var)
    if 'error' not in str.lower(msg):
        return render_template('result.html', message=msg, pagetitle='Restored', version=version)
    else:
        return render_template('result.html', message=msg, pagetitle='Error', version=version)

@app.route('/restore/bannered_film/<path:var>')
def restore_bannerred_poster(var=""):
    #print(var)
    msg = scripts.restore_single_bannered(var)
    print(msg)
    if 'error' not in str.lower(msg):
        return render_template('result.html', message=msg, pagetitle='Restored', version=version)
    else:
        return render_template('result.html', message=msg, pagetitle='Error', version=version)

@app.route('/restart_server')
def restart_server():
    cmd = "supervisorctl restart gunicorn"
    os.system(cmd)
    return redirect('/index')
    
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
                        "bannered_season" TEXT,
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

@app.route('/sync_ratings')
def sync_ratings():
    threading.Thread(target=scripts.sync_ratings).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)

@app.route('/maintenance')
def run_maintenance():
    threading.Thread(target=scripts.maintenance).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs', version=version)
