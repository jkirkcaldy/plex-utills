from flask import Flask
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from app.scripts import posters4k, posters3d, hide4k, disney, pixar, migrate, restore_posters, fresh_hdr_posters
import os
from flask_apscheduler import APScheduler
import sqlite3
import logging
import shutil
from plexapi.server import PlexServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("app/logs/application_log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) 

def update_scheduler():
  logger = logging.getLogger('Scheduler')
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler("app/logs/log.log")
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  scheduler.remove_all_jobs()
  conn = sqlite3.connect('app/app.db')
  c = conn.cursor()
  c.execute("SELECT * FROM plex_utills")
  config = c.fetchall()
  c.close()
  t1 = config[0][7]
  t2 = config[0][8]
  t3 = config[0][9]
  t4 = config[0][10]
  t5 = config[0][11]
  if config[0][13] == 1:
    scheduler.add_job('posters4k', func=posters4k, trigger='cron', hour=t1.split(":")[0], minute=t1.split(":")[1])
    logger.info("4K/HDR Posters schedule created for "+ t1)
  if config[0][16] == 1:
    scheduler.add_job('posters3d', func=posters3d, trigger='cron', hour=t5.split(":")[0], minute=t5.split(":")[1])
    logger.info("3D Posters schedule created for "+ t5)
  if config[0][20] == 1:
    scheduler.add_job('hide4k', func=hide4k, trigger='cron', hour=t4.split(":")[0], minute=t4.split(":")[1])
    logger.info("Hide 4k schedule created for "+ t4)
  if config[0][18] == 1:
    scheduler.add_job('disney', func=disney, trigger='cron', hour=t2.split(":")[0], minute=t2.split(":")[1])
    logger.info("Disney Collection schedule created for "+ t2)
  if config[0][19] == 1:
    scheduler.add_job('pixar', func=pixar, trigger='cron', hour=t3.split(":")[0], minute=t3.split(":")[1])
    logger.info("Pixar Collection schedule created for "+ t3)

def setup_helper():
    def create_table():
        shutil.copy('app/static/default_db/default_app.db', 'app/app.db')
    def continue_setup():
        conn = sqlite3.connect('app/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        config = c.fetchall()
    
        logger.info("Setup Helper: Going though the setup helper.")
    
        
        
        try:
            plex = PlexServer(config[0][1], config[0][2])
            films = plex.library.section(config[0][3])
            media_location = films.search()
            filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
            plexpath = '/'+filepath.split('/')[1]
    
            c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
            conn.commit()
            c.close()
            logger.info("Setup Helper: Your plexpath has been changed to "+plexpath)
            
        except OSError as e:
            if e.errno == 111: 
                logger.warning("Setup Helper: Cannont connect to your plex server, this may be because it is the first run and you haven't changed the config yet.")

    def table_check():
        database = os.path.exists('app/app.db')
        if database == True:
            continue_setup()
        else:
            create_table()
    table_check()
SCHEDULER_API_ENABLED = True

class Plex_utills(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
          with self.app_context():
            setup_helper()
        super(Plex_utills, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = Plex_utills(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
setup_helper()
update_scheduler()
if __name__ == "__main__":
  app.run()


app.secret_key = os.urandom(42)


Bootstrap(app)
db_name = 'app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from app import routes