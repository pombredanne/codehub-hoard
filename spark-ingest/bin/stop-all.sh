#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost

INSTALL_DIR=~/ingest-tools
SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1

echo Stopping Spark ...
$INSTALL_DIR/$SPARK_VERSION/sbin/stop-all.sh
sleep 10

echo Stopping Nifi ...
$INSTALL_DIR/$NIFI_VERSION/bin/nifi.sh stop
sleep 10

echo Stopping Kafka ...
$INSTALL_DIR/$KAFKA_VERSION/bin/kafka-server-stop.sh

echo Stopping Kafka Zookeeper ...
$INSTALL_DIR/$KAFKA_VERSION/bin/zookeeper-server-stop.sh
sleep 10

echo Stop-all completed!

