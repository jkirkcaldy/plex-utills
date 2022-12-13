import logging
from flask import render_template, flash, request, redirect, send_file
from app import db
from app import app
from app.forms import AddRecord_config, AddRecord_config_options, admin_config
from app.models import Plex, film_table, ep_table, season_table
import threading
from threading import Thread
import datetime

import os
from app import scripts 
import asyncio
date = datetime.datetime.now()
date = date.strftime("%y.%m.%d-%H%M")
from app.routes import log, version
from app.schedule import update_scheduler

########## CONFIG PAGES #########
@app.route('/config', methods=['POST', 'GET'])
def config():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config()
        form.backup.default = plex.backup
        form.restore_from_tmdb.default = plex.tmdb_restore
        form.process()
        return render_template('config.html', plex=plex, form=form, pagetitle='Config', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config()
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
        plex.tautulli_server = request.form['tautulli_server']
        plex.tautulli_api = request.form['tautulli_api']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            update_scheduler(app)
            return render_template('result.html', message=message, pagetitle='Config Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config.html', plex=plex, form=form, pagetitle='Error', version=version)

@app.route('/config_options', methods=['POST', 'GET'])
def config_options():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config_options()
        form.skip_media_info.default = plex.skip_media_info
        form.posters4k.default = plex.posters4k
        form.mini4k.default = plex.mini4k
        form.hdr.default = plex.hdr
        form.recreate_hdr.default = plex.recreate_hdr
        form.posters3d.default = plex.posters3d
        form.tv4kposters.default = plex.tv4kposters
        form.films4kposters.default = plex.films4kposters
        form.mini3d.default = plex.mini3d
        form.hide4k.default = plex.hide4k
        form.transcode.default = plex.transcode
        form.pixar.default = plex.pixar
        form.disney.default = plex.disney
        form.default_poster.default = plex.default_poster
        form.mcu_collection.default = plex.mcu_collection
        form.autocollections.default = plex.autocollections
        form.tr_r_p_collection.default = plex.tr_r_p_collection
        form.audio_posters.default = plex.audio_posters
        form.spoilers.default = plex.spoilers
        form.process()
        return render_template('config_options.html', plex=plex, form=form, pagetitle='Config Options', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = AddRecord_config_options()
        plex.posters4k = request.form['posters4k']
        plex.films4kposters = request.form['films4kposters']
        plex.tv4kposters = request.form['tv4kposters']
        plex.mini4k = request.form['mini4k']
        plex.hdr  = request.form['hdr']
        plex.recreate_hdr = request.form['recreate_hdr']
        plex.posters3d = request.form['posters3d']
        plex.mini3d = request.form['mini3d']
        plex.hide4k = request.form['hide4k']
        plex.transcode = request.form['transcode']
        plex.disney = request.form['disney']
        plex.pixar = request.form['pixar']
        plex.mcu_collection = request.form['mcu_collection']
        plex.default_poster = request.form['default_poster']
        plex.autocollections = request.form['autocollections']
        plex.tr_r_p_collection = request.form['tr_r_p_collection']
        plex.audio_posters = request.form['audio_posters']
        plex.skip_media_info = request.form['skip_media_info']
        plex.spoilers = request.form['spoilers']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            update_scheduler(app)
            return render_template('result.html', message=message, pagetitle='Config Options Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config_options.html', plex=plex, form=form, pagetitle='Error', version=version)


@app.route('/admin_config', methods=['POST', 'GET'])
def admin_config_form():
    if request.method=='GET':
        plex = Plex.query.filter(Plex.id == '1').first()
        form = admin_config()
        form.skip_media_info.default = plex.skip_media_info
        form.manualplexpath.default = plex.manualplexpath
        form.loglevel.default = plex.loglevel
        form.backup.default = plex.backup
        form.restore_from_tmdb.default = plex.tmdb_restore
        form.posters4k.default = plex.posters4k
        form.mini4k.default = plex.mini4k
        form.hdr.default = plex.hdr
        form.recreate_hdr.default = plex.recreate_hdr
        form.posters3d.default = plex.posters3d
        form.tv4kposters.default = plex.tv4kposters
        form.films4kposters.default = plex.films4kposters
        form.mini3d.default = plex.mini3d
        form.hide4k.default = plex.hide4k
        form.transcode.default = plex.transcode
        form.pixar.default = plex.pixar
        form.disney.default = plex.disney
        form.default_poster.default = plex.default_poster
        form.mcu_collection.default = plex.mcu_collection
        form.autocollections.default = plex.autocollections
        form.tr_r_p_collection.default = plex.tr_r_p_collection
        form.audio_posters.default = plex.audio_posters
        form.spoilers.default = plex.spoilers
        form.process()
        return render_template('admin_config.html', plex=plex, form=form, pagetitle='Config Options', version=version)
    if request.method=='POST':
        id = request.form['id_field']
        plex = Plex.query.filter(Plex.id == '1').first()
        form = admin_config()
        plex.loglevel = request.form['loglevel']
        plex.posters4k = request.form['posters4k']
        plex.films4kposters = request.form['films4kposters']
        plex.tv4kposters = request.form['tv4kposters']
        plex.mini4k = request.form['mini4k']
        plex.hdr  = request.form['hdr']
        plex.recreate_hdr = request.form['recreate_hdr']
        plex.posters3d = request.form['posters3d']
        plex.mini3d = request.form['mini3d']
        plex.hide4k = request.form['hide4k']
        plex.transcode = request.form['transcode']
        plex.disney = request.form['disney']
        plex.pixar = request.form['pixar']
        plex.mcu_collection = request.form['mcu_collection']
        plex.default_poster = request.form['default_poster']
        plex.autocollections = request.form['autocollections']
        plex.tr_r_p_collection = request.form['tr_r_p_collection']
        plex.audio_posters = request.form['audio_posters']
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
        plex.tautulli_server = request.form['tautulli_server']
        plex.tautulli_api = request.form['tautulli_api']
        plex.manualplexpath = request.form['manualplexpath']
        plex.manualplexpathfield = request.form['manualplexpathfield']
        plex.mountedpath = request.form['mountedpath']
        plex.skip_media_info = request.form['skip_media_info']
        plex.spoilers = request.form['spoilers']
        if form.validate_on_submit():
            db.session.commit()
            message = f"The data for {plex.plexurl} has been updated."
            scripts.logger_start()
            update_scheduler(app)
            return render_template('result.html', message=message, pagetitle='Config Options Updated', version=version)
        else:
            Plex.id = id
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in {}: {}".format(
                        getattr(form, field).label.text,
                        error
                    ), 'error')
            return render_template('config_options.html', plex=plex, form=form, pagetitle='Error', version=version)
