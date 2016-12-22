#!/usr/bin/env bash

INGEST_TOOLS=${ingest.tools.dir}

echo Starting Nifi ...
$INGEST_TOOLS/nifi-*/bin/nifi.sh start
