#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/code
pip install -r requirements.txt
./cloned_dep_data.py --env public --topic CLONED_DATA_QUEUE
