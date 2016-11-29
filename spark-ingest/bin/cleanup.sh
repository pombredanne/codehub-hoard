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
mkdir -p "$PROCESS_DATA_DIR/input/updates"

mkdir -p "$SEARCH_DATA_DIR/output"
mkdir -p "$INGEST_DATA_DIR/output"
mkdir -p "$PROCESS_DATA_DIR/output"

chmod -R 777 "$SEARCH_DATA_DIR"
chmod -R 777 "$INGEST_DATA_DIR"
chmod -R 777 "$PROCESS_DATA_DIR"

curl -XDELETE 'http://${elastic.server.url}/projects/'
curl -XDELETE 'http://${elastic.server.url}/code/'

curl -XPUT http://${elastic.server.url}/projects/ -d '{
    "mappings" : {
        "project" : {
            "properties" : {
                "project_name" : {
                    "type" : "string"
                },
                "project_description" : {
                    "type" : "string"
                },
                "content" : {
                    "type" : "string"
                },
                "contributors_list" : {
                    "type" : "object"
                },
                "suggest" : {
                    "type" : "completion",
                    "analyzer" : "simple",
                    "search_analyzer" : "simple"
                }
            }
        }
    }
}'

#TODO add mapping for code index

echo "Cleanup complete"