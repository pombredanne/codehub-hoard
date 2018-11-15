#!/usr/bin/env bash

INGEST_TOOLS=/opt/ingest-tools

echo Starting Nifi ...
#$INGEST_TOOLS/nifi-*/bin/nifi.sh start
sudo -u ec2-user $INGEST_TOOLS/nifi-*/bin/nifi.sh start > /dev/null 2>&1 &

sleep 10

exit 0
