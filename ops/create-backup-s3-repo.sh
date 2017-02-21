#!/usr/bin/env bash

ES_SERVER_URL=${elastic.server.url}
ES_S3_REPO=es_s3_repository_${ingest.env}

echo 'Creating S3 repository for backup..'
curl -XPUT ${ES_SERVER_URL}/_snapshot/${ES_S3_REPO} -d '
{
  "type": "s3",
  "settings": {
                "bucket": "${ingest.env}-heimdall-bucket",
                "base_path": "/stage-es-backup",
                "region": "us-east-1",
                "access_key": "",
                "secret_key": "",
                "max_retries": "2"
              }
}';
