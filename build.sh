#!/bin/bash

if command -v podman &> /dev/null
then
    export CONTAINER_RUNTIME=podman
elif command -v docker &> /dev/null
then
    export CONTAINER_RUNTIME=docker
else
    echo "Neither Podman nor Docker is installed"
fi


USERNAME=lausser
IMAGE=kraken-watch
$CONTAINER_RUNTIME build -t $USERNAME/$IMAGE:latest .
