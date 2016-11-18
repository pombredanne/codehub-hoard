#!/bin/bash
cd ~/stage/consolidation/heimdall-hoard/ingress/github/sonar
pip install -r requirements.txt
python clone_repos.py
