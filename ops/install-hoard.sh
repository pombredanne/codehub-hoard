#!/usr/bin/env bash

set -e
# The following prerequisites should be performed on the target server before installing heimdall-hoard
# - Setup passwordless ssh to localhost for user ec2-user
# - Make sure JAVA installed and JAVA_HOME is set
# - add https://github.boozallencsn.com/ site's cert to trusted certs on target server
#
# usage: sudo ./install-hoard.sh
#
# If you encounter error while installing, remove following folders, fix the error and start again
# INSTALL_TOOLS_DIR, DATA_HOME_DIR, INGEST_HOME
#

./install-tools.sh
sleep 10
./create-backup-s3-repo.sh

echo "Hoard tools installation complete."