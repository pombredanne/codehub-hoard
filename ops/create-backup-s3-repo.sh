#!/usr/bin/env bash

ES_SERVER_URL=${elastic.server.url}

echo 'Creating S3 repository for backup..'
curl -XPUT ${ES_SERVER_URL}/_snapshot/es_s3_repository -d '
{
  "type": "s3",
  "settings": {
                "bucket": "test-heimdall-bucket",
                "base_path": "/stage-es-backup",
                "region": "us-east-1",
                "access_key": "",
                "secret_key": "",
                "max_retries": "2"
              }
}';
