#!/usr/bin/env bash

KAFKA_HOME=$1

echo creating kafka topics...

$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic INGEST_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic INGEST_QUEUE2
$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic INGEST_QUEUE3

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic INGEST_QUEUE2
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic INGEST_QUEUE3
