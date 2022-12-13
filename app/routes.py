import logging
from flask import render_template, flash, request, redirect, send_file
from app import db
from app import app
from app.forms import AddRecord_config, AddRecord_config_options, admin_config
from app.models import Plex, film_table, ep_table, season_table
import threading
from threading import Thread
import datetime
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

######### SITE ##############

@app.route('/run_scripts', methods=["GET"])
def run_scripts():
    return render_template('scripts.html', pagetitle='Scripts', version=version)

@app.route('/films')
def get_films():
    return render_template('films.html', pagetitle='Films', version=version)

@app.route('/episodes')
def get_episodes():
    return render_template('episodes.html', pagetitle='Episodes', version=version)

@app.route('/seasons')
def get_seasons():
    return render_template('seasons.html', pagetitle='Seasons', version=version)


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
            while chunk := f.read(1024 * 10):
                yield chunk
    return app.response_class(script_generate(), mimetype='text/plain')

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

########## SCRIPTS ###################


#### FILMS ####
@app.route('/posters4k', methods=['GET'])
def run_posters4k():
    webhooktitle = ''
    t = Thread(target=scripts.posters4k, name='4K Poster Script', args=[app, webhooktitle])
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

