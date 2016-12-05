#!/usr/bin/env python

import json
import logging
import os
import shutil
import time

import glob2
import requests
import xmltodict
from git import Repo

import configparams

def filter_dependencies(repo):
    filtered_dependency = []
    if repo is not None:
        for filter in repo['dependency_content']:
            if not 'content' in filter:
                filtered_dependency.append(filter)
        return filtered_dependency

def _make_elasticsearch_updates(config, repo):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    data_json = {"componentDependencies": repo['dependency_content']}
    update_query = {
      "doc": data_json
    }
    res = requests.post(configurations['stage_es_url']+'/projects/project/'+repo['_id']+'/_update', data=json.dumps(update_query))
    return res

def _process_elasticsearch_update(config, results):
    logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
    collected_response = _make_elasticsearch_updates(config, results)
    print(collected_response)


def fetch_non_empty_dependencies(config, repo):
    if repo is not None:
        filtered_dependency = filter_dependencies(repo)
        repo['dependency_content'] = filtered_dependency
        return repo



def automate_processes(config,repo):
    logging.info(time.strftime("%c")+' Started')
    filtered_repo = fetch_non_empty_dependencies(config, repo)
    _process_elasticsearch_update(config,filtered_repo)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config, repo)
