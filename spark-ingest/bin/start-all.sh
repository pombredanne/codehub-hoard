#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost

INSTALL_DIR=~/ingest-tools
SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1

#Start all services
echo Starting Spark ...
INSTALL_DIR/$SPARK_VERSION/sbin/start-all.sh
sleep 10

echo Starting Nifi ...
$INSTALL_DIR/$NIFI_VERSION/bin/nifi.sh start
sleep 10

echo Starting Kafka Zookeeper ...
$INSTALL_DIR/$KAFKA_VERSION/bin/zookeeper-server-start.sh $INSTALL_DIR/$KAFKA_VERSION/config/zookeeper.properties > /dev/null 2>&1 &
sleep 10

echo Starting Kafka ...
$INSTALL_DIR/$KAFKA_VERSION/bin/kafka-server-start.sh $INSTALL_DIR/$KAFKA_VERSION/config/server.properties > /dev/null 2>&1 &

echo start-all complete!

