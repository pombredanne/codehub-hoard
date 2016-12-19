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
    if repo['dependency_content']:
    	repo_dep = repo['dependency_content'][0]
	if 'dependency_content' in repo_dep:
		data_json = {"componentDependencies": repo_dep['dependency_content']}
    	        print("repo")
    	        print(repo)
    	        print("data_json")
    	        print(data_json)
    	        update_query = {
      	        "doc": data_json
    	        }
    	        print(configurations['stage_es_url']+'/code/project/'+repo['_id']+'/_update')
    	        res = requests.post(configurations['stage_es_url']+'/code/project/'+repo['_id']+'/_update', data=json.dumps(update_query))
    	        print("update status....")
    	        print(res)
    	        return res
    else:
	pass

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
    print(filtered_repo)
    _process_elasticsearch_update(config,filtered_repo)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config, repo)
