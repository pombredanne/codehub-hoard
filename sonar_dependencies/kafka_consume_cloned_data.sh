#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/sonar
pip install -r requirements.txt
./process_sonar_messages.py --topic CLONED_DATA_QUEUE --install_sonar_runner
