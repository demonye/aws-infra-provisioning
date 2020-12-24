#!/bin/sh

repo_name=$(cat config.json |jq -r .source_repo)
cmd_output=$(aws codecommit create-repository --repository-name $repo_name 2>&1)
echo $cmd_output |grep -q "already exists"
if [ $? -eq 0 ]; then
    echo "The repository $repo_name exists!"
    echo -n "Do you want delete it and re-create? [y/N] " && read confirmed
    if [ "$confirmed" = "y" ] || [ "$confirmed" = "Y" ]; then
        aws codecommit delete-repository --repository-name $repo_name
        aws codecommit create-repository --repository-name $repo_name
    else
        echo User abort!
        exit 1
    fi
fi

git_email=$(git config user.email)
if [ -z "$git_email" ]; then
    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"
fi
git init
echo "0.0.1" >version.txt
git add . && git commit -am "initial command"
git remote add origin codecommit::$AWS_DEFAULT_REGION://$repo_name
git push -u origin master

table_name=$(cat config.json |jq -r .table_name)
aws dynamodb create-table \
    --table-name $table_name \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=10,WriteCapacityUnits=5
