#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/code
pip install -r requirements.txt
./process_dependency_messages.py --topic CLONED_DEP_DATA_QUEUE
