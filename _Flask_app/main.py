from app import app


def sys_info():
    import platform

    uname = platform.uname()
    log.info({"System: "+uname.system,
        "Node Name: "+uname.node,
        "Release: "+uname.release,
        "Version: "+uname.version,
        "Machine: "+uname.machine})
    from app.setup import setup_helper
    setup_helper()

plexpath = ''
import sqlite3
import shutil
from app import log
def continue_setup():
    
    def add_new_columns():
        #log.debug('Adding new Columns')
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
        query16 = """ALTER TABLE plex_utills    
                ADD COLUMN migrated INT
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
            c.execute(query16)
        except sqlite3.OperationalError as e:
            pass                                                              
        try:
            api = config[0][32]
            loglevel = config[0][36]
            manpp = config[0][37]
            mediainfo = config[0][39]
            newhdr = config[0][28]
            migrated = config[0][41]
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
            if not migrated:
                c.execute("UPDATE plex_utills SET migrated = '0' WHERE ID = 1")                
            conn.commit()
        except (sqlite3.OperationalError, IndexError) as e:
            pass
            #log.debug(repr(e))         
        c.close()

    add_new_columns()
    #try:
    #    update_plex_path()
    #except:
    #    raise Exception('looks like this is a first run')
    add_new_table()
def create_table():
      shutil.copy('app/static/default_db/default_app.db', '/config/app.db')
      #log.debug('Copying table')
      continue_setup()
def add_new_table():
    #log.debug('Adding new table')
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
        pass #log.debug(repr(e))
def add_ep_table():
    #log.debug('Adding new table')
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
        pass #log.debug(repr(e))  
def add_season_table():
    #log.debug('Adding new table')
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor() 
        table = """CREATE TABLE "seasons" (
                	"ID"	INTEGER NOT NULL UNIQUE,
                	"Title"	TEXT NOT NULL,
                	"GUID"	TEXT NOT NULL,
                    "poster" TEXT,
                    "bannered_poster" TEXT,
                    "checked" INTEGER,
                	PRIMARY KEY("ID" AUTOINCREMENT)
                ); """
        c.execute(table)
        conn.commit()
    except Exception as e:
        pass #log.debug(repr(e)) 
def table_check():
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        c.close()
        continue_setup()
    except sqlite3.OperationalError as e:
        #log.debug(repr(e))
        create_table()
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM films")
        c.close()
        continue_setup()
    except sqlite3.OperationalError as e:
        #log.debug(repr(e))
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
            pass # log.debug(repr(e))  
        try:
            q3 = """ALTER TABLE episodes    
                    ADD COLUMN bannered_poster TEXT
                    """   
            c.execute(q3)
        except sqlite3.OperationalError as e:
            pass #log.debug(repr(e))                                 
        try:
            q2 = """ALTER TABLE films
                    ADD COLUMN bannered_poster TEXT
                    """ 
            c.execute(q2)  
        except sqlite3.OperationalError as e:
            pass #log.debug(repr(e))             
        c.close()
        continue_setup()
    except sqlite3.OperationalError as e:
        #log.debug(repr(e))
        add_ep_table()    
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM seasons")
        c.close()
        continue_setup()
    except sqlite3.OperationalError as e:
        pass #log.debug(repr(e))
        add_season_table()                                  
log.debug('Running setup Helper')
table_check()
from app import log
import os
b_dir = '/config/backup/' 
try:
    log.info('creating backup directory now')
    if os.path.exists(b_dir):
        pass
    else:
        os.makedirs(b_dir)
    if os.path.exists(b_dir+'/films'):
        pass
    else:
        os.makedirs(b_dir+'/films')

    if os.path.exists(b_dir+'/tv/episodes'):
        pass
    else:
        os.makedirs(b_dir+'/tv/episodes')
    if os.path.exists(b_dir+'/tv/bannered_episodes'):
        pass
    else:
        os.makedirs(b_dir+'/tv/bannered_episodes')        
    if os.path.exists(b_dir+'bannered_films'):
        pass
    else:
        os.makedirs(b_dir+'bannered_films')
    if os.path.exists(b_dir+'/tv/bannered_seasons'):
        pass
    else:
        os.makedirs(b_dir+'/tv/bannered_seasons')  
    if os.path.exists(b_dir+'/tv/seasons'):
        pass
    else:
        os.makedirs(b_dir+'/tv/seasons')   

except: pass

try: 
    for root,dirs,files in os.walk('/config'):
        os.chmod(root, 0o777)
        for f in files :
            os.chmod(os.path.join(root,f) , 0o777) 
        for d in dirs :
            os.chmod(os.path.join(root,d) , 0o777)  
except Exception as e:
    log.error(repr(e))

if __name__ == '__main__':
    app.run()