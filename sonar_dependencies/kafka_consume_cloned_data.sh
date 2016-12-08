#!/bin/bash

PROJ_HOME_DIR=${ingest.home}
cd "$PROJ_HOME_DIR/ingress/github/sonar"
pip install -r requirements.txt
./process_sonar_messages.py --topic CLONED_DATA_QUEUE --install_sonar_runner
