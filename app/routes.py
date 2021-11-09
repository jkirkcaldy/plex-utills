import logging
from flask import render_template, flash, request
from flask.wrappers import Response
from werkzeug.wrappers import response

from app import db
from app import app
from app.forms import AddRecord
from app.models import Plex
from time import sleep
from app import update_scheduler, posters4k, posters3d, hide4k, disney, pixar, migrate, restore_posters, fresh_hdr_posters, setup_logger
import threading



setup_logger('SYS', r"/logs/application_log.log")
log = logging.getLogger('SYS')



@app.route('/')
@app.route('/index', methods=["GET"])
def index():
    plex = Plex.query.filter(Plex.id == '1').all()
    return render_template('index.html', plex=plex, pagetitle='Home')

@app.route('/run_scripts', methods=["GET"])
def run_scripts():
    return render_template('scripts.html', pagetitle='Scripts')





@app.route('/posters4k', methods=['GET'])
def run_posters4k():
    threading.Thread(target=posters4k).start()   
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
@app.route('/posters3d', methods=['GET'])
def run_posters3d():   
    threading.Thread(target=posters3d).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
@app.route('/hide4k', methods=['GET'])
def run_hide4k():   
    threading.Thread(target=hide4k).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
@app.route('/disney', methods=['GET'])
def run_disney():   
    threading.Thread(target=disney).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
@app.route('/pixar', methods=['GET'])
def run_pixar():
    threading.Thread(target=pixar).start()
    return(render_template('script_log_viewer.html', pagetitle='Script Logs'))
@app.route('/restore', methods=['GET'])
def run_restore():   
    threading.Thread(target=restore_posters).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
    
@app.route('/recreate_hdr')
def run_recreate_hdr():   
    return render_template("/recreate_hdr.html", pagetitle='Recreate HDR Posters')

@app.route('/recreate_hdr_script')
def run_recreate_hdr_script():   
    threading.Thread(target=fresh_hdr_posters).start()
    return render_template('script_log_viewer.html', pagetitle='Script Logs')

@app.route('/migrate')
def run_migrate():
    return render_template('migrate.html', pagetitle='Config Migration')

@app.route('/start_migrate', methods=['GET', 'POST'])
def start_migrate():
    migrate()
    message = 'The database has been migrated, please go to the config page to double check your config has migrated correctly.'
    return render_template('result.html', message=message, pagetitle='Config migrated')

@app.route('/view_script_logs')
def script_logs():
    return render_template('script_log_viewer.html', pagetitle='Script Logs')
@app.route("/script_log_stream", methods=["GET"])
def script_stream():
    def script_generate():
        with open('/logs/script_log.log', "rb") as f:
            while chunk := f.read(1024 * 10):
                yield chunk
    return app.response_class(script_generate(), mimetype='text/plain') 



@app.route('/view_application_logs')
def application_logs():
    return render_template('application_log_viewer.html', pagetitle='Application Logs')
@app.route("/application_log_stream", methods=["GET"])
def stream():
    def generate():
        with open('/logs/application_log.log', "rb") as f:
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
        form = AddRecord()
        form.backup.default = plex.backup
        form.restore_from_tmdb.default = plex.tmdb_restore
        form.posters4k.default = plex.posters4k
        form.mini4k.default = plex.mini4k
        form.hdr.default = plex.hdr
        form.new_hdr.default = plex.new_hdr
        form.recreate_hdr.default = plex.recreate_hdr
        form.posters3d.default = plex.posters3d
        form.tv4kposters.default = plex.tv4kposters
        form.films4kposters.default = plex.films4kposters
        form.mini3d.default = plex.mini3d
        form.hide4k.default = plex.hide4k
        form.transcode.default = plex.transcode
        form.pixar.default = plex.pixar
        form.disney.default = plex.disney
        form.process()
        return render_template('config.html', plex=plex, form=form, pagetitle='Config')
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord()
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
        plex.posters4k = request.form['posters4k']
        plex.films4kposters = request.form['films4kposters']
        plex.tv4kposters = request.form['tv4kposters']
        plex.mini4k = request.form['mini4k']
        plex.hdr  = request.form['hdr']
        plex.new_hdr = request.form['new_hdr']
        plex.recreate_hdr = request.form['recreate_hdr']
        plex.posters3d = request.form['posters3d']
        plex.mini3d = request.form['mini3d']
        plex.hide4k = request.form['hide4k']
        plex.transcode = request.form['transcode']
        plex.disney = request.form['disney']
        plex.pixar = request.form['pixar']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            update_scheduler()
            return render_template('result.html', message=message, pagetitle='Config Updated')
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config.html', plex=plex, form=form, pagetitle='Error')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e), 404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e), 500


@app.route('/help')
def help():
    import sqlite3
    import os
    from plexapi.server import PlexServer
    import re
    import requests
    import shutil
    
    
    try:
        os.remove('app/static/img/poster.png')
        os.remove('app/static/img/poster_bak.png')
    except FileNotFoundError as e:
        log.debug(e)
    
    plex = Plex.query.filter(Plex.id == '1').all()
    
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    try:
        plexserver = PlexServer(config[0][1], config[0][2])
        films = plexserver.library.section(config[0][3])
    except requests.exceptions.ConnectionError as e:
        log.error(e)
        message = "Can not connect to your plex server, please check your config"
        return render_template('error.html', pagetitle="Error - Connection Error", pageheading="Connection Error", error=e, message=message)

    
    def get_poster():
        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        filename = "poster.png"
        if img.status_code == 200:
            img.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img.raw, f) 
        shutil.copy(filename, './app/static/img/poster.png')
        if backup == True:
            poster_bak = os.path.join(newdir+'poster_bak.png')
            shutil.copy(poster_bak, './app/static/img/poster_bak.png')
        
    for i in films.search(resolution='4k'):
        get_poster()
        plex_filepath = i.media[0].parts[0].file
        filmtitle = i.title
        newdir = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
        break
    return render_template('help.html', pagetitle='Help', plex=plex, plex_filepath=plex_filepath, filmtitle=filmtitle, newdir=newdir, pageheadding='Help')

    