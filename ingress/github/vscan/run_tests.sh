#!/bin/bash

#
# Execute all the python tests with pattern *_test.py
#
pip install -r test_requirements.txt
pwd
python -m unittest discover '.' '*_test.py'
