#!/usr/bin/env bash

#AWS deploys the apps as root, need to change the ownership to ec2-user after deploying
INGEST_HOME=${ingest.home}
cd $INGEST_HOME
cd ../
sudo chown -R ec2-user:ec2-user heimdall

DATA_DIR=${ingest.data.dir}

if [ ! -d $DATA_DIR ]; then
    mkdir -p $DATA_DIR

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
        "mappings": {
            "project": {
                "properties": {
                    "project_name": {
                        "type": "string",
                          "analyzer": "title_analyzer"
                    },
                    "project_description": {
                        "type": "string",
                            "analyzer": "grimdall_analyzer"
                    },
                    "content": {
                        "type": "string",
                            "analyzer": "grimdall_analyzer"
                    },
                    "language": {
                        "type": "string",
                            "analyzer": "language_analyzer"
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
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "title_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": "my_char",
                        "filter": ["lowercase","my_synonym_filter","edgy"]
                    },
                    "grimdall_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": "my_char",
                        "filter": ["lowercase","my_synonym_filter","my_stop","my_snow"]
                    },
                    "language_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": "my_char",
                        "filter": ["lowercase","my_synonym_filter","edgy"]
                    }
                },
                "filter": {
                    "edgy": {
                        "type": "edge_ngram",
                        "min_gram": "2",
                        "max_gram": "10"
                    },
                    "my_synonym_filter": {
                        "type": "synonym",
                        "synonyms": ["javascript=>js"]
                    },
                    "my_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "my_snow": {
                        "type": "snowball",
                        "language": "English"
                    }
                },
                "char_filter": {
                    "my_char": {
                        "type": "mapping",
                        "mappings": ["++ => plusplus", "# => sharp"]
                    }
                }
            }
        }
    }'

    #TODO add mapping for code index

    echo "Cleanup complete"
fi