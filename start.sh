#! /usr/bin/env sh
set -e
exec /usr/bin/supervisord
exec supervisorctl restart all