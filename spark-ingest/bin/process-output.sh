#!/usr/bin/env bash

SPARK_HOME_DIR=~/stage/expt_spark/ingest-tools/spark-2.0.1-bin-hadoop2.7
JOB_DIR=~/stage/expt_spark/JOB_DIR
PROCESS_OUTPUT_DIR=~/stage/expt_spark/dev/data/esearch/input/github
PROCESS_INPUT_DIR=~/stage/expt_spark/dev/data/process/input/github

$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local --deploy-mode client --executor-memory 3g --name ProcessOutput $JOB_DIR/spark-ingest-1.0-SNAPSHOT.jar $JOB_DIR/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR
