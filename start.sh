#!/bin/bash
cp /app/app/static/dockerfiles/default /etc/nginx/sites-enabled/default
cp /app/app/static/dockerfiles/plex-utills.conf /etc/supervisor/conf.d/plex-utills.conf

systemctl restart nginx
supervisorctl reload
