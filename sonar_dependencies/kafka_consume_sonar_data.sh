#!/bin/bash

PROJ_HOME_DIR=${ingest.home}

cd "$PROJ_HOME_DIR/ingress/github/sonar"
pip install -r requirements.txt
./kafkaSonarEsUpdate.py --topic SONAR_DATA_QUEUE
