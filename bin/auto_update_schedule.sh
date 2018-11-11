#!/bin/bash
path="$(dirname "$0")"
~/frikanalen/env/bin/python ~/frikanalen/fkbeta/pickle_schedule.py
$path/update_jukebox.sh
python $path/playout_reload_schedule.py localhost 8889
