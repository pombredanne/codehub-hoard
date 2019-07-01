#!/usr/bin/env python

import glob2
import requests
import json
import xmltodict
import shutil,pickle
import pickle, kafkaConsumer, kafkaProducer
import time
import logging
from subprocess import Popen, PIPE
import subprocess
from os.path import expanduser
from pykafka import KafkaClient
import os, sys
sys.path.append(os.path.abspath("../config"))
#pylint: disable=import-error
import configparams
ssl_verify='/etc/ssl/cert.pem'


def _prepare_update_data(data):
    if data is None:
        return None

    vscan = data['vscan']
    if vscan is None:
        return None

    result = {"doc" : {"vscan" : vscan}}

    return result


def _update_project_data(config, data):
    configurations = config['config']
    es_url = configurations['stage_es_url']
    project_id = data['_id']
    if project_id is None:
        print(time.strftime("%c")+" ERROR: Invalid project id.")
        return None

    es_request_url = es_url+'/projects/project/'+project_id+'/_update'
    print(es_request_url)
    update_data = _prepare_update_data(data)
    if update_data is None:
        print(time.strftime("%c")+" ERROR: Invalid data.")
        return None
    # print(json.dumps(update_data,indent=2))

    resp = requests.post(es_request_url, data=json.dumps(update_data))
    if resp:
        print(time.strftime("%c")+" Project data updated ("+project_id+").")
    else:
        print(time.strftime("%c")+" ERROR: Fail to updated project data : Response status code: "+str(resp.status_code))


def _process_messages(config, messages):
    for message in messages:
        if message is None:
            continue

        data = pickle.loads(message.value)
        if data is None:
            continue

        print(time.strftime("%c")+" VSProc started for : "+data["org"]+"->"+data["project_name"])

        _update_project_data(config, data)

        print(time.strftime("%c")+" VSProc completed")


def automate_process(config):
    print(time.strftime("%c")+" VSProc processing started")
    messages = kafkaConsumer._get_balanced_consumer(config,'consumer_vsresult_group')
    _process_messages(config, messages)
    print(time.strftime("%c")+" VSProc processing completed")


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_process(config)
