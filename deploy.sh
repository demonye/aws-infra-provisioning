#!/bin/bash


if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    read access_key_id
    export AWS_ACCESS_KEY_ID=$access_key_id
fi
if [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    read secret_access_key
    export AWS_SECRET_ACCESS_KEY=$secret_access_key
fi
if [[ -z "$AWS_DEFAULT_REGION" ]]; then
    read region_name
    export AWS_DEFAULT_REGION=$region_name
fi

# dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 2>&1 &
# sleep 3

cd demoapp
ash ./set_code.sh
ash ./build.sh
cd ..

cdk deploy


