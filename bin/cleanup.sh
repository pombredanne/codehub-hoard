#!/usr/bin/env bash


INGEST_HOME=/opt/heimdall
INGEST_TOOLS=/opt/ingest-tools
DATA_DIR=/var/heimdall/data


#Restore old config file settings after deploying. This will be removed once we
#have a mechanism to encrypt the github tokens in config files
if [[ -f $DATA_HOME_DIR/config/application_orig.conf ]]; then
    cp $DATA_HOME_DIR/config/application_orig.conf $INGEST_HOME/config/application.conf
fi
if [[ -f $DATA_HOME_DIR/config/ingest_orig.conf ]]; then
    cp $DATA_HOME_DIR/config/ingest_orig.conf $INGEST_HOME/ingress/github/config/ingest.conf
fi

#AWS deploys the apps as root, need to change the ownership to ec2-user after deploying
cd $INGEST_HOME
cd ../
sudo chown -R ec2-user:ec2-user heimdall

#Start creating the data directory structure
if [ ! -d $DATA_DIR ]; then
    mkdir -p $DATA_DIR
    mkdir -p $DATA_HOME_DIR/config
    mkdir -p $DATA_HOME_DIR/logs

    SEARCH_DATA_DIR="${DATA_DIR}/esearch/"
    PROCESS_DATA_DIR="${DATA_DIR}/process/"

    rm -r "$SEARCH_DATA_DIR"
    rm -r "$PROCESS_DATA_DIR"

    mkdir -p "$SEARCH_DATA_DIR/input"
    mkdir -p "$PROCESS_DATA_DIR/input"

    mkdir -p "$SEARCH_DATA_DIR/output"
    mkdir -p "$SEARCH_DATA_DIR/kindred"
    mkdir -p "$PROCESS_DATA_DIR/output"

    chmod -R 777 "$SEARCH_DATA_DIR"
    chmod -R 777 "$PROCESS_DATA_DIR"
fi

exit 0
