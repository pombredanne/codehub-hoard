#!/usr/bin/env bash

# Install and configure CLAMAV
# ----------------------------
# This script is intended to run on a Amazon-linux type OS
# where yum package manager is available.

# 1) Install clamav
sudo yum install -y clamav.x86_64

# 2) Getting virus database
sudo freshclam

# 3) Validate installation by checking the version
clamscan --version
rc=$?
if [[ $rc != 0 ]]; then
  echo "Error installing CLAMAV"
  exit $rc
else
  echo "Successfull intallation of CLAMAV"
fi
