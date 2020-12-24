#!/bin/bash

bumping_type=${1:-"patch"}
echo "$bumping_type" |grep -qE "^(major|minor|patch)$"
if [ $? -ne 0 ]; then
    echo "bumping type must be one of the values: major, minor, patch"
    exit 1
fi

version=$(sed -n 's/^.*version="\([0-9.]\+\)".*$/\1/p' setup.py)
major=$(echo $version |cut -d. -f1)
minor=$(echo $version |cut -d. -f2)
patch=$(echo $version |cut -d. -f3)

(( $bumping_type += 1 ))
if [ "$bumping_type" = "major" ]; then
    minor=0
    patch=0
fi
if [ "$bumping_type" = "minor" ]; then
    patch=0
fi
version=$major.$minor.$patch

sed -i "s/^\(.*version=\"\)\([0-9.]\+\)\(\".*\)$/\1$version\3/" setup.py
grep -nH version setup.py

git ci -am "bumping tag to $version" && git push
git tag $version && git push origin $version
