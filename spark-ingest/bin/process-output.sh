#!/usr/bin/env bash

INGEST_HOME=${ingest.home}
INGEST_TOOLS=${ingest.tools.dir}
DATA_DIR=${ingest.data.dir}
SPARK_HOME_DIR="${INGEST_TOOLS}/spark-2.0.1-bin-hadoop2.7"
PROCESS_INPUT_DIR="${DATA_DIR}/process/input"
PROCESS_OUTPUT_DIR="${DATA_DIR}/esearch/input"
UPDATES_INPUT_DIR="${DATA_DIR}/process/input/updates"

echo "$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local --deploy-mode client --executor-memory 3g --name ProcessOutput $INGEST_HOME/spark-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR $UPDATES_INPUT_DIR"
$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.process.ElasticDataOutput --master local --deploy-mode client --executor-memory 3g --name ProcessOutput $INGEST_HOME/spark-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $PROCESS_INPUT_DIR $PROCESS_OUTPUT_DIR $UPDATES_INPUT_DIR
