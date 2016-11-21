#!/bin/bash
cd ~/stage/expt_spark/heimdall-hoard/ingress/github/code
pip install -r requirements.txt
python process_dependency.py
