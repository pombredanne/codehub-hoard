#!/usr/bin/env bash

INGEST_HOME=/opt/heimdall
INGEST_TOOLS=/opt/ingest-tools
DATA_DIR=/var/heimdall/data

SPARK_HOME_DIR="${INGEST_TOOLS}/spark-2.0.1-bin-hadoop2.7"
INGEST_OUTPUT_DIR="${DATA_DIR}/process/input/project"

echo "$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Github --master local[4] --deploy-mode client --executor-memory 3g --name ProjectsIngest $INGEST_HOME/hoard-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $INGEST_OUTPUT_DIR"
$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Github --master local[4] --deploy-mode client --executor-memory 2g  --name ProjectsIngest $INGEST_HOME/hoard-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $INGEST_OUTPUT_DIR
