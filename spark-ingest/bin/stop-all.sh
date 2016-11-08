#!/usr/bin/env bash

set -e

#Prerequisites:
# - Setup passwordless ssh to localhost

INGEST_TOOLS=${ingest.tools.dir}
SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1

echo Stopping Spark ...
$INGEST_TOOLS/$SPARK_VERSION/sbin/stop-all.sh
sleep 10

echo Stopping Nifi ...
$INGEST_TOOLS/$NIFI_VERSION/bin/nifi.sh stop
sleep 10

echo Stopping Kafka ...
$INGEST_TOOLS/$KAFKA_VERSION/bin/kafka-server-stop.sh

echo Stopping Kafka Zookeeper ...
$INGEST_TOOLS/$KAFKA_VERSION/bin/zookeeper-server-stop.sh
sleep 10

echo Stop-all completed!

