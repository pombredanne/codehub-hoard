#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json
import xmltodict
import os
import shutil
import configparams,automate_sonar_dependencies,automate_sonar_processing
import time
import logging
from subprocess import call,check_output, run
import subprocess


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
            collected_response['metrics'] = res['metrics']
            collected_response['returned_res'] = returned_res
            returned_responses_collection.append(collected_response)
    return returned_responses_collection

def makeEsUpdates(config,returned_responses):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    for ret in returned_responses:
        project_id = ret['returned_res']['hits']['hits'][0]['_id']
        filtered_health_metrics = ret['metrics']

        if len(filtered_health_metrics) > 0:
            data_json = {"project_health_metrics": filtered_health_metrics}
            update_query = {
              "doc": data_json
            }
            ret_response = requests.post(configurations['stage_es_url']+'/projects/logs/'+project_id+'/_update', data=json.dumps(update_query))
            if project_id not in collected_ids:
                collected_ids.append(project_id)
                collected_response.append(json.loads(ret_response.text))
    return collected_response

def process_elasticSearch_update(results, config):
    if config['update'] == 'results.out':
        logging.info(time.strftime("%c")+' Writing the result data to a local file results.out')
        write_results(config['update'], results)
    else:
        logging.info(time.strftime("%c")+' talking to ES and adding project metrics attribute with processed data')
        res_arr = get_es_project(config,results)
        collected_response = makeEsUpdates(config,res_arr)
        display_stats(config, collected_response)

def write_results(resultfile,results):
    file_object = open(os.getcwd()+"/"+resultfile, 'w')
    file_object.write("\t******************** The following Projects have health metrics ********************************\n\n")
    for res in results:
        file_object.write(json.dumps(res))
        file_object.write("\n")

def display_stats(config, response_arr):
    logging.info(time.strftime("%c")+" ******The following "+str(len(response_arr)) + " projects have health metrics ******")
    repos_just_updated = []
    configurations = config['config']
    for repo in response_arr:
        response = requests.get(configurations['stage_es_url']+'/projects/logs/'+repo['_id'])
        logging.info(json.loads(response.text))
        if(repo['_shards']['successful'] == 1):
            repos_just_updated.append(json.loads(response.text))

    if(len(repos_just_updated) > 0):
        logging.info("******The following projects are "+ str(len(repos_just_updated))+" just updated******")
        for repo in repos_just_updated:
            logging.info(repo)
    else:
        logging.info(time.strftime("%c")+" **** No Project is updated ****")

def cleanup_after_update():
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' cleaning up cloned projects after elasticsearch updates or written to a file')
    delete_directory(clone_dir)

def read_result_file(res_dir):
    json_res = []
    with open(res_dir) as data_file:
        try:
             data = json.load(data_file)
             json_res = data
        except ValueError:
             data = []
    return json_res


def automate_processes(config):
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    #res_dir = os.getcwd()+"/metric_result.json"
    configurations = config['config']
    sonar_result_path = configurations['cloned_projects_json_file_path']+"/sonar_health_metrics.json"
    if os.path.exists(sonar_result_path):
        results = read_result_file(sonar_result_path)
        print(results)
        process_elasticSearch_update(results, config)
    else:
        automate_sonar_processing.automate_processes(config)
        results = read_result_file(res_dir)
        print(results)
        process_elasticSearch_update(results, config)

    #cleanup_after_update()

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
