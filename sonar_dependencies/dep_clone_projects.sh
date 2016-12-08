#!/bin/bash
PROJ_HOME_DIR=${ingest.home}
cd "$PROJ_HOME_DIR/ingress/github/code"
pip install -r requirements.txt
./cloned_dep_data.py --env public --topic CLONED_DATA_QUEUE
