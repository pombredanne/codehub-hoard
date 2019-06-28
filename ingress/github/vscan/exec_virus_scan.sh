#!/bin/bash

PROJ_HOME_DIR=[*-UPDATE-PROJECT-PATH-HERE-*]

cd "$PROJ_HOME_DIR/ingress/github/vscan"
pip install -r requirements.txt
./exec_virus_scan.py --topic CLONED_DATA_QUEUE --env PUBLIC
