#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json
import xmltodict
import shutil, pickle
import automate_sonar_dependencies,automate_sonar_processing
import time
import logging
from subprocess import call,check_output
import subprocess
import os, sys
sys.path.append(os.path.abspath("../config"))
import configparams

def _process_elasticSearch_update(config,returned_responses):
    logging.info(time.strftime("%c")+' talking to ES and adding project metrics attribute with processed data')
    configurations = config['config']
    if returned_responses is not None:
        if 'metrics' in returned_responses:
            filtered_health_metrics = returned_responses['metrics']
            if len(filtered_health_metrics) > 0:
                data_json = {"project_health_metrics": filtered_health_metrics}
                update_query = {
                  "doc": data_json
                }
                ret_response = requests.post(configurations['stage_es_url']+'/code/project/'+returned_responses['_id']+'/_update', data=json.dumps(update_query))
                print(ret_response)

def automate_processes(config, repos_metrics):
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    configurations = config['config']
    print(repos_metrics)
    _process_elasticSearch_update(config, repos_metrics)
    print("...completing updating ES")
