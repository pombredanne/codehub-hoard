#!/usr/bin/env python

import configparams,os, signal
from pykafka import KafkaClient
import pickle, process_dependency, kafkaConsumer, kafkaProducer

def process_messages(messages,config,topic):
    for message in messages:
        if message is not None:
            data = pickle.loads(message.value)
            print(data)
            processed_dependecy_data = process_dependency.automate_processes(config,data)
            print("processed_dependecy_data ....")
            print(processed_dependecy_data)
            kafkaProducer.publish_kafka_message(processed_dependecy_data, config, topic)
        else:
            pass

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer._get_balanced_consumer(config)
    process_messages(messages,config,config['config']['dependency_topic'])
