#!/usr/bin/env bash

KAFKA_HOME=$1

KAFKA_ZOOKEEPER_SERVER=${kafka.zookeeper.servers}

echo creating kafka topics...

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic CLONED_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic SONAR_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic DEPENDENCY_DATA_QUEUE
