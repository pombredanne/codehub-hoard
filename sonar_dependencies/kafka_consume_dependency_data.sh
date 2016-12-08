#!/bin/bash

PROJ_HOME_DIR=${ingest}

cd "$PROJ_HOME_DIR/ingress/github/code"
pip install -r requirements.txt
./kafkaDependencyEsUpdate.py --topic DEPENDENCY_DATA_QUEUE
