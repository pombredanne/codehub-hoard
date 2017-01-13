#!/usr/bin/env python
from pykafka import KafkaClient
import pickle, process_es_dependency_update, kafkaConsumer,kafkaConsumer_update
import os, sys,signal
sys.path.append(os.path.abspath("../config"))
import configparams


def process_es_update(messages,config):
    for message in messages:
        if message is not None:
            processed_dependecy_data = pickle.loads(message.value)
            print("processed dependecy data....")
            print(processed_dependecy_data)
            process_es_dependency_update.automate_processes(config,processed_dependecy_data)
        else:
            pass

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer_update._get_balanced_consumer(config)
    process_es_update(messages,config)
