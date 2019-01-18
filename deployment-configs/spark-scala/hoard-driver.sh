#!/usr/bin/env bash

echo installing and starting up ingestion tools
./install-hoard-dot-task4.sh

echo starting up services
./start-spark-nifi.sh
