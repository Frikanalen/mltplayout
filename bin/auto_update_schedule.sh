#!/bin/bash
path="$(dirname "$0")"
if pidof -o %PPID -x "auto_update_schedule.sh">/dev/null; then
    echo "Process already running"
    return;
fi
while true; do
    ~/frikanalen/env/bin/python ~/frikanalen/fkbeta/pickle_schedule.py
    $path/update_jukebox.sh
    python $path/playout_reload_schedule.py localhost 8889
    sleep 3600  # Refresh every hour
done
