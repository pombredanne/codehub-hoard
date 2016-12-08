#!/bin/bash

PROJ_HOME_DIR=${ingest.home}

cd "$PROJ_HOME_DIR/ingress/github/code"
pip install -r requirements.txt
python process_dependency.py
