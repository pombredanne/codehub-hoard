#!/bin/bash 
cd ~/stage/expt_spark/heimdall-hoard/ingress/github/sonar
pip install -r requirements.txt
python process_sonar.py --install_sonar_runner
