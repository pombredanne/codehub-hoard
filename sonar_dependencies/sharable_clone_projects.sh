#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/sonar
pip install -r requirements.txt
./clone_repos.py --env public --topic CLONED_DATA_QUEUE
