#!/usr/bin/env bash

#This script is run before the updated package is deployed in the server. It checks to see
#if any of the ingest scripts are currently running and waits till they are all done.1

PROCESS_NAME_ENDING="ingest.sh"

pids=$(pgrep -f $PROCESS_NAME_ENDING)
while [ "$pids" != "" ]; do
    echo "Waiting for job to finish .."
    sleep 10
    pids=$(pgrep -f $PROCESS_NAME_ENDING)
done

