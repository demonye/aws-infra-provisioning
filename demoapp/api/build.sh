#!/bin/sh

repo_name=$(cat config.json |jq -r .source_repo)
account_id=$(aws sts get-caller-identity |jq -r .Account)
repository_uri=$(aws ecr describe-repositories --repository-name $repo_name 2>/dev/null |jq -r .repositories[0].repositoryUri)
if [ -z $repository_uri ] || [[ "$repository_uri" = "null" ]]; then
    repository_uri=$(aws ecr create-repository --repository-name $repo_name |jq -r .repository.repositoryUri)
fi

docker build . -t $repository_uri:latest
$(aws ecr get-login $region --no-include-email)
docker push $repository_uri:latest
