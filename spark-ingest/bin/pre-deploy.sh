#!/usr/bin/env bash

INGEST_TOOLS=${ingest.tools.dir}
INGEST_HOME=${ingest.home}

echo Stopping Nifi ...
$INGEST_TOOLS/nifi-*/bin/nifi.sh stop

sleep 60

gzip $INGEST_HOME/config/StageNfiDataflow.xml

cp $INGEST_HOME/config/StageNfiDataflow.xml $INGEST_HOME/config/flow.xml.gz

mv $INGEST_HOME/config/flow.xml.gz $INGEST_TOOLS/nifi-*/config/

sleep 10

echo Starting Nifi ...
$INGEST_TOOLS/nifi-*/bin/nifi.sh start
