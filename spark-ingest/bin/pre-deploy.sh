#!/usr/bin/env bash

INGEST_TOOLS=${ingest.tools.dir}
INGEST_HOME=${ingest.home}

#Save old config file settings before deploying. This will be removed once we
#have a mechanism to encrypt the github token in config files
cp $INGEST_HOME/config/application.conf $INGEST_HOME/config/application_orig.conf


echo Stopping Nifi ...
$INGEST_TOOLS/nifi-*/bin/nifi.sh stop

sleep 60

gzip $INGEST_HOME/config/StageNifiConfiguration.xml

cp $INGEST_HOME/config/StageNifiConfiguration.xml $INGEST_HOME/config/flow.xml.gz

mv $INGEST_HOME/config/flow.xml.gz $INGEST_TOOLS/nifi-*/config/

sleep 10

echo Starting Nifi ...
$INGEST_TOOLS/nifi-*/bin/nifi.sh start
