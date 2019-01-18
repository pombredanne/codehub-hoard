#!/usr/bin/env bash

echo building elasticsearch image
./create-search-docker-image.sh

echo starting elasticsearch container
./create-run-search-container.sh

echo creating indices settings and mapping
./create-search-index.sh
