#!/usr/bin/env python

import configparams,os, signal
from pykafka import KafkaClient
import pickle, process_es_dependency_update, kafkaConsumer,kafkaConsumer_update

def process_es_update(messages,config):
    for message in messages:
        if message is not None:
            processed_dependecy_data = pickle.loads(message.value)
            process_es_dependency_update.automate_processes(config,processed_dependecy_data)
        else:
            pass

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer_update._get_balanced_consumer(config)
    print("messages 222")
    process_es_update(messages,config)
