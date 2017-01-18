#!/usr/bin/env bash

set -e

./install-tools.sh
sleep 10
./create-backup-s3-repo.sh
sleep 10
#./create-kafka-topics.sh

echo "Hoard tools installation complete."