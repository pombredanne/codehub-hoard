#!/usr/bin/env python
import configparams
from pykafka import KafkaClient
import json,pickle

def publish_kafka_message(repo,config, *args):
    configurations = config['config']
    client = KafkaClient(hosts=configurations['kafka_host'])
    message_topic = ""
    if args:
        message_topic = args[0].encode('ascii')
    else:
        message_topic = configurations['topic'].encode('ascii')
    print(message_topic)
    topic = client.topics[message_topic]
    with topic.get_producer() as producer:
        repo_byte = pickle.dumps(repo)
        producer.produce(repo_byte)
