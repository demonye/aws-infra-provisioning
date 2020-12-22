#!/bin/sh


if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo -n "AWS access_key_id: " && read access_key_id
    export AWS_ACCESS_KEY_ID=$access_key_id
fi
if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -n "AWS secret_access_key: " && read secret_access_key
    export AWS_SECRET_ACCESS_KEY=$secret_access_key
fi
if [ -z "$AWS_DEFAULT_REGION" ]; then
    echo -n "AWS region_name: " && read region_name
    export AWS_DEFAULT_REGION=$region_name
fi

# dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 2>&1 &
# sleep 3

# setup demoapp API code
cd demoapp/api
sh ./set_code.sh
sh ./build.sh
cd ../..

# setup demoapp API code
cd demoapp/web
sh ./set_code.sh
cd ../..

cdk deploy


