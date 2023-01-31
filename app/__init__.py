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




        
class Plex_utills(Flask):

    def run(self, host=None, port=None, debug=False, threaded=True, **options):
        super(Plex_utills, self).run(host='0.0.0.0', port=port, debug=True, threaded=threaded, **options)

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