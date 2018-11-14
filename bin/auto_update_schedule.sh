#!/bin/bash
path="$(dirname "$0")"
if pidof -o %PPID -x "auto_update_schedule.sh">/dev/null; then
    echo "Process already running"
    return;
fi
while true; do
    if [ -n $VIRTUAL_ENV ] ; then
    $VIRTUAL_ENV/bin/python ~/frikanalen/fkbeta/pickle_schedule.py
    $path/update_jukebox.sh
    $VIRTUAL_ENV/bin/python $path/playout_reload_schedule.py localhost 8889
    sleep 3600  # Refresh every hour
fi;
done
