#!/usr/bin/env bash

CURR_DATE_TIME="`date +%Y%m%d%H%M%S`";

ES_SERVER_URL=${elastic.server.url}

curl -XPUT $ES_SERVER_URL'/_snapshot/es_s3_repository/stage_snapshot_'$CURR_DATE_TIME
