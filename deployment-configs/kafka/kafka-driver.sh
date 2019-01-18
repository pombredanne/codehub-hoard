#!/usr/bin/env bash

echo "installing compatible spark compatible kafka with zookeeper"
./install-kafka.sh

echo "starting kafka and zookeeper servers"
./kafka-start.sh

echo "creating kafka topics"
./create-kafka-topics.sh
