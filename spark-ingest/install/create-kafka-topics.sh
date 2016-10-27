#!/usr/bin/env bash

KAFKA_HOME=$1

echo $INSTALL_DIR/$KAFKA_VERSION

echo creating kafka topics...

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
