#!/usr/bin/env bash

DATA_INPUT_DIR="/home/ec2-user/dev/data/esearch/input/github"

curl -s -XPOST localhost:9200/_bulk --data-binary "@$DATA_INPUT_DIR/part-00000"