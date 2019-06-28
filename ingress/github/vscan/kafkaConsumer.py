#!/usr/bin/env python
from pykafka import KafkaClient
import pickle


def _get_balanced_consumer(config, consumer_group_name):
    configurations = config['config']
    client = KafkaClient(hosts=configurations['kafka_host'])
    print(configurations['topic'])
    topic = client.topics[configurations['topic'].encode('ascii')]
    balanced_consumer = topic.get_balanced_consumer(consumer_group=configurations[consumer_group_name].encode('ascii'), auto_commit_enable=True,auto_start=True, zookeeper_connect=configurations['zookeeper_connect'])
    return balanced_consumer
