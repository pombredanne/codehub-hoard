#!/bin/bash

PROJ_HOME_DIR=/opt/heimdall

cd "$PROJ_HOME_DIR/ingress/github/sonar"
pip install -r requirements.txt
./clone_repos.py --topic CLONED_DATA_QUEUE --env PUBLIC
