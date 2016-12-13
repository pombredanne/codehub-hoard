#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost foe user ec2-user
# - Make sure JAVA_HOME is set

INSTALL_TOOLS_DIR=${ingest.tools.dir}
DATA_DIR=${ingest.data.home.dir}
INGEST_HOME=${ingest.home}

ENV=dev
INSTALL_SCRIPTS_DIR=.
TEMP=tmp

SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1
SPARK_WORKSPACE_DIR=${spark.worker.dir}
NIFI_WEB_PORT=8088
#ELASTIC_VERSION=elasticsearch-2.4.0
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

if [ ! -d $DATA_DIR ]; then
 mkdir -p $DATA_DIR
fi

if [ ! -d $TEMP ]; then
 mkdir -p $TEMP
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

#Get and install Nifi
echo https://archive.apache.org/dist/nifi/0.7.1/${NIFI_VERSION}-bin.tar.gz
wget -P $TEMP/ https://archive.apache.org/dist/nifi/0.7.1/${NIFI_VERSION}-bin.tar.gz
tar zxvf $TEMP/${NIFI_VERSION}-bin.tar.gz -C $INSTALL_TOOLS_DIR/

#change nifi default port for the webapp from 8080(which conflicts with spark port) to 8088
sed -i 's/nifi.web.http.port=8080/nifi.web.http.port=8088/' $INSTALL_TOOLS_DIR/$NIFI_VERSION/conf/nifi.properties

#Get and install Elastic
#wget -P $TEMP/ https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.4.0/elasticsearch-2.4.0.tar.gz
#tar zxvf $TEMP/${ELASTIC_VERSION}.tar.gz -C $INSTALL_TOOLS_DIR/

rm -r tmp

#Change user and ownership of the hoard directories to ec2-user. Everything will be run by this user
cd /opt
sudo chown -R ec2-user:ec2-user heimdall
sudo chown -R ec2-user:ec2-user ingest-tools
cd /var
sudo chown -R ec2-user:ec2-user heimdall

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

sleep 20

#echo Starting Elastic Search Server ...
#$INSTALL_TOOLS_DIR/$ELASTIC_VERSION/bin/elasticsearch &

echo creating kafka topics...

$INSTALL_TOOLS_DIR/$KAFKA_VERSION/bin/kafka-topics.sh --create --zookeeper $KAFKA_ZOOKEEPER_SERVER --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
#--retention.ms=86400000


echo setup complete!