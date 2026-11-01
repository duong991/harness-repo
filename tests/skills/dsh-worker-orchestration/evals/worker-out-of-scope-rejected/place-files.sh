#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q && echo ".dsh-test/" >> .git/info/exclude
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm init
