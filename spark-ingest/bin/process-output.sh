#!/usr/bin/env bash

SPARK_HOME_DIR="/home/ec2-user/dev/spark-2.0.0-bin-hadoop2.7"
JOB_DIR="/home/ec2-user/dev/spark-ingest"
PROCESS_OUTPUT_DIR="/home/ec2-user/dev/data/process/output/github"


$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local --deploy-mode client --executor-memory 3g --name ProcessOutput $JOB_DIR/spark-ingest-1.0-SNAPSHOT.jar $JOB_DIR/conf/application.conf /home/ec2-user/dev/data/process/input/github/ $PROCESS_OUTPUT_DIR
