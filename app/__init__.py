from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from app.scripts import setup_logger
import os
import logging
import tzlocal
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

    from app.setup import setup_helper, backup_dirs
    backup_dirs
    setup_helper
    sys_info
    def run(self, host=None, port=None, debug=True, threaded=True, **options):
       # if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
       # from app.setup import setup_helper
            #with self.app_context():
       # sys_info()
       # setup_helper()
        super(Plex_utills, self).run(host='0.0.0.0', port=port, debug=debug, threaded=threaded, **options)

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

db_name = '/config/app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_BINDS'] = {
    'db1': 'sqlite:///' + db_name,
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
from app import routes, api, config, schedule