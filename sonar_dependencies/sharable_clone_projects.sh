#!/bin/bash

PROJ_HOME_DIR=${ingest.home}

cd "$PROJ_HOME_DIR/ingress/github/sonar"
pip install -r requirements.txt
./clone_repos.py --env public --topic CLONED_DATA_QUEUE
