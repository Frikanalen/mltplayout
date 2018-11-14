#!/bin/bash
# Update the jukebox file
# for running in cron
set -o errexit

TMPFILE=$(mktemp --tmpdir=/tmp frikanalen_jukebox_XXXXXX)

wget -q http://frikanalen.no/api/jukebox_csv -O $TMPFILE

if [ "$(cat $TMPFILE | wc -l)" -lt 100 ]; then
  echo Jukebox file is too short
  exit 1
fi

cd "$(dirname "$0")"
if [ -e ../cache/csvdb/jukebox_selection.csv ] ; then
    mv ../cache/csvdb/jukebox_selection.csv ../cache/csvdb/jukebox_selection.csv.prev
fi;

mv $TMPFILE ../cache/csvdb/jukebox_selection.csv
