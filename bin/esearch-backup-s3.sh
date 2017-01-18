#!/usr/bin/env bash

CURR_DATE_TIME="`date +%Y%m%d%H%M%S`";

curl -XPUT 'http://localhost:9200/_snapshot/es_s3_repository/stage_snapshot_'$CURR_DATE_TIME
