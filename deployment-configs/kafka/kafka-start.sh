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

KAFKA_VERSION=kafka_2.11-2.1.0
KAFKA_ZOOKEEPER_SERVER=34.201.133.243:2181


#Change user and ownership of the hoard directories to ec2-user. Everything will be run by this user
sudo chown -R $USER:$USER $INGEST_HOME
sudo chown -R $USER:$USER $INSTALL_TOOLS_DIR
sudo chown -R $USER:$USER $DATA_DIR

#Start kafka services
echo Starting Kafka Zookeeper ...
sudo -u $USER $INSTALL_TOOLS_DIR/$KAFKA_VERSION/bin/zookeeper-server-start.sh $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/zookeeper.properties > /dev/null 2>&1 &
sleep 10

echo Starting Kafka Server ...
sudo -u $USER $INSTALL_TOOLS_DIR/$KAFKA_VERSION/bin/kafka-server-start.sh $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/server.properties > /dev/null 2>&1 &

echo kafka is running!!

exit 0
