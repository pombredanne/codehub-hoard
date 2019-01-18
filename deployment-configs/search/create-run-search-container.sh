#!/bin/bash

# Script cannot be run multiple times since the name is already taken.  You can either remove the container or change
# the name.

docker run -d -p 9200:9200 --name dot-task4-search dot-task4/search:0.1.0 
