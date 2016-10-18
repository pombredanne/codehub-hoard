#!/bin/bash

#
# This script drops all indices and data from the Elastic Search and reloads it fresh using the Bulk API
#
# ASSUMPTIONS:
# -- Elastic Search and Logstash are both installed and running
# -- Script is executed on the host that ES and LS are installed on.
# -- Data files are located in the same directory as this script
#
SUCCESS=0
ERROR=1
HOST=$1
DATA_FILE=$2
PORT=9200
INDEX=projects

# Deleete Indices
curl -XDELETE http://$HOST:$PORT/$INDEX
./load-search-data.sh $HOST $DATA_FILE

exit $SUCCESS
