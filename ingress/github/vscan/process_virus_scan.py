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

class ProcessVirusScan() :

    def _prepare_update_data(self, data):
        if data is None:
            return None

        if 'vscan' not in data:
            return None

        vscan = data['vscan']

        result = {"doc" : {"vscan" : vscan}}

        return result


    def _update_project_data(self, config, data):
        configurations = config['config']
        es_url = configurations['stage_es_url']
        if "_id" not in data:
            print(time.strftime("%c")+" ERROR: Invalid project id.")
            return None

        project_id = data['_id']

        es_request_url = es_url+'/projects_gio/project/'+project_id+'/_update'
        print(es_request_url)
        update_data = self._prepare_update_data(data)
        if update_data is None:
            print(time.strftime("%c")+" ERROR: Invalid data.")
            return None
        # print(json.dumps(update_data,indent=2))

        resp = requests.post(es_request_url, data=json.dumps(update_data))
        if resp.status_code == 200:
            print(time.strftime("%c")+" Project data updated ("+project_id+").")
            return True
        else:
            print(time.strftime("%c")+" ERROR: Fail to updated project data : Response status code: "+str(resp.status_code))
            return False


    def _process_messages(self, config, messages):
        for message in messages:
            if message is None:
                continue

            data = pickle.loads(message.value)
            if data is None:
                continue

            print(time.strftime("%c")+" VSProc started for : "+data["org"]+"->"+data["project_name"])

            self._update_project_data(config, data)

            print(time.strftime("%c")+" VSProc completed")


    def automate_process(self, config):
        print(time.strftime("%c")+" VSProc processing started")
        messages = kafkaConsumer._get_balanced_consumer(config,'consumer_vsresult_group')
        self._process_messages(config, messages)
        print(time.strftime("%c")+" VSProc processing completed")


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    pvs = ProcessVirusScan()
    pvs.automate_process(config)
