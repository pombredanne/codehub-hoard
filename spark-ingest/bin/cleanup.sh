#!/usr/bin/env bash

#Temporary script until we add batchid for every run

DATA_DIR=${ingest.data.dir}

if [ ! -d $DATA_DIR ]; then
 mkdir -p $DATA_DIR
fi

SEARCH_DATA_DIR="${DATA_DIR}/esearch/"
INGEST_DATA_DIR="${DATA_DIR}/ingest/"
PROCESS_DATA_DIR="${DATA_DIR}/process/"

rm -r "$SEARCH_DATA_DIR"
rm -r "$INGEST_DATA_DIR"
rm -r "$PROCESS_DATA_DIR"

mkdir -p "$SEARCH_DATA_DIR/input"
mkdir -p "$INGEST_DATA_DIR/input"
mkdir -p "$PROCESS_DATA_DIR/input"

mkdir -p "$SEARCH_DATA_DIR/output"
mkdir -p "$INGEST_DATA_DIR/output"
mkdir -p "$PROCESS_DATA_DIR/output"

chmod -R 777 "$SEARCH_DATA_DIR"
chmod -R 777 "$INGEST_DATA_DIR"
chmod -R 777 "$PROCESS_DATA_DIR"

curl -XDELETE 'http://localhost:9200/projects/'
curl -XDELETE 'http://localhost:9200/code/'

echo "Cleanup complete"