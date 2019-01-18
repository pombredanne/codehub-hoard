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

if [ ! -d /tmp/spark-events ]; then
 mkdir -p /tmp/spark-events
fi

#Get and install spark in  standalone mode
echo http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz
wget -P $TEMP/ http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz
tar zxvf $TEMP/$SPARK_VERSION.tgz -C $INSTALL_TOOLS_DIR/

#setup spark config
cp $INSTALL_SCRIPTS_DIR/spark-env.sh $INSTALL_TOOLS_DIR/$SPARK_VERSION/conf/spark-env.sh

#Get and install Nifi
echo https://archive.apache.org/dist/nifi/1.7.1/${NIFI_VERSION}-bin.tar.gz
wget -P $TEMP/ https://archive.apache.org/dist/nifi/1.7.1/${NIFI_VERSION}-bin.zip
unzip $TEMP/${NIFI_VERSION}-bin.zip -d $INSTALL_TOOLS_DIR/

#change nifi default port for the webapp from 8080(which conflicts with spark port) to 8086
gsed -i 's/nifi.web.http.port=8086/nifi.web.http.port='$NIFI_WEB_PORT'/' $INSTALL_TOOLS_DIR/$NIFI_VERSION/conf/nifi.properties
rm -r tmp

exit 0
