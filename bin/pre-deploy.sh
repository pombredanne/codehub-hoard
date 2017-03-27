#!/usr/bin/env bash

INGEST_TOOLS=${ingest.tools.dir}
INGEST_HOME=${ingest.home}
DATA_HOME=${ingest.data.home.dir}

#Save old config file settings before deploying. This will be removed once we
#have a mechanism to encrypt the github token in config files
cp $INGEST_HOME/config/application.conf $DATA_HOME/config/application_orig.conf
cp $INGEST_HOME/ingress/github/code/ingest.conf $DATA_HOME/ingress/github/code/ingest_orig.conf


#Experimental for now
#gzip $INGEST_HOME/config/StageNifiConfiguration.xml
#cp $INGEST_HOME/config/StageNifiConfiguration.xml $INGEST_HOME/config/flow.xml.gz
#mv $INGEST_HOME/config/flow.xml.gz $INGEST_TOOLS/nifi-*/config/

#sleep 10

exit 0