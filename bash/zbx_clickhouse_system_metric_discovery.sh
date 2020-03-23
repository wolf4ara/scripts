#!/bin/bash

set -e

CH_HOST="${1:-localhost}"
PORT="${2:-9440}"
USER="${3:-zabbix}"

function json {
        JSON_DATA="[ "
        for METRIC in $(/usr/bin/clickhouse-client -s -h $CH_HOST --port $PORT -u $USER -q 'select metric from system.metrics')
        do
                JSON_STRING=$(jq -n --arg mn "$METRIC" '{"{#METRIC_NAME}": $mn}')
                if [[ "$JSON_DATA" == "[ " ]]
                then
                        JSON_DATA="${JSON_DATA}${JSON_STRING}"
                else
                        JSON_DATA="${JSON_DATA},${JSON_STRING}"
                fi
        done
        JSON_DATA="${JSON_DATA}]"
        echo $JSON_DATA
}

json 
