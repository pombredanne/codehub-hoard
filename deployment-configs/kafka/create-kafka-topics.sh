#!/usr/bin/env bash


INSTALL_TOOLS_DIR=/opt/dot-task4/ingest-tools
KAFKA_VERSION=kafka_2.11-2.1.0
KAFKA_ZOOKEEPER_SERVER=34.201.133.243:2181

KAFKA_HOME=$INSTALL_TOOLS_DIR/$KAFKA_VERSION

#KAFKA_ZOOKEEPER_SERVER=${kafka.zookeeper.servers}

echo creating kafka topics...

#$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --topic INGEST_QUEUE
#$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --topic CLONED_DATA_QUEUE
#$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --topic SONAR_DATA_QUEUE
#$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --topic DEPENDENCY_DATA_QUEUE
#$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --topic CLONED_DEP_DATA_QUEUE



$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic INGEST_QUEUE
sleep 5
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic CLONED_DATA_QUEUE
sleep 5

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic SONAR_DATA_QUEUE
sleep 5

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic DEPENDENCY_DATA_QUEUE
sleep 5

$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper ${KAFKA_ZOOKEEPER_SERVER} --replication-factor 1 --partitions 1 --topic CLONED_DEP_DATA_QUEUE
sleep 5
