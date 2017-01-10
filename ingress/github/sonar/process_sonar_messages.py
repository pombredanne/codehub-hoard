#!/usr/bin/env python

import clone_repos
from pykafka import KafkaClient
import pickle,process_sonar, kafkaConsumer,kafkaProducer
import os, sys
sys.path.append(os.path.abspath("../config"))
import configparams

def process_messages(messages,config,topic):
    for message in messages:
        if message is not None:
            data = pickle.loads(message.value)
            processed_sonar_data = process_sonar.automate_processes(config,data)
            print(processed_sonar_data)
            kafkaProducer.publish_kafka_message(processed_sonar_data, config, topic)
        else:
            pass

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    messages = kafkaConsumer._get_balanced_consumer(config)
    print(messages)
    process_messages(messages,config,config['config']['sonar_topic'])
