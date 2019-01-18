#!/bin/bash

DATA_DIR=/var/dot-task4/mongo-data
if [ ! -d $DATA_DIR ]; then
 mkdir -p $DATA_DIR
fi

# Script cannot be run multiple times since the name is already taken.  You can either remove the container or change
# the name.
docker run -d -p 27018:27017 --name dot-task4-mongo dot-task4/mongo:0.1.0 -v $DATA_DIR:/data/db
