#!/usr/bin/env bash

echo building mongoDB image
./create-mongo-docker-image.sh

echo starting up mongoDB container
./create-run-mongodb-container.sh
