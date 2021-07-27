#!/bin/bash
FILE=/config/config.ini
if test -f "$FILE"
then
    echo "$FILE exists"
else
    cp -r /app/config/config.ini /config/config.ini
    echo "copied files"
fi

python -u ./run_all.py
