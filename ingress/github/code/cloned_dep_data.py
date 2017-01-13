#!/usr/bin/env python

from pykafka import KafkaClient
import pickle, process_dependency, kafkaConsumer, kafkaProducer
import os, sys,signal
sys.path.append(os.path.abspath("../config"))
import configparams

def process_messages(messages,config,topic):
    print("i am here")
    print(messages)
    for message in messages:
        if message is not None:
            print("processed clone data for dep ....")
            print(message.value)
            data = pickle.loads(message.value)
            print(data)
            kafkaProducer.publish_kafka_message(data, config, topic)
        else:
            print("processed clone data for dep nope....")

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer._get_balanced_consumer(config)
    print(messages)
    process_messages(messages,config,config['config']['clone_dep_topic'])
