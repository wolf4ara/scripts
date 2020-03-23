#!/bin/bash

#set -x

LAST_COMMIT=$1
PREVIOUS_COMMIT=$2

function lint {
	for file in $(git diff $PREVIOUS_COMMIT $LAST_COMMIT --name-status | awk '/\.sls/ {if ($1 == "A" || $1 == "M") print $2}')
	do
		/usr/local/bin/salt-lint $file
	done
}

[ -z "$(git diff $PREVIOUS_COMMIT $LAST_COMMIT --name-status | awk '/\.sls/ {if ($1 == "A" || $1 == "M") print $2}')" ] && echo "No files to check" || lint
