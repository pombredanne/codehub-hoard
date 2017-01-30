#!/bin/bash

#
# The program pulls all the Elastic Search data for the projects/code indices and pushes
# the data to the Kindred Service.
#
#
CURR_DATE_TIME="`date +%Y%m%d%H%M%S`";

DATA_DIR=${ingest.data.dir}/esearch/kindred/${CURR_DATE_TIME}

mkdir -p $DATA_DIR

PROJECTS_ES_URL=http://${elastic.server.url}/projects/_search/?size=10000
CODE_ES_URL=http://${elastic.server.url}/code/_search/?size=10000

KINDRED_PORT=${kindred.port}
KINDRED_DOMAIN_NAME=${kindred.domain.name}
KINDRED_PATH=/recommendation-service/api/v1/update_doc_sim
PROJECT_DATA_FILE="$DATA_DIR/data-from-es-project.json"
CODE_DATA_FILE="$DATA_DIR/data-from-es-code.json"

#rm $PROJECT_DATA_FILE
#rm $CODE_DATA_FILE

echo "Pulling ES data from $PROJECTS_ES_URL..."
curl -get $PROJECTS_ES_URL -o "$PROJECT_DATA_FILE"
echo "Pulling ES data from $CODE_ES_URL..."
curl -get $CODE_ES_URL -o "$CODE_DATA_FILE"


if [ -f "$PROJECT_DATA_FILE" ]
then
    echo "Pushing Projects data to $KINDRED_URL..."
    curl -v POST http://"$KINDRED_DOMAIN_NAME":"$KINDRED_PROD_PORT""$KINDRED_PATH" -d @$PROJECT_DATA_FILE --header "Content-Type: application/json"
else
    echo "$PROJECT_DATA_FILE Not Found!"
    exit 1
fi

#Note: Kindred is not accepting code data yet
#if [ -f "$CODE_DATA_FILE" ]
#then
#    echo "Pushing Code data to $KINDRED_URL..."
#    curl -v POST http://"$KINDRED_DOMAIN_NAME":"$KINDRED_PROD_PORT""$KINDRED_PATH" -d @$CODE_DATA_FILE --header "Content-Type: application/json"
#else
#    echo "$CODE_DATA_FILE Not Found!"
#    exit 1
#fi

exit 0
