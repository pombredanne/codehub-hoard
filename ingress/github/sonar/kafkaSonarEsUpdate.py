#!/usr/bin/env python

import configparams,clone_repos,os, signal
from pykafka import KafkaClient
import pickle, process_sonar, process_es,kafkaConsumer

def process_es_update(messages,config):
    for message in messages:
        if message is not None:
            processed_sonar_data = pickle.loads(message.value)
            print(processed_sonar_data)
            process_es.automate_processes(config,processed_sonar_data)
        else:
            pass

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer._get_balanced_consumer(config)
    print(messages)
    process_es_update(messages,config)
