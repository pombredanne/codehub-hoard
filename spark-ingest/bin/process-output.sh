#!/usr/bin/env bash

SPARK_HOME_DIR="~/dev/spark-2.0.0-bin-hadoop2.7"
JOB_DIR="~/dev/spark-ingest"
PROCESS_OUTPUT_DIR="~/dev/data/esearch/input/github"
PROCESS_INPUT_DIR="~/dev/data/process/input/github/"

$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local --deploy-mode client --executor-memory 3g --name ProcessOutput $JOB_DIR/spark-ingest-1.0-SNAPSHOT.jar $JOB_DIR/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR
