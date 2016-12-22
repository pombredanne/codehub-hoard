#!/bin/bash

#
# Loads JSON Data using the Elastic Search Bulk API.
#
# ASSUMPTIONS:
# -- Elastic Search is running
#

SUCCESS=0
ERROR=1
HOST=$1
DATA_FILE=$2
PORT=9200
INDEX=projects
DOC_TYPE=logs

# copy data file to server for Logstash to load
curl -XPOST http://$HOST:$PORT/$INDEX/$DOC_TYPE/_bulk --data-binary @$DATA_FILE

exit $SUCCESSS