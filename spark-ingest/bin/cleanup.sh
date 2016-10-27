#!/usr/bin/env bash

#Temporary script until we add batchid for every run
mkdir -p ~/dev/data

SEARCH_DATA_DIR="~/dev/data/esearch/"
INGEST_DATA_DIR="~/dev/data/ingest/"
PROCESS_DATA_DIR="~/dev/data/process/"

rm -r "$SEARCH_DATA_DIR"
rm -r "$INGEST_DATA_DIR"
rm -r "$PROCESS_DATA_DIR"

mkdir -p "$SEARCH_DATA_DIR/input/github"
mkdir -p "$INGEST_DATA_DIR/input/github"
mkdir -p "$PROCESS_DATA_DIR/input"

mkdir -p "$SEARCH_DATA_DIR/output"
mkdir -p "$INGEST_DATA_DIR/output"
mkdir -p "$PROCESS_DATA_DIR/output"

chmod -R 777 "$SEARCH_DATA_DIR"
chmod -R 777 "$INGEST_DATA_DIR"
chmod -R 777 "$PROCESS_DATA_DIR"

curl -XDELETE 'http://localhost:9200/projects/'

echo "Cleanup complete"