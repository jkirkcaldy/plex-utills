#!/bin/bash

echo "Running Pre-start script"

RANDOM_ADMIN_PASS=`python3 -c "import secrets;chars = 'abcdefghijklmnopqrstuvwxyz0123456789';print(''.join(secrets.choice(chars) for i in range(10)))"`
ADMIN_PASSWORD=${ADMIN_PASSWORD:-$RANDOM_ADMIN_PASS}
echo "Getting migrations"
python3 manage.py makemigrations
echo "Running migrations service"
python3 manage.py migrate
EXISTING_INSTALLATION=`echo "from django.contrib.auth.models import User; print(User.objects.exists())" |python3  manage.py shell`
if [ "$EXISTING_INSTALLATION" = "True" ]; then 
    echo "Users exist, skipping creating admin user"
else
    echo "Creating admin user"
	# post_save, needs redis to succeed (ie. migrate depends on redis)
    DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD python3 manage.py createsuperuser \
        --no-input \
        --username=$ADMIN_USERNAME \
        --email=$ADMIN_EMAIL
    echo "Created admin user with password: $ADMIN_PASSWORD"
fi   






#### Supervisord Configurations #####

cp deploy/supervisord/supervisord-debian.conf /etc/supervisor/conf.d/supervisord-debian.conf

echo "Enabling uwsgi app server"
cp deploy/supervisord/supervisord-uwsgi.conf /etc/supervisor/conf.d/supervisord-uwsgi.conf
echo "Enabling nginx as uwsgi app proxy and media server"
cp deploy/nginx/server /etc/nginx/sites-available/default
cp deploy/nginx/uwsgi_conf /etc/nginx/sites-enabled/uwsgi_conf
cp deploy/nginx/nginx.conf /etc/nginx/
cp deploy/nginx/mime.types /etc/nginx/
cp deploy/supervisord/supervisord-nginx.conf /etc/supervisor/conf.d/supervisord-nginx.conf
echo "Enabling celery-beat scheduling server"
cp deploy/supervisord/supervisord-beat.conf /etc/supervisor/conf.d/supervisord-celery_beat.conf
echo "Enabling Task Worker"
cp deploy/supervisord/supervisord-plex-utils.conf /etc/supervisor/conf.d/supervisord-plex-utils.conf

if [ X"$ENABLE_REDIS" = X"yes" ] ; then
    echo "Enabling Redis"
    mkdir /redis
    cp deploy/supervisord/supervisord-redis.conf /etc/supervisor/conf.d/supervisord-redis.conf
fi