#!/usr/bin/env bash

#Elastic server to restore the snapshot into
ES_SERVER_URL=${elastic.server.url}
#name of the snapshot to restore
SNAPSHOT=

#Close index before restoring
curl -XPOST ${ES_SERVER_URL}'/code/_close'
curl -XPOST ${ES_SERVER_URL}'/projects/_close'

#Restoring from backup
curl -XPOST ${ES_SERVER_URL}'/_snapshot/es_s3_repository/'$SNAPSHOT'/_restore'

#Open index after restore
curl -XPOST ${ES_SERVER_URL}'/code/_open'
curl -XPOST ${ES_SERVER_URL}'/projects/_open'



~
~
