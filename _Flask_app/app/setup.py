import os
import sqlite3
import shutil
from plexapi.server import PlexServer
import re
from app import log
b_dir = '/config/backup/' 

def setup_helper():
    plexpath = ''
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
                pass
                #log.debug(repr(e))         
            c.close()
        def update_plex_path():
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
        add_new_columns()
        try:
            update_plex_path()
        except:
            raise Exception('looks like this is a first run')
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

def backup_dirs():
    log.info('creating backup directory now')
    if os.path.exists(b_dir):
        pass
        #log.info('Backup directory exists')
    else:
        os.makedirs(b_dir)

    if os.path.exists(b_dir+'/films'):
        pass
        #log.info('Backup directory exists')
    else:
        os.makedirs(b_dir+'/films')
        
    if os.path.exists(b_dir+'/tv/episodes'):
        #log.info('Backup directory exists')
        pass
    else:
        os.makedirs(b_dir+'/tv/episodes')
    if os.path.exists(b_dir+'/tv/bannered_episodes'):
        #log.info('Backup directory exists')
        pass
    else:
        os.makedirs(b_dir+'/tv/bannered_episodes')        
    if os.path.exists(b_dir+'bannered_films'):
        pass
        #log.info('Bannered Film folder exists')
    else:
        os.makedirs(b_dir+'bannered_films')
    if os.path.exists(b_dir+'/tv/bannered_seasons'):
        #log.info('Bannered Season folder exists')
        pass
    else:
        os.makedirs(b_dir+'/tv/bannered_seasons')  
    if os.path.exists(b_dir+'/tv/seasons'):
        #log.info('Season folder exists')
        pass
    else:
        os.makedirs(b_dir+'/tv/seasons')    
    os.chmod(b_dir , 0o777)
    for root,dirs,_ in os.walk(b_dir):
        for d in dirs :
            os.chmod(os.path.join(root,d) , 0o777)    
    
