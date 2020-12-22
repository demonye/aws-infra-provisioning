#!/bin/sh

repo_name=SimpleTodo
cmd_output=$(aws codecommit create-repository --repository-name $repo_name 2>&1)
echo $cmd_output |grep -q "already exists"
if [ $? -eq 0 ]; then
    echo "The repository $repo_name exists!"
    echo "Do you want delete it and re-create? [y/N] " && read confirmed
    if [[ "$confirmed" == "y" ]] || [[ "$confirmed" == "Y" ]]; then
        aws codecommit delete-repository --repository-name $repo_name
        aws codecommit create-repository --repository-name $repo_name
    else
        echo User abort!
        exit 1
    fi
fi

git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git init
git add . && git commit -am "initial command"
git remote add origin codecommit::$AWS_DEFAULT_REGION://$repo_name
git push -u origin master
