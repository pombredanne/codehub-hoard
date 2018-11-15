#!/usr/bin/env bash

INGEST_HOME=/opt/heimdall
INGEST_TOOLS=/opt/ingest-tools
DATA_DIR=/var/heimdall/data
SPARK_HOME_DIR="${INGEST_TOOLS}/spark-2.0.1-bin-hadoop2.7"
PROCESS_INPUT_DIR="${DATA_DIR}/process/input"
PROCESS_OUTPUT_DIR="${DATA_DIR}/esearch/input"
UPDATES_INPUT_DIR="${DATA_DIR}/process/input/updates"

echo "$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local[2] --deploy-mode client --executor-memory 3g --name ProcessOutput $INGEST_HOME/hoard-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR $UPDATES_INPUT_DIR"
$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local[2] --deploy-mode client --executor-memory 3g --name ProcessOutput $INGEST_HOME/hoard-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR $UPDATES_INPUT_DIR
