#!/usr/bin/env bash


INGEST_HOME=${ingest.home}

#Restore old config file settings after deploying. This will be removed once we
#have a mechanism to encrypt the github tokens in config files
cp $INGEST_HOME/config/application_orig.conf $INGEST_HOME/config/application.conf
cp $INGEST_HOME/ingress/github/code/ingest_orig.conf $INGEST_HOME/ingress/github/code/ingest.conf
cp $INGEST_HOME/ingress/github/sonar/ingest_orig.conf $INGEST_HOME/ingress/github/sonar/ingest.conf

#AWS deploys the apps as root, need to change the ownership to ec2-user after deploying
cd $INGEST_HOME
cd ../
sudo chown -R ec2-user:ec2-user heimdall


#Start creating the data directory structure
DATA_DIR=${ingest.data.dir}

if [ ! -d $DATA_DIR ]; then
    mkdir -p $DATA_DIR

    SEARCH_DATA_DIR="${DATA_DIR}/esearch/"
    PROCESS_DATA_DIR="${DATA_DIR}/process/"

    rm -r "$SEARCH_DATA_DIR"
    rm -r "$PROCESS_DATA_DIR"

    mkdir -p "$SEARCH_DATA_DIR/input"
    mkdir -p "$PROCESS_DATA_DIR/input"

    mkdir -p "$SEARCH_DATA_DIR/output"
    mkdir -p "$SEARCH_DATA_DIR/kindred"
    mkdir -p "$PROCESS_DATA_DIR/output"

    chmod -R 777 "$SEARCH_DATA_DIR"
    chmod -R 777 "$PROCESS_DATA_DIR"

    #Delete indices - for dev purpose only
    curl -XDELETE 'http://${elastic.server.url}/projects/'
    curl -XDELETE 'http://${elastic.server.url}/code/'

    #Create Projects Index
    curl -XPUT http://${elastic.server.url}/projects/ -d '{
        "mappings": {
            "project": {
                "_timestamp": {
                        "enabled": true
                 },
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
                        "filter": ["lowercase","my_synonym_filter","edgy_title"]
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
                        "filter": ["lowercase","my_synonym_filter","edgy_lang"]
                    }
                },
                "filter": {
                    "edgy_title": {
                        "type": "edge_ngram",
                        "min_gram": "4",
                        "max_gram": "10"
                    },
                    "edgy_lang": {
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

    #Create empty index for code
    curl -XPUT http://${elastic.server.url}/code/ -d '{
        "mappings": {
            "project": {
                "_timestamp": {
                        "enabled": true
                 }
            }
        }
    }'

    echo "Cleanup complete"
fi

exit 0
