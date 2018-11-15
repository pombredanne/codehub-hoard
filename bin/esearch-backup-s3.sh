#!/usr/bin/env bash

CURR_DATE_TIME="`date +%Y%m%d%H%M%S`";

ES_SERVER_URL=${elastic.server.url}
ES_S3_REPO=es_s3_repository

curl -XPUT $ES_SERVER_URL'/_snapshot/'$ES_S3_REPO'/stage_snapshot_'$CURR_DATE_TIME
