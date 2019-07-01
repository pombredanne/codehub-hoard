#!/bin/bash

PROJ_HOME_DIR=[*-UPDATE-PROJECT-PATH-HERE-*]

cd "$PROJ_HOME_DIR/ingress/github/vscan"
pip install -r requirements.txt
./process_virus_scan.py --topic VIRUS_SCAN_QUEUE --env PUBLIC
