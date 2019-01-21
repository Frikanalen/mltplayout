#!/bin/bash
path="$(dirname "$0")"
python $path/fetch_and_pickle_schedule.py 10 $path/../cache/dailyplan/
$path/update_jukebox.sh
python $path/playout_reload_schedule.py localhost 8889
