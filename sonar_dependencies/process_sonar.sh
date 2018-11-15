#!/bin/bash

PROJ_HOME_DIR=/opt/heimdall

cd "$PROJ_HOME_DIR/ingress/github/sonar"
pip install -r requirements.txt
python process_sonar.py --install_sonar_runner
