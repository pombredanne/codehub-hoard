#!/usr/bin/env bash

INGEST_HOME=${ingest.home}
INGEST_TOOLS=${ingest.tools.dir}
DATA_DIR=${ingest.data.dir}

SPARK_HOME_DIR="${INGEST_TOOLS}/spark-2.0.1-bin-hadoop2.7"
INGEST_OUTPUT_DIR="${DATA_DIR}/process/input/code"

echo "$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Sonar --master local --deploy-mode client --executor-memory 3g --name CodeIngest $INGEST_HOME/spark-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $INGEST_OUTPUT_DIR"
$SPARK_HOME_DIR/bin/spark-submit --class com.bah.heimdall.ingestjobs.Sonar --master local --deploy-mode client --executor-memory 3g --name CodeIngest $INGEST_HOME/spark-ingest-1.0-SNAPSHOT.jar $INGEST_HOME/config/application.conf $INGEST_OUTPUT_DIR
