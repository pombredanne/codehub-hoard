#!/usr/bin/env bash

set -e

# The following prerequisites should be performed on the target server before installing dot-task4-hoard
# - Setup passwordless ssh to localhost for the user
# - Make sure JAVA installed and JAVA_HOME is set
#
# usage: sudo ./dot-task4-hoard.sh
#
# If you encounter error while installing, remove following folders, fix the error and start again
# INSTALL_TOOLS_DIR, DATA_DIR, INGEST_HOME
#

INSTALL_TOOLS_DIR=/opt/dot-task4/ingest-tools
DATA_DIR=/var/dot-task4
INGEST_HOME=/opt/dot-task4

INSTALL_SCRIPTS_DIR=.
TEMP=tmp

#KAFKA_VERSION=kafka_2.10-0.10.0.1
KAFKA_VERSION=kafka_2.11-2.1.0
KAFKA_ZOOKEEPER_SERVER=10.194.22.71:2181

#Create required directories
if [ ! -d $INGEST_HOME ]; then
 mkdir -p $INGEST_HOME
fi

if [ ! -d $INSTALL_TOOLS_DIR ]; then
 mkdir -p $INSTALL_TOOLS_DIR
fi

if [ ! -d $SPARK_WORKSPACE_DIR ]; then
 mkdir -p $SPARK_WORKSPACE_DIR
fi

if [ ! -d $DATA_DIR ]; then
 mkdir -p $DATA_DIR
fi

if [ ! -d $TEMP ]; then
 mkdir -p $TEMP
fi


# #Get and install Kafka
#kafka_2.10-0.10.0.1.tgz
echo https://www-eu.apache.org/dist/kafka/2.1.0/${KAFKA_VERSION}.tgz
wget -P $TEMP/ https://www-eu.apache.org/dist/kafka/2.1.0/${KAFKA_VERSION}.tgz
tar zxvf $TEMP/$KAFKA_VERSION.tgz -C $INSTALL_TOOLS_DIR/

#change kafka message retention for 1 day
sed -i 's/log.retention.hours=168/log.retention.hours=24/' $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/server.properties
rm -r tmp

exit 0
