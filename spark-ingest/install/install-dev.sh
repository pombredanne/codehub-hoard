#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost

ENV=dev
INSTALL_SCRIPTS_DIR=.
TEMP=tmp
INSTALL_DIR=~/stage/consolidation/ingest-tools
SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
SPARK_ENV_CONFIG=~/stage/consolidation/heimdall-hoard/spark-ingest/install
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1
NIFI_WEB_PORT=8088

if [ ! -d $INSTALL_DIR ]; then
 mkdir $INSTALL_DIR
fi

#Get and install spark in local mode
echo http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz

wget -P $TEMP/ http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz
tar zxvf $TEMP/$SPARK_VERSION.tgz -C $INSTALL_DIR/

#setup spark config
cp $SPARK_ENV_CONFIG/spark-env-${ENV}.sh $INSTALL_DIR/$SPARK_VERSION/conf/spark-env.sh

#Get and install Kafka
wget -P $TEMP/ http://apache.claz.org/kafka/0.10.0.1/${KAFKA_VERSION}.tgz
tar zxvf $TEMP/$KAFKA_VERSION.tgz -C $INSTALL_DIR/

#Get and install Elastic

#Get and install Nifi
wget -P $TEMP/ https://archive.apache.org/dist/nifi/0.7.1/${NIFI_VERSION}-bin.tar.gz
tar zxvf $TEMP/${NIFI_VERSION}-bin.tar.gz -C $INSTALL_DIR/

#change nifi default port for the webapp from 8080(which conflicts with spark port) to 8088
sed -i -e 's/nifi.web.http.port=8080/nifi.web.http.port=8088/' $INSTALL_DIR/$NIFI_VERSION/conf/nifi.properties

rm -r tmp

echo setup complete!
