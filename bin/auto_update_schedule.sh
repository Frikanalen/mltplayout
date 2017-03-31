#!/bin/bash

while true; do
    ~/frikanalen/env/bin/python ~/frikanalen/fkbeta/pickle_schedule.py
    python ~/mltplayout/bin/playout_reload_schedule.py localhost 8889
    sleep 3600  # Refresh every hour
done
