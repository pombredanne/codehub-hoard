#!/usr/bin/env bash

KAFKA_HOME=$1

echo creating kafka topics...

$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic INGEST_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic CLONED_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic SONAR_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic DEPENDENCY_DATA_QUEUE



$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic CLONED_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic SONAR_DATA_QUEUE
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic DEPENDENCY_DATA_QUEUE
