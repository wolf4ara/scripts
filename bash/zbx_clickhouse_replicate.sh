#!/bin/bash

set -o errexit

PARAM=$1
DB=$2
TABLE=$3
CH_HOST="${4:-localhost}"
PORT="${5:-9440}"
USER="${6:-zabbix}"
CONNECT="/usr/bin/clickhouse-client -s -h "$CH_HOST" --port $PORT -u $USER"

function discovery {
        echo "{ \"data\":[ "
        size=$($CONNECT -q 'select database,table from system.replicas'|wc -l)
        i=0
        for replica in $($CONNECT -q 'select database,table from system.replicas' | awk '{print $1"."$2}')
        do
                i=$((i+1))
                DB=$(echo $replica | awk -F'.' '{print $1}')
                TABLE=$(echo $replica | awk -F'.' '{print $2}')
                if [[ "$i" -eq "$size" ]]
                then
                        echo "{ \"{#DB}\": \"$DB\", \"{#TABLE}\": \"$TABLE\" }"
                else
                        echo "{ \"{#DB}\": \"$DB\", \"{#TABLE}\": \"$TABLE\" },"
                fi
        done
        echo "] }"
}

function get_data {
        $CONNECT -q "SELECT $PARAM FROM system.replicas WHERE database='$DB' and table='$TABLE'"
}

# main
[ "$PARAM" == "discovery" ] && discovery || get_data

exit 0
