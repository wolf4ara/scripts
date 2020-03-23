#!/usr/bin/env python3
"""get list consumer group, parts, topics
and it's status and lags
"""
import argparse
import json
import socket
from kafka.admin.client import KafkaAdminClient
from kafka.protocol.group import MemberAssignment
from kafka import KafkaConsumer, TopicPartition

def connect_to_kafka(params):
    """connect to kafa server
    """
    return KafkaAdminClient(**params, request_timeout_ms=100)

def disconnect_to_kafka(connection):
    """buy kafka-server
    """
    return connection.close()

def arguments():
    """parsing arguments
    """
    hostname = socket.gethostname()
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='bootstrap ip addr', required=True)
    parser.add_argument('--port', help='bootstrap server port', default=9093, type=int)
    parser.add_argument('--cacert', help='path to ca cert', default='/etc/ssl/kafka/kafka.crt')
    parser.add_argument('--cert', help='path to ssl cert', \
            default='/etc/ssl/kafka/' + hostname + '.crt')
    parser.add_argument('--key', help='path to ssl key', default='/etc/ssl/kafka/'\
            + hostname + '.key')
    parser.add_argument('--action', help='run action for get elements monitoring', required=True, \
            choices=['discovery_groups', 'get_groups_status', 'get_lags_from_groups', \
            'get_lag_from_group', 'discovery_info_about_lags', 'discovery_info_from_group'])
    parser.add_argument('--group', help='consumer group, to get lag info')
    return parser.parse_args()

def discovery_groups(connect):
    """find consumer groups
    """
    dump = []
    for group in connect.list_consumer_groups():
        dump.append({"{#KAFKA_CONSUMER_GROUP_LIST}": group[0]})
    print(json.dumps({"data": dump}))

def get_groups_status(connect, data):
    """get status each group
    """
    group_status = []
    for group in data:
        describe = connect.describe_consumer_groups([group])
        if describe:
            if describe[0][2] in 'Stable':
                group_status.append(str(group) + ' 0')
            elif describe[0][2] in 'PreparingRebalance':
                group_status.append(str(group) + ' 1')
            elif describe[0][2] in 'Empty':
                group_status.append(str(group) + ' 2')
            elif describe[0][2] in 'Dead':
                group_status.append(str(group) + ' 3')
            elif describe[0][2] in 'NonExisting':
                group_status.append(str(group) + ' 4')
            else:
                group_status.append(str(group) + ' 5')
        else:
            group_status.append(str(group) + ' 6')
    return group_status

def get_lags_from_groups(connect):
    """get lags from groups
    """
    for group in connect.list_consumer_groups():
        get_lag_from_group(connect, group[0])

def get_lag_from_group(connect, group):
    """get lag from group
    """
    consumer = KafkaConsumer(**CONNECT_PARAMS, request_timeout_ms=10001, group_id=group)
    for member in connect.describe_consumer_groups([group])[0][5]:
        for data in MemberAssignment.decode(member[4]).assignment:
            topic = data[0]
            parts = data[1]
            for part in parts:
                topart = TopicPartition(topic, part)
                last_offsets = consumer.end_offsets([topart])
                committed = consumer.committed(topart)
                if last_offsets != None and committed != None:
                    lag = last_offsets.get(topart) - committed
                    print("group: {} topic: {} partition: {} lag: {}".\
                            format(group, topic, part, lag))

def discovery_info_from_group(connect, group):
    """discovery topics and parts from group
    """
    lags = []
    for member in connect.describe_consumer_groups([group])[0][5]:
        for data in MemberAssignment.decode(member[4]).assignment:
            topic = data[0]
            parts = data[1]
            for part in parts:
                lags.append({"{#CGRP}": group, "{#PRT}": part, "{#TOP}": topic})
    print(json.dumps(lags))

def discovery_info_about_lags(connect):
    """discovery data for monitoring
    """
    for group in connect.list_consumer_groups():
        discovery_info_from_group(connect, group[0])

if __name__ == '__main__':
    ARGS = arguments()
    CONNECT_PARAMS = {'bootstrap_servers': str(ARGS.server) + ":" + str(ARGS.port), \
            'security_protocol': 'SSL', 'ssl_check_hostname': False, 'ssl_cafile': ARGS.cacert, \
            'ssl_certfile': ARGS.cert, 'ssl_keyfile': ARGS.key}
    CLIENT = connect_to_kafka(CONNECT_PARAMS)
    if ARGS.action == 'discovery_groups':
        discovery_groups(CLIENT)
    if ARGS.action == 'get_groups_status':
        RESULT = get_groups_status(CLIENT, CLIENT.list_consumer_groups())
        for RX in RESULT:
            print(RX)
    if ARGS.action == 'get_lags_from_groups':
        get_lags_from_groups(CLIENT)
    if ARGS.action == 'discovery_info_about_lags':
        discovery_info_about_lags(CLIENT)
    if ARGS.action == 'get_lag_from_group':
        get_lag_from_group(CLIENT, ARGS.group)
    if ARGS.action == 'discovery_info_from_group':
        if ARGS.group:
            discovery_info_from_group(CLIENT, ARGS.group)
        else:
            print("Enter group name")
    disconnect_to_kafka(CLIENT)
