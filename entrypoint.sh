#!/bin/bash
set -e



mkdir -p /logs/nginx
mkdir -p /logs/supervisor
mkdir -p /config

ENV_EXISTS=/config/.env
if test -f "$ENV_EXISTS" ; then
    echo "$ENV_EXISTS exists"
else
    touch /config/.env
    cat /plex-utils/deploy/env > /config/.env
fi
FILE=/config/django_db.sqlite3
if test -f "$FILE"; then
    echo "$FILE exists."
else
    echo "Copying database"
    cp deploy/django_db.sqlite3 /config/django_db.sqlite3
fi

TARGET_GID=$(stat -c "%g" /plex-utils)

EXISTS=$(cat /etc/group | grep $TARGET_GID | wc -l)

 #Create new group using target GID and add www-data user
if [ $EXISTS == "0" ]; then
    groupadd -g $TARGET_GID tempgroup
    usermod -a -G tempgroup www-data
else
   # GID exists, find group name and add
    GROUP=$(getent group $TARGET_GID | cut -d: -f1)
    usermod -a -G $GROUP www-data
fi
echo "changing permissions, this could take a minute..."

# We should do this only for folders that have a different owner, since it is an expensive operation
echo "application files..."

find /plex-utils/plex_utils/  ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/api/  ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/posters/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/utils/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/deploy/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/static/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /plex-utils/templates/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +

echo "logs..."
find /logs/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +
find /config/ ! \( -user www-data -group $TARGET_GID \) -exec chown www-data:$TARGET_GID {} +

chmod +x /plex-utils/start.sh /plex-utils/prestart.sh

exec "$@"