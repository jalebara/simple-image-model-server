#!/bin/bash

# Run the server with a GPU and expose port 8000
PORT=8000
RUNTIME=nvidia

docker volume create image-model-server-data

docker run --rm --ipc=host -p $PORT:$PORT --runtime=$RUNTIME \
    -v image-model-server-data:/data \
    image-model-server