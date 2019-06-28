#!/bin/bash
PROJ_HOME_DIR=[*-UPDATE-PROJECT-PATH-*]
cd "$PROJ_HOME_DIR/ingress/github/vscan"
pip install -r requirements.txt
./mock_repo_cloned.py --env public --topic CLONED_DATA_QUEUE
