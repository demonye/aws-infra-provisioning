#!/bin/sh

account_id=$(aws sts get-caller-identity |jq -r .Account)
repository_uri=$(aws ecr describe-repositories --repository-name simpletodo 2>/dev/null |jq -r .repositories[0].repositoryUri)
if [ -z $repository_uri ] || [[ "$repository_uri" = "null" ]]; then
    repository_uri=$(aws ecr create-repository --repository-name simpletodo |jq -r .repository.repositoryUri)
fi

docker build . -t $repository_uri:latest
$(aws ecr get-login $region --no-include-email)
docker push $repository_uri:latest
