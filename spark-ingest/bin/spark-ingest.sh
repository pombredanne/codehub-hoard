#!/usr/bin/env bash

SPARK_HOME_DIR="~/ingest-tools/spark-2.0.0-bin-hadoop2.7"
JOB_DIR="~/dev/spark-ingest"
INGEST_OUTPUT_DIR="~/dev/data/process/input/github"


$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Github --master local --deploy-mode client --executor-memory 3g --name ProjectsIngest $JOB_DIR/spark-ingest-1.0-SNAPSHOT.jar $JOB_DIR/config/application.conf $INGEST_OUTPUT_DIR
