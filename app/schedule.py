from flask_apscheduler import APScheduler
from app import app, log
from apscheduler.triggers.cron import CronTrigger
from app.scripts import posters3d, hide4k, setup_logger, autocollections, collective4k, maintenance
from app.models import Plex
from app import db
import time
from croniter import croniter
import os
from plexapi.server import PlexServer
import plexapi



scheduler = APScheduler()
scheduler.init_app(app)

def update_scheduler(app):
    with app.app_context():
        scheduler.delete_all_jobs()
        scheduler.add_job('maintenance', func=maintenance, trigger=CronTrigger.from_crontab('0 4 * * *'))
        config = Plex.query.filter(Plex.id == '1')
        log.debug('Running Updater')
        def check_schedule_format(input):
            try:
                time.strptime(input, '%H:%M')
                return 'time trigger'
            except ValueError:
                if croniter.is_valid(input) == True:
                    return 'cron'
                else:
                    return log.error('Schedule for t1 is incorrect')       
        t1 = config[0].t1
        t2 = config[0].t2
        t3 = config[0].t3
        t4 = config[0].t4
        t5 = config[0].t5
        if config[0].posters4k == 1:
            if check_schedule_format(t1) == 'time trigger':
                scheduler.add_job('posters4k', func=collective4k, args=[app], trigger='cron', hour=t1.split(":")[0], minute=t1.split(":")[1])
            elif check_schedule_format(t1) == 'cron':
                scheduler.add_job('posters4k', func=collective4k, args=[app], trigger=CronTrigger.from_crontab(t1))
           #log.info("4K/HDR Posters schedule created for "+ t1)
        if config[0].posters3d == 1:
            if check_schedule_format(t5) == 'time trigger':
                scheduler.add_job('posters3d', func=posters3d, args=[app], trigger='cron', hour=t5.split(":")[0], minute=t5.split(":")[1])
            elif check_schedule_format(t5) == 'cron':
                scheduler.add_job('posters3d', func=posters3d, args=[app], trigger=CronTrigger.from_crontab(t5))
            #log.info("3D Posters schedule created for "+ t5)
        if config[0].hide4k == 1:
            if check_schedule_format(t4) == 'time trigger':
                scheduler.add_job('hide4k', func=hide4k, args=[app], trigger='cron', hour=t4.split(":")[0], minute=t4.split(":")[1])
            elif check_schedule_format(t4) == 'cron':
                scheduler.add_job('hide4k', func=hide4k, args=[app], trigger=CronTrigger.from_crontab(t4))
            #log.info("Hide 4k schedule created for "+ t4)
        if config[0].autocollections == 1:
            if check_schedule_format(t2) == 'time trigger':
                scheduler.add_job('autocollections', func=autocollections, args=[app], trigger='cron', hour=t2.split(":")[0], minute=t2.split(":")[1])
            elif check_schedule_format(t2) == 'cron':
                scheduler.add_job('autocollections', func=autocollections, args=[app], trigger=CronTrigger.from_crontab(t2))
            #log.info("Auto Collections schedule created for "+ t2)
        #if config[0].spoilers == 1:
        #    if check_schedule_format(t3) == 'time trigger':
        #        scheduler.add_job('spoilers', func=spoilers_scheduled, args=[app], trigger='cron', hour=t3.split(":")[0], minute=t3.split(":")[1])
        #    elif check_schedule_format(t3) == 'cron':
        #        scheduler.add_job('spoilers', func=spoilers_scheduled, args=[app], trigger=CronTrigger.from_crontab('0 0 * * 0'))
        for j in scheduler.get_jobs():
            log.info(j)
