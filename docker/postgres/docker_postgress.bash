#!/bin/bash

# Make sure we have the posgres docker image
docker pull postgres:16.0

# Check to see if we have the ecosyste.ms dump file
# If not, download it
if [ ! -f ./data/ecosystems/*.sql ]; then
    wget https://ecosystems-data.s3.amazonaws.com/packages-2023-08-08.tar.gz -O ./data/ecosystems/packages-2023-08-08.tar.gz
    tar -xzf ./data/ecosystems/packages-2023-08-08.tar.gz -C ./data/ecosystems/
fi

# If so, load it into the postgres container
docker run --name postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 -v $(pwd)/data/ecosystems:/var/lib/postgresql/data postgres:16.0


