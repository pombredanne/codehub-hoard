#!/usr/bin/env bash

KAFKA_HOME=$1

echo creating kafka topics...

KAFKA_ZOOKEEPER_SERVER=${kafka.zookeeper.servers}

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper $KAFKA_ZOOKEEPER_SERVER --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
#--retention.ms=86400000
