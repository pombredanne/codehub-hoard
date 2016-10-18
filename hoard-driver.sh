#!/bin/bash

#
#
# This driver runs all the data hoarding from Github, loads Elastic Search, loads Dependencis, and loads Dexi.
#
# Requirements:
#   1: Python 2.7 installed (see install for your OS)
#   2: pip is installed
#   3: virtualenv installed (pip install virtualenv)
#   4: Make sure you have ALL the settings configured before kicking off the driver
#       - ingress/github/project/ingest.conf
#       - ingress/github/code/ingest.conf
#
# Example:  ./heimdall-driver.sh ALL DEV 1.2.3.4 11.22.33.44
#

GITHUB_SYSTEM=$1
ENV_TO_UPDATE=$2
ELASTIC_SEARCH_URL=$3
DEXI_URL=$4

# PREPARE ENV
rm -rf venv
rm ingress/github/project/organization_info.json ingress/github/project/output.log
rm ingress/github/code/project_dependency.log
rm data-from-es-*.json
virtualenv venv
source venv/bin/activate

# RUN SCRIPTS
cd ingress/github/project/
pip install -r requirements.txt
python github-data-ingestion.py -env $GITHUB_SYSTEM
cp organization_info.json ../../../egress/search/organization_info.json

cd ../../../egress/search
./reload-search-data.sh $ELASTIC_SEARCH_URL organization_info.json

cd ../../ingress/github/code
pip install -r requirements.txt
python elasticProjectDependency.py -update

cd ../../..
./egress/dexi/push-data.sh $ENV_TO_UPDATE $ELASTIC_SEARCH_URL $DEXI_URL

deactivate
