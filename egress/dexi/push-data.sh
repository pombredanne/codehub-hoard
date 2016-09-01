#!/bin/bash

#
# The program pulls all the Elastic Search data for the /projects index and pushes
# the data to the Dexi Service.
#
# Parameters: push-data.sh $1 $2 $3
# -----------------------------------
# $1 - The environment to execute against {dev, prod}
# $2 - The IP or Host for Elastic Search.  Assumes you're running on default port 9200
# $3 - The IP or Host for Dexi Service.  Assumes you're running on default port 5009
#
#

ES_URL=http://"$2":9200/projects/_search/?size=10000
DEXI_DEV_PORT=5007
DEXI_PROD_PORT=5009
DEXI_DOMAIN_NAME="$3"
DEXI_PATH=/recommendation-service/api/v1/update_doc_sim
PROD_DATA_FILE=data-from-es-prod.json
DEV_DATA_FILE=data-from-es-dev.json

if [ "$1" = "prod" ]
then

  rm $PROD_DATA_FILE
  echo "Pulling ES data from $ES_URL..."
  curl -get $ES_URL -o "$PROD_DATA_FILE"
  echo "Finished pulling ES data from $ES_URL."

  if [ -f "$PROD_DATA_FILE" ]
  then
    echo "Pushing to $DEXI_URL..."
    curl -v POST http://"$DEXI_DOMAIN_NAME":"$DEXI_PROD_PORT""$DEXI_PATH" -d @$PROD_DATA_FILE --header "Content-Type: application/json"
  else
    echo "$PROD_DATA_FILE Not Found!"
    exit 1
  fi

elif [ "$1" = "dev" ]
then

  rm $DEV_DATA_FILE
  echo "Pulling ES data from $ES_URL..."
  curl -get $ES_URL -o "$DEV_DATA_FILE"
  echo "Finished pulling ES data from $ES_URL."

  if [ -f "$DEV_DATA_FILE" ]
  then
    echo "Pushing to $DEXI_URL""_dev..."
    curl -v POST http://"$DEXI_DOMAIN_NAME":"$DEXI_DEV_PORT""$DEXI_PATH" -d @$DEV_DATA_FILE --header "Content-Type: application/json"
  else
    echo "$DEV_DATA_FILE Not Found!"
    exit 1
  fi

else
  echo "Please provide an ENV, ES IP, and Dexi IP, in that order (ex: push-data.sh dev 3.33.4.44 22.33.22.33)"
  exit 1
fi

exit 0
