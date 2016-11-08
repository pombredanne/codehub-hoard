#!/usr/bin/env bash

set -e

INGEST_TOOLS=${ingest.tools.dir}

echo $INGEST_TOOLS

SPARK_VERSION=spark-2.0.1-bin-hadoop2.7
KAFKA_VERSION=kafka_2.10-0.10.0.1
NIFI_VERSION=nifi-0.7.1
SEARCH_HOME=elasticsearch-2.4.0
#KIBANA_HOME=kibana-4.6.1

#Start all services
echo Starting Spark ...
$INGEST_TOOLS/$SPARK_VERSION/sbin/start-all.sh
sleep 10

echo Starting Nifi ...
$INGEST_TOOLS/$NIFI_VERSION/bin/nifi.sh start
sleep 10

echo Starting Kafka Zookeeper ...
$INGEST_TOOLS/$KAFKA_VERSION/bin/zookeeper-server-start.sh $INGEST_TOOLS/$KAFKA_VERSION/config/zookeeper.properties > /dev/null 2>&1 &
sleep 10

echo Starting Kafka ...
$INGEST_TOOLS/$KAFKA_VERSION/bin/kafka-server-start.sh $INGEST_TOOLS/$KAFKA_VERSION/config/server.properties > /dev/null 2>&1 &

sleep 10

echo Starting Elastic Search ...
$INGEST_TOOLS/$SEARCH_HOME/bin/elasticsearch &

sleep 10
#echo Starting Kibana ...
#$INGEST_TOOLS/$KIBANA_HOME/bin/kibana &

#sleep 10

echo Start-all complete!

