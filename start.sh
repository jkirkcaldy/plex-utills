#! /usr/bin/env sh
/usr/sbin/nginx
/usr/local/bin/gunicorn --chdir /app main:app -w 9 --threads 2 -b 0.0.0.0:5000 
