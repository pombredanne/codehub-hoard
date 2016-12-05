#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/code
pip install -r requirements.txt
python process_es_dependency_update.py
