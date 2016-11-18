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
    for filter in repo['dependency_content']:
        if not 'content' in filter:
            filtered_dependency.append(filter)
    return filtered_dependency

def _make_elasticsearch_updates(config, repos):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    for repo in repos:
        print(repo['_id'])
        data_json = {"componentDependencies": repo['dependency_content']}
        update_query = {
          "doc": data_json
        }
        #ret_response = requests.post(configurations['stage_es_url']+'/projects/project/'+repo['_id']+'/_update', data=json.dumps(update_query))
        #collected_response.append(json.loads(ret_response.text))
    return collected_response


def _process_elasticsearch_update(config, results):
    logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
    collected_response = _make_elasticsearch_updates(config, results)
    #display_stats(config, collected_response)

def display_stats(config, response_arr):
    logging.info(time.strftime("%c")+" ******The following "+str(len(response_arr)) + " projects have dependencies******")
    repos_just_updated = []
    configurations = config['config']
    for repo in response_arr:
        #print(repo['_id'])
        response = requests.get(configurations['stage_es_url']+'/projects/project/'+'7501879_46727828')
        logging.info(json.loads(response.text))

        if repo['_shards']['successful'] == 1:
            repos_just_updated.append(json.loads(response.text))

    if len(repos_just_updated) > 0:
        logging.info("******The following projects are "+ str(len(repos_just_updated))+" just updated******")
        for repo in repos_just_updated:
            logging.info(repo)
    else:
        logging.info(time.strftime("%c")+" **** No Project is updated ****")

def read_processed_projects(config):
    json_repos = []
    configurations = config['config']
    repos_json = configurations['cloned_projects_json_file_path']+"/project_dependencies.json"
    with open(repos_json) as data_file:
        try:
             data = json.load(data_file)
             json_repos = data
        except ValueError:
             data = []
    return json_repos

def fetch_non_empty_dependencies(config, repos):
    filtered_repos = []
    for repo in repos:
        filtered_dependency = filter_dependencies(repo)
        repo['dependency_content'] = filtered_dependency
        filtered_repos.append(repo)
    print(filtered_repos[0])
    return filtered_repos



def automate_processes(config):
    logging.info(time.strftime("%c")+' Started')
    processed_combined_results = read_processed_projects(config)
    #print(processed_combined_results[0])
    fetch_non_empty_dependencies(config, processed_combined_results)
    _process_elasticsearch_update(config,processed_combined_results)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
