#!/bin/bash

# build the server
docker build --network=host -t image-model-server  .
