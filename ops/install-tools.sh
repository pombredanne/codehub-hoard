#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost for user ec2-user
# - Make sure JAVA_HOME is set

INSTALL_TOOLS_DIR=${ingest.tools.dir}
DATA_HOME_DIR=${ingest.data.home.dir}
INGEST_HOME=${ingest.home}

INSTALL_SCRIPTS_DIR=.
TEMP=tmp

SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1
SPARK_WORKSPACE_DIR=${spark.worker.dir}
NIFI_WEB_PORT=${nifi.webapp.port}
KAFKA_ZOOKEEPER_SERVER=${kafka.zookeeper.servers}

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

if [ ! -d $DATA_HOME_DIR ]; then
 mkdir -p $DATA_HOME_DIR
fi

if [ ! -d $TEMP ]; then
 mkdir -p $TEMP
fi

if [ ! -d /tmp/spark-events ]; then
 mkdir -p /tmp/spark-events
fi

#Get and install spark in local mode
echo http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz
wget -P $TEMP/ http://d3kbcqa49mib13.cloudfront.net/${SPARK_VERSION}.tgz
tar zxvf $TEMP/$SPARK_VERSION.tgz -C $INSTALL_TOOLS_DIR/

#setup spark config
cp $INSTALL_SCRIPTS_DIR/spark-env.sh $INSTALL_TOOLS_DIR/$SPARK_VERSION/conf/spark-env.sh

#Get and install Kafka
echo http://apache.claz.org/kafka/0.10.0.1/${KAFKA_VERSION}.tgz
wget -P $TEMP/ http://apache.claz.org/kafka/0.10.0.1/${KAFKA_VERSION}.tgz
tar zxvf $TEMP/$KAFKA_VERSION.tgz -C $INSTALL_TOOLS_DIR/
#change kafka message retention for 1 day
sed -i 's/log.retention.hours=168/log.retention.hours=24/' $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/server.properties

#Get and install Nifi
echo https://archive.apache.org/dist/nifi/0.7.1/${NIFI_VERSION}-bin.tar.gz
wget -P $TEMP/ https://archive.apache.org/dist/nifi/0.7.1/${NIFI_VERSION}-bin.tar.gz
tar zxvf $TEMP/${NIFI_VERSION}-bin.tar.gz -C $INSTALL_TOOLS_DIR/

#change nifi default port for the webapp from 8080(which conflicts with spark port) to 8088
sed -i 's/nifi.web.http.port=8080/nifi.web.http.port='$NIFI_WEB_PORT'/' $INSTALL_TOOLS_DIR/$NIFI_VERSION/conf/nifi.properties

rm -r tmp

#Change user and ownership of the hoard directories to ec2-user. Everything will be run by this user
sudo chown -R ec2-user:ec2-user $INGEST_HOME
sudo chown -R ec2-user:ec2-user $INSTALL_TOOLS_DIR
sudo chown -R ec2-user:ec2-user $DATA_HOME_DIR
sudo chown -R ec2-user:ec2-user /tmp/spark-events

#Start all services
echo Starting Spark ...
sudo -u ec2-user $INSTALL_TOOLS_DIR/$SPARK_VERSION/sbin/start-all.sh
sleep 10

echo Starting Nifi ...
sudo -u ec2-user $INSTALL_TOOLS_DIR/$NIFI_VERSION/bin/nifi.sh start
sleep 10

echo Starting Kafka Zookeeper ...
sudo -u ec2-user $INSTALL_TOOLS_DIR/$KAFKA_VERSION/bin/zookeeper-server-start.sh $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/zookeeper.properties > /dev/null 2>&1 &
sleep 10

echo Starting Kafka Server ...
sudo -u ec2-user $INSTALL_TOOLS_DIR/$KAFKA_VERSION/bin/kafka-server-start.sh $INSTALL_TOOLS_DIR/$KAFKA_VERSION/config/server.properties > /dev/null 2>&1 &

echo Tools setup complete!