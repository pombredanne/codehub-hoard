#!/bin/bash

PROJ_HOME_DIR=${ingest}

cd "$PROJ_HOME_DIR/ingress/github/code"
pip install -r requirements.txt
./process_dependency_messages.py --topic CLONED_DEP_DATA_QUEUE
