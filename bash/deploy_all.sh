#!/usr/bin/env bash

set -e
set -o nounset
set -x 

PR_LIST=$1
TOKEN="PRIVATE-TOKEN: $2"
DUSER=$3
IG_LIST=${4:-service}
URL="https://xdevteam.com/api/v4"
TNAME="deployman"
VARSDEPLOY=""

function operations {

if [[ "$PR_LIST" == "s7_css" ]] || [[ "$PR_LIST" == "f1" ]]
then
	VARSDEPLOY=$PR_LIST
	PR_LIST="demo"
fi

[ "$1" == "exclude" ] && PARAM=" -E -v $IG_LIST" || PARAM=" -E $PR_LIST"

for page in $(seq 1 $(curl -s -H "$TOKEN" "${URL}/groups/casino-react/projects?per_page=100&page=1" -I | awk '/x-total-pages/ { sub(/\r/,"",$2); print $2}'))
	do
	curl -s -H "$TOKEN" "${URL}/groups/casino-react/projects?per_page=100&page=$page" \
	| jq -r '.[] | "\(.path_with_namespace)\t\(.id)"' | grep $PARAM \
	| while read PROJECT
	do
		[ -z $VARSDEPLOY ] && PUTVARS="-F variables[DUSER]=$DUSER" || PUTVARS="-F variables[DUSER]=$DUSER -F variables[DEPLOY_SERVER]=$VARSDEPLOY"
		PID=$(echo $PROJECT| awk '{print $2}')
		PNAME=$(echo $PROJECT| awk '{print $1}' | sed 's/.*\///')
		echo $PNAME
		TDATA=$(curl -g -H "$TOKEN" "${URL}/projects/$PID/triggers" | jq -r '.[] | "\(.description) \(.token)"' | awk '/'$TNAME'/')
		[ -z "$TDATA" ] && TT=$(curl -g -H "$TOKEN" -F description="$TNAME" "${URL}/projects/$PID/triggers" |jq -r '.token') || TT=$(echo $TDATA| awk '{print $2}')
		curl -X POST -F token=$TT -F ref=develop $PUTVARS ${URL}/projects/$PID/trigger/pipeline
	done
done
}

# main

[ "$PR_LIST" == "ALL" ] && operations exclude || operations include
