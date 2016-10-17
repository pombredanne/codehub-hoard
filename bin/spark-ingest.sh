#!/usr/bin/env bash

SPARK_HOME_DIR="/home/ec2-user/dev/spark-2.0.0-bin-hadoop2.7"
JOB_DIR="/home/ec2-user/dev/spark-ingest"

INGEST_OUTPUT_DIR="/home/ec2-user/dev/data/process/input/github"


$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Github --master local --deploy-mode client --executor-memory 3g --name ProjectsIngest $JOB_DIR/spark-ingest-1.0-SNAPSHOT.jar $JOB_DIR/conf/application.conf $INGEST_OUTPUT_DIR