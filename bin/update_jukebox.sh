#!/bin/bash
# Update the jukebox file
# for running in cron
set -o errexit

wget -q http://frikanalen.no/api/jukebox_csv -O /tmp/jukebox.csv

if [ "$(cat /tmp/jukebox.csv | wc -l)" -lt 100 ]; then
  echo Jukebox file is too short
  exit 1
fi

cd "$(dirname "$0")"
mv ../cache/csvdb/jukebox_selection.csv ../cache/csvdb/jukebox_selection.csv.prev
cp /tmp/jukebox.csv ../cache/csvdb/jukebox_selection.csv
