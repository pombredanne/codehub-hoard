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


def get_es_project(config,results):
    returned_responses_collection = []
    configurations = config['config']
    for res in results:
        query_data = {
                      "query": {
                        "bool": {
                          "must": [
                            { "match": { "project_name":  res['project_name'] }},
                            { "match": { "organization": res['org']}}
                          ]
                        }
                      }
                    }
        response = requests.get(configurations['stage_es_url']+'/projects/logs/_search', data=json.dumps(query_data))
        returned_res = json.loads(response.text)
        collected_response = {}
        if returned_res['hits']['total'] > 0:
            collected_response['filtered'] = filter_dependencies(res)
            collected_response['returned_res'] = returned_res
            returned_responses_collection.append(collected_response)
    return returned_responses_collection


def _make_elasticsearch_updates(config, returned_responses):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    for ret in returned_responses:
        project_id = ret['returned_res']['hits']['hits'][0]['_id']
        filtered_repo_dependencies = ret['filtered']

        if len(filtered_repo_dependencies) > 0:
            data_json = {"componentDependencies": filtered_repo_dependencies}
            update_query = {
              "doc": data_json
            }
            ret_response = requests.post(configurations['stage_es_url']+'/projects/logs/'+project_id+'/_update', data=json.dumps(update_query))
            if project_id not in collected_ids:
                collected_ids.append(project_id)
                collected_response.append(json.loads(ret_response.text))
    return collected_response


def _process_elasticsearch_update(config, results):
    logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
    res_arr = get_es_project(config,results)
    collected_response = _make_elasticsearch_updates(config, res_arr)
    display_stats(config, collected_response)
    
def display_stats(config, response_arr):
    logging.info(time.strftime("%c")+" ******The following "+str(len(response_arr)) + " projects have dependencies******")
    repos_just_updated = []
    configurations = config['config']
    for repo in response_arr:
        response = requests.get(configurations['stage_es_url']+'/projects/logs/'+repo['_id'])
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

def automate_processes(config):
    logging.info(time.strftime("%c")+' Started')
    processed_combined_results = read_processed_projects(config)
    print(processed_combined_results)
    _process_elasticsearch_update(config,processed_combined_results)
    #cleanup_after_update()


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
