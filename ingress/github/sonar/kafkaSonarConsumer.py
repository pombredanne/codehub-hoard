#!/usr/bin/env python

import configparams,clone_repos,os, signal,process_es
from pykafka import KafkaClient
import json,process_sonar


def consume_kafka_sonar_data(config):
    configurations = config['config']
    clone_data = []
    client = KafkaClient(hosts=configurations['kafka_host'])
    topic = client.topics[b'SONAR_DATA_QUEUE']
    print(configurations)
    print(configurations['consumer_group'])
    balanced_consumer = topic.get_balanced_consumer(consumer_group=b'sonar_group', auto_commit_enable=True,auto_start=True,reset_offset_on_start=False, zookeeper_connect=configurations['zookeeper_connect'])
    i = 0
    for message in balanced_consumer:
        if message is not None:
            #print(message.value.decode('ascii'))
            #process_sonar.automate_processes(config)
            data = message.value.decode('ascii')
            print(message.value.decode('ascii'))
            process_es.automate_processes(config,message.value.decode('ascii'))
            clone_data.append(data)
            #clone_repos.result_json(clone_data, config)
            result_json(message.value.decode('ascii'),config)
            #process_sonar.automate_processes(config,message.value.decode('ascii'))
            #clone_repos.result_json("\n",config)
            #i = i+1
            #print(data)
        else:
            pass
    print(configurations)

def result_json(repos, config):
    configurations = config['config']
    print("Demeke yeeepe Kassaye")
    #print(len(repos))
    #print(repos)

    #result_path = configurations['cloned_projects_json_file_path']
    result_json_dir = "sonar_repos_data.json"
    #delete_directory(os.getcwd()+"/"+result_json_dir)
    with open(result_json_dir, 'w') as outfile:
        json.dump(repos, outfile, indent=4, sort_keys=True, separators=(',', ':'))
        #data = outfile.write(repos)
        #print(json.load(repos))
        print("Demeke")
        #outfile.write(",")
        #outfile.write("\n")
    return result_json_dir

if __name__ == "__main__":
    print("In the sonar consumer")
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    consume_kafka_sonar_data(config)
    #process_consumed_data()
