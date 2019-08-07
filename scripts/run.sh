#!/bin/sh
set -e

TABLES_PATH=$KBC_DATADIR/out/tables
FILES_PATH=$KBC_DATADIR/out/files

if [ "$(ls -A $TABLES_PATH)" ]; then
    TABLES_PATH=$TABLES_PATH/*
     rm -r $TABLES_PATH
fi

if [ "$(ls -A $FILES_PATH)" ]; then
    FILES_PATH=$FILES_PATH/*
     rm -r $FILES_PATH
fi

python /code/src/main.py