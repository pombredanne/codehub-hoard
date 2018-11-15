#!/usr/bin/env bash

#Elastic server to restore the snapshot into
ES_SERVER_URL=${elastic.server.url}
ES_S3_REPO=es_s3_repository
#name of the snapshot to restore from S3 backup. Eg: snapshot_01122017
SNAPSHOT=

#Close index before restoring
curl -XPOST ${ES_SERVER_URL}'/code/_close'
curl -XPOST ${ES_SERVER_URL}'/projects/_close'

#Restoring from backup
curl -XPOST ${ES_SERVER_URL}'/_snapshot/'$ES_S3_REPO'/'$SNAPSHOT'/_restore'

#Open index after restore
curl -XPOST ${ES_SERVER_URL}'/code/_open'
curl -XPOST ${ES_SERVER_URL}'/projects/_open'
