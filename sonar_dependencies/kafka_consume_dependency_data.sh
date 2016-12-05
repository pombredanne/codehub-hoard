#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/code
pip install -r requirements.txt
./kafkaDependencyEsUpdate.py --topic DEPENDENCY_DATA_QUEUE
