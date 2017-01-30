#!/usr/bin/env bash

set -e

#This script should be used to load data into ES in local ES environment ONLY. Make sure the data file
#elastic_data.json is in the same dir as the script.

#Delete indices - for dev purpose only
curl -XDELETE 'http://localhost:9200/projects/'
curl -XDELETE 'http://localhost:9200/code/'

#Create Projects Index
curl -XPUT http://localhost:9200/projects/ -d '{
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
                    "filter": ["lowercase","my_synonym_filter","edgy_lang"]
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
                    "filter": ["lowercase","my_synonym_filter","edgy_title"]
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
curl -XPUT 'http://localhost:9200/code/'

curl -s -XPOST http://localhost:9200/_bulk --data-binary "@elastic_data.json"
