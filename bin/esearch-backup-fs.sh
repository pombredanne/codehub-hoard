#!/usr/bin/env bash

curl -XPUT http://localhost:9200/_snapshot/stage_backup_repo -d '
{
  "type": "fs",
  "settings": {
                "location": "/mnt/hgfs/dev/data/esbackup",
                "compress": true,
                "max_snapshot_bytes_per_sec": "20mb",
                "max_restore_bytes_per_sec": "20mb"
              }
}';

