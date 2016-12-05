#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/sonar
pip install -r requirements.txt
./kafkaSonarEsUpdate.py --topic SONAR_DATA_QUEUE
