#!/usr/bin/env bash

DATA_INPUT_DIR="/home/ec2-user/dev/data/esearch/input/github"

#add sorting
for dir in $DATA_INPUT_DIR/*/;
do

  echo $dir

 if [ -d $dir ]; then

  echo "Processing" $dir
  outdirname=${dir/input/output}

  mkdir -p $outdirname

  cat ${dir}part* > ${outdirname}github_elastic_data.json

  #delete index now but it will be changed once delta indexing is ready
  #curl -X DELETE 'http://localhost:9200/projects/'

  curl -s -XPOST localhost:9200/_bulk --data-binary "@$outdirname/github_elastic_data.json"

  rm -r $dir
 fi

done;
