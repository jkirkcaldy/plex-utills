from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from app.scripts import posters3d, hide4k, setup_logger, autocollections, collective4k
import os
from flask_apscheduler import APScheduler
import sqlite3
import logging
import shutil
from plexapi.server import PlexServer
import re
import plexapi
import tzlocal
import time
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter
import time
import platform

setup_logger('Application', r"/logs/application_#log.log")
log = logging.getLogger('Application')
b_dir = '/config/backup/' 



def sys_info():
    #log.info("System Information")
    uname = platform.uname()
    log.info({"System: "+uname.system,
        "Node Name: "+uname.node,
        "Release: "+uname.release,
        "Version: "+uname.version,
        "Machine: "+uname.machine})
        
class Plex_utills(Flask):
    def run(self, host=None, port=None, debug=True, threaded=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
          with self.app_context():
            sys_info()
            from app.setup import setup_helper
            setup_helper()
        super(Plex_utills, self).run(host='0.0.0.0', port=port, debug=debug, threaded=True, **options)

timezone = str(tzlocal.get_localzone())
class Config: 
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = timezone


app = Plex_utills(__name__)
app.config.from_object(Config())

if __name__ == "__main__":   
    app.run()


app.secret_key = '_3:WBH)qdY2WDe-_/h9r6)BD(Mp$SX' #os.urandom(42)

bootstrap = Bootstrap5(app)
#Bootstrap(app)

db_name = '/config/app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_BINDS'] = {
    'db1': 'sqlite:///' + db_name,
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
from app import routes, api, config, schedule


