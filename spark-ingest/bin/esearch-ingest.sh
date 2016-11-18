#!/usr/bin/env bash

set -e


DATA_DIR=${ingest.data.dir}
DATA_INPUT_DIR="${DATA_DIR}/esearch/input"

#add sorting
for dir in $DATA_INPUT_DIR/*/;
do

  echo $dir

 if [ -d $dir ]; then

  echo "Processing" $dir
  outdirname=${dir/input/output}

  mkdir -p $outdirname

  for file in ${dir}part*; do
    if [[ -f $file ]]; then
        cat ${dir}part* > ${outdirname}elastic_data.json

        curl -s -XPOST localhost:9200/_bulk --data-binary "@$outdirname/elastic_data.json"
        break
    fi
  done
  #cat ${dir}part* > ${outdirname}elastic_data.json
  #delete index now but it will be changed once delta indexing is ready
  #curl -X DELETE 'http://localhost:9200/projects/'
  #curl -s -XPOST localhost:9200/_bulk --data-binary "@$outdirname/elastic_data.json"

  rm -r $dir
 fi

done;
