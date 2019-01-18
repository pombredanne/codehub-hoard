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

SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
NIFI_VERSION=nifi-1.7.1
SPARK_WORKSPACE_DIR=/opt/dot-task4/workspace/
NIFI_WEB_PORT=8086


#Change user and ownership of the hoard directories to ec2-user. Everything will be run by this user
sudo chown -R $USER:$USER $INGEST_HOME
sudo chown -R $USER:$USER $INSTALL_TOOLS_DIR
sudo chown -R $USER:$USER $DATA_DIR
sudo chown -R $USER:$USER /tmp/spark-events

#Start all services
echo Starting Spark ...
sudo -u $USER $INSTALL_TOOLS_DIR/$SPARK_VERSION/sbin/stop-all.sh
sleep 10
sudo -u $USER $INSTALL_TOOLS_DIR/$SPARK_VERSION/sbin/start-all.sh
sleep 10

echo Starting Nifi ...
sudo -u $USER $INSTALL_TOOLS_DIR/$NIFI_VERSION/bin/nifi.sh start
sleep 10
exit 0
