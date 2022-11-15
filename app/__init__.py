from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from app.scripts import spoilers_scheduled, posters3d, hide4k, setup_logger, autocollections, collective4k
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

setup_logger('Application', r"/logs/application_log.log")
log = logging.getLogger('Application')
b_dir = '/config/backup/' 

def setup_helper():
    plexpath = ''
    def continue_setup():
        def add_new_columns():
            log.debug('Adding new Columns')
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM plex_utills")
            config = c.fetchall()
            query1 = """ALTER TABLE plex_utills
                    ADD COLUMN autocollections INT
                    """
            query2 = """ALTER TABLE plex_utills        
                    ADD COLUMN default_poster INT
                    """
            query3 = """ALTER TABLE plex_utills        
                    ADD COLUMN tr_r_p_collection INT
                    """
            query4 = """ALTER TABLE plex_utills    
                    ADD COLUMN tautulli_server TEXT
                    """        
            query5 = """ALTER TABLE plex_utills    
                    ADD COLUMN tautulli_api TEXT
                    """
            query6 = """ALTER TABLE plex_utills    
                        ADD COLUMN mcu_collection INT
                        """      
            query7 = """ALTER TABLE plex_utills    
                        ADD COLUMN audio_posters INT
                        """
            query8 = """ALTER TABLE plex_utills    
                    ADD COLUMN loglevel INT
                    """           
            query9 = """ALTER TABLE plex_utills    
                    ADD COLUMN manualplexpath INT
                    """     
            query10 = """ALTER TABLE plex_utills    
                    ADD COLUMN manualplexpathfield TEXT
                    """                 
            query11 = """ALTER TABLE plex_utills    
                    ADD COLUMN skip_media_info INT
                    """    
            query12 = """ALTER TABLE plex_utills    
                    ADD COLUMN spoilers INT
                    """    
            query13 = """ALTER TABLE episodes    
                    ADD COLUMN show_season INT
                    """    
            query14 = """ALTER TABLE seasons    
                    ADD COLUMN checked INT
                    """      
            query15 = """ALTER TABLE films    
                    ADD COLUMN url TEXT
                    """                                                                                    
            try:
                c.execute(query1)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query2)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query3)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query4)
                
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query5)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query6)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query7)
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query8)
                
            except sqlite3.OperationalError as e:
                pass
            try:          
                c.execute(query9)
                
            except sqlite3.OperationalError as e:
                pass  
            try:
                c.execute(query10)
            except sqlite3.OperationalError as e:
                pass   
            try:
                c.execute(query11)
            except sqlite3.OperationalError as e:
                pass    
            try:
                c.execute(query12)
            except sqlite3.OperationalError as e:
                pass  
            try:
                c.execute(query13)
            except sqlite3.OperationalError as e:
                pass
            try:
                c.execute(query14)
            except sqlite3.OperationalError as e:
                pass 
            try:
                c.execute(query15)
            except sqlite3.OperationalError as e:
                pass                                                          
            try:
                api = config[0][32]
                loglevel = config[0][36]
                manpp = config[0][37]
                mediainfo = config[0][39]
                newhdr = config[0][28]
                if not api:
                    c.execute("UPDATE plex_utills SET tautulli_server = 'http://127.0.0.1:8181' where ID = 1")
                if not loglevel or loglevel == '0':
                    c.execute("UPDATE plex_utills SET loglevel = '1' WHERE ID = 1")    
                if not manpp:
                    c.execute("UPDATE plex_utills SET manualplexpath = '0' WHERE ID = 1")
                    c.execute("UPDATE plex_utills SET manualplexpathfield = 'None' WHERE ID = 1")
                if not mediainfo or mediainfo == 'None':
                    c.execute("UPDATE plex_utills SET skip_media_info = '0' WHERE ID = 1")
                if not newhdr or newhdr == 'None':
                    c.execute("UPDATE plex_utills SET new_hdr = '1' WHERE ID = 1")
                conn.commit()
            except (sqlite3.OperationalError, IndexError) as e:
                log.debug(repr(e))         
            c.close()
        def update_plex_path():
            log.debug('update plex path')
            import requests
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
                    log.info('Plexpath Manual override enabled') 
                    plexpath = config[0][38]
                    log.debug(plexpath)
                    log.debug('plexpath = '+plexpath)
                    c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
                    conn.commit()
                    c.close()
                    log.info("Setup Helper: Your plexpath has been changed from "+plexpath+" to '/films'")
                elif config[0][37] == 0:
                    filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
                    log.debug("Plex Movie location is: "+filepath)
                    try:
                        plexpath = '/'+filepath.split('/')[2]
                        plexpath = '/'+filepath.split('/')[1]
                        log.debug('plexpath split = '+plexpath)
                        log.debug('Testing to see if plexpath is mounted at root')
                    except IndexError as e:
                        log.debug(repr(e))
                        plexpath = '/'
                    log.debug('plexpath = '+plexpath)
                    c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
                    conn.commit()
                    c.close()
                    log.info("Setup Helper: Your plexpath has been changed from "+plexpath+" to '/films'")
            except Exception:
                log.error(repr(e))
                log.warning('This looks like a first run')
        def update_database():
            log.debug('update database')
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
                        log.debug(i.media[0].parts[0].file)
                        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                        log.debug(newdir)
                    elif config[0][37] == 0:
                        if config[0][5] == '/':
                            newdir = '/films'+i.media[0].parts[0].file
                            log.debug(newdir)
                        else:
                            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                            log.debug(newdir)
                    testfile = newdir+'test'
                    log.debug('Plex-Utills file path is here: '+newdir)
                    #try:
                    #    open(testfile, 'w')
                    #    log.info('Permissions, look to be correct')
                    #except PermissionError as e:
                    #    log.error(e)
                    #if os.path.exists(testfile) == True:
                    #    os.remove(testfile)
                    #break   
            except (plexapi.exceptions.NotFound, OSError, ConnectionError, NameError) as e:
                log.error(e)

        add_new_columns()
        try:
            update_plex_path()
        except:
            log.error("first run?")
        update_database()
        #add_database()
        add_new_table()
    def create_table():
          shutil.copy('app/static/default_db/default_app.db', '/config/app.db')
          log.debug('Copying table')
          continue_setup()
    def add_new_table():
        log.debug('Adding new table')
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor() 
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
                    	PRIMARY KEY("ID" AUTOINCREMENT)
                    ); """
            c.execute(table)
            conn.commit()
        except Exception as e:
            log.debug(repr(e))
    def add_ep_table():
        log.debug('Adding new table')
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor() 
            table = """CREATE TABLE "episodes" (
                    	"ID"	INTEGER NOT NULL UNIQUE,
                        "Show_season" TEXT,
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
                        "blurred"   INTEGER,
                    	PRIMARY KEY("ID" AUTOINCREMENT)
                    ); """
            c.execute(table)
            conn.commit()
        except Exception as e:
            log.debug(repr(e))  
    def add_season_table():
        log.debug('Adding new table')
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor() 
            table = """CREATE TABLE "seasons" (
                    	"ID"	INTEGER NOT NULL UNIQUE,
                    	"Title"	TEXT NOT NULL,
                    	"GUID"	TEXT NOT NULL,
                        "poster" TEXT,
                        "bannered_season" TEXT,
                        "checked" INTEGER,
                    	PRIMARY KEY("ID" AUTOINCREMENT)
                    ); """
            c.execute(table)
            conn.commit()
        except Exception as e:
            log.debug(repr(e)) 
    def table_check():
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM plex_utills")
            c.close()
            continue_setup()
        except sqlite3.OperationalError as e:
            log.debug(repr(e))
            create_table()
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM films")
            c.close()
            continue_setup()
        except sqlite3.OperationalError as e:
            log.debug(repr(e))
            add_new_table() 
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM episodes")
            try:
                q1 = """ALTER TABLE episodes    
                        ADD COLUMN blurred INT
                        """   

                c.execute(q1)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))  
            try:
                q3 = """ALTER TABLE episodes    
                        ADD COLUMN bannered_poster TEXT
                        """   

                c.execute(q3)
            except sqlite3.OperationalError as e:
                log.debug(repr(e))                                 
            try:
                q2 = """ALTER TABLE films
                        ADD COLUMN bannered_poster TEXT
                        """ 
                c.execute(q2)  
            except sqlite3.OperationalError as e:
                log.debug(repr(e))             
            c.close()
            continue_setup()
        except sqlite3.OperationalError as e:
            log.debug(repr(e))
            add_ep_table()    
        try:
            conn = sqlite3.connect('/config/app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM seasons")
            c.close()
            continue_setup()
        except sqlite3.OperationalError as e:
            log.debug(repr(e))
            add_season_table()                                  
    log.debug('Running setup Helper')
    table_check()

    if os.path.exists(b_dir+'/films'):
        log.info('Backup directory exists')
    else:
        os.makedirs(b_dir+'/films')
    if os.path.exists(b_dir+'/tv/episodes'):
        log.info('Backup directory exists')
    else:
        os.makedirs(b_dir+'/tv/episodes')
    if os.path.exists(b_dir+'/tv/bannered_episodes'):
        log.info('Backup directory exists')
    else:
        os.makedirs(b_dir+'/tv/bannered_episodes')        
    if os.path.exists(b_dir+'bannered_films'):
        log.info('Bannered Film folder exists')
    else:
        os.makedirs(b_dir+'bannered_films')
    if os.path.exists(b_dir+'/tv/bannered_seasons'):
        log.info('Bannered Season folder exists')
    else:
        os.makedirs(b_dir+'/tv/bannered_seasons')  
    if os.path.exists(b_dir+'/tv/seasons'):
        log.info('Season folder exists')
    else:
        os.makedirs(b_dir+'/tv/seasons')               

def update_scheduler():
    
    log.debug('Running Updater')
    scheduler.remove_all_jobs()
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    def check_schedule_format(input):
        try:
            time.strptime(input, '%H:%M')
            return 'time trigger'
        except ValueError:
            if croniter.is_valid(input) == True:
                return 'cron'
            else:
                return log.error('Schedule for t1 is incorrect')       
    t1 = config[0][7]
    t2 = config[0][8]
    t3 = config[0][9]
    t4 = config[0][10]
    t5 = config[0][11]
    if config[0][13] == 1:
        if check_schedule_format(t1) == 'time trigger':
            scheduler.add_job('posters4k', func=collective4k, trigger='cron', hour=t1.split(":")[0], minute=t1.split(":")[1])
        elif check_schedule_format(t1) == 'cron':
            scheduler.add_job('posters4k', func=collective4k, trigger=CronTrigger.from_crontab(t1))
        log.info("4K/HDR Posters schedule created for "+ t1)
    if config[0][16] == 1:
        if check_schedule_format(t5) == 'time trigger':
            scheduler.add_job('posters3d', func=posters3d, trigger='cron', hour=t5.split(":")[0], minute=t5.split(":")[1])
        elif check_schedule_format(t5) == 'cron':
            scheduler.add_job('posters3d', func=posters3d, trigger=CronTrigger.from_crontab(t5))
        log.info("3D Posters schedule created for "+ t5)
    if config[0][20] == 1:
        if check_schedule_format(t4) == 'time trigger':
            scheduler.add_job('hide4k', func=hide4k, trigger='cron', hour=t4.split(":")[0], minute=t4.split(":")[1])
        elif check_schedule_format(t4) == 'cron':
            scheduler.add_job('hide4k', func=hide4k, trigger=CronTrigger.from_crontab(t4))
        log.info("Hide 4k schedule created for "+ t4)
    if config[0][18] == 1:
        if check_schedule_format(t2) == 'time trigger':
            scheduler.add_job('autocollections', func=autocollections, trigger='cron', hour=t2.split(":")[0], minute=t2.split(":")[1])
        elif check_schedule_format(t2) == 'cron':
            scheduler.add_job('autocollections', func=autocollections, trigger=CronTrigger.from_crontab(t2))
        log.info("Auto Collections schedule created for "+ t2)
    if config[0][40] == 1:
        if check_schedule_format(t3) == 'time trigger':
            scheduler.add_job('spoilers', func=spoilers_scheduled, trigger='cron', hour=t3.split(":")[0], minute=t3.split(":")[1])
        elif check_schedule_format(t3) == 'cron':
            scheduler.add_job('spoilers', func=spoilers_scheduled, trigger=CronTrigger.from_crontab('0 0 * * 0'))
    for j in scheduler.get_jobs():
        log.info(j)
    def update_plex_path():
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
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
        log.debug('Updating plex path')
        if config[0][37] == 1:
            log.info('Plexpath Manual override enabled')
            plexpath = config[0][38]
        elif config[0][37] == 0:
            filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
            log.debug("Plex Movie location is: "+filepath)
            try:
                plexpath = '/'+filepath.split('/')[2]
                plexpath = '/'+filepath.split('/')[1]
                log.debug('plexpath split = '+plexpath)
                log.debug('Testing to see if plexpath is mounted at root')
            except IndexError as e:
                log.debug(repr(e))
                plexpath = '/'
        log.debug('plexpath = '+plexpath)
        c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
        conn.commit()
        c.close()
        log.info("Setup Helper: Your plexpath has been changed from "+plexpath+" to '/films'")
    try:
        update_plex_path()
    except (plexapi.exceptions.NotFound, OSError) as e:
        log.error(e)

def sys_info():
    log.info("System Information")
    uname = platform.uname()
    log.info({"System: "+uname.system,
        "Node Name: "+uname.node,
        "Release: "+uname.release,
        "Version: "+uname.version,
        "Machine: "+uname.machine})
        
class Plex_utills(Flask):
    def run(self, host=None, port=None, debug=True, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
          with self.app_context():
            sys_info()
            from app.scripts import maintenance
            scheduler.add_job('maintenance', func=maintenance, trigger=CronTrigger.from_crontab('0 4 * * *'))
            setup_helper()
        super(Plex_utills, self).run(host='0.0.0.0', port=port, debug=debug, **options)

timezone = str(tzlocal.get_localzone())
class Config: 
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = timezone


app = Plex_utills(__name__)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()   
try:
    setup_helper()
    update_scheduler()
except:
    log.warning("is this a first run?")
if __name__ == "__main__":   
    app.run()


app.secret_key = '_3:WBH)qdY2WDe-_/h9r6)BD(Mp$SX' #os.urandom(42)

bootstrap = Bootstrap5(app)
#Bootstrap(app)

db_name = '/config/app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_BINDS'] = {
    'db1': 'sqlite:///' + db_name,
    #'db2': 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user=mysql_user, password=mysql_pass, server=mysql_url, database=mysql_database)
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from app import routes


