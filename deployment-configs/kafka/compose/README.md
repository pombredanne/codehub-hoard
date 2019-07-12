# Kafka via Docker-Compose

This folder contains a docker-compose.yml file that fully encapsulates all necessary resources for a local Kafka deployment.

# Usage Instructions

### 1. Set the DOCKER_HOST_IP environment variable 

If you're on a unix machine: 

Run ifconfig
Look for "inet addr:" under the desired network interface - generally "eth0" for Linux and "en0" for OSX
Copy that IP address and then run command export DOCKER_HOST_IP=<addr>

### 2. Build and run the containers

Run `docker-compose up --build -d`

### Extra Information

Run `docker-compose rm -fvs` to stop and delete the docker containers.