#!/usr/bin/env python

import glob2
import requests
import json
import xmltodict
import shutil,pickle
import pickle, kafkaConsumer, kafkaProducer
import time
import logging
from subprocess import call,check_output
import subprocess
from os.path import expanduser
from pykafka import KafkaClient
import os, sys
sys.path.append(os.path.abspath("../config"))
import configparams
ssl_verify='/etc/ssl/cert.pem'

def create_mock_message(config):
    # repo variable represents the message data pushed to the CLONED_DATA_QUEUE once a repo is cloned.
    repo = {}
    repo['_id'] = '33698304_117576470'
    repo['project_name'] = 'fedgov-cv-whtools-webapp'
    repo['clone_url'] = ''
    repo['language'] = 'CSS'
    repo['org'] = 'usdot-jpo-sdcsdw'
    repo['cloned_project_path'] = '[*-UPDATE-REAL-PATH-HERE-*]/cloned_projects/Stage/stage-webapp'
    print(repo)
    kafkaProducer.publish_kafka_message(repo,config,'CLONED_DATA_QUEUE')

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    create_mock_message(config)