#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json,decimal
import xmltodict
import shutil
import automate_sonar_dependencies,kafkaProducer,process_es
import time
import logging
from subprocess import call,check_output
import subprocess,pickle
import os, sys
sys.path.append(os.path.abspath("../config"))
import configparams

def process_cloned_projects(repo):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repo_map = {}
    print("repo cloned_project_path")
    print(repo)
    if "cloned_project_path" in repo and repo["cloned_project_path"] is not None:
        src_dir = repo['cloned_project_path']+'/*/'
        lists = glob2.glob(src_dir)
        if(len(lists) > 0):
            repo_map['_id'] = repo['_id']
            repo_map['project_name'] = repo['project_name']
            repo_map['src_list'] = lists
            repo_map['org'] = repo['org']
            repo_map['language'] = repo['language']
            repo_map['root_dir'] = repo['cloned_project_path']
    return repo_map

def build_sonar_project_config(repos_src,config):
    configurations = config['config']
    writeToConfigFile(repos_src)
    run_sonar_script(repos_src['root_dir'],configurations['sonar_runner_path'])


def writeToConfigFile(repo):
    aggregated_src = ''
    exclusions = '**/system/**, **/test/**, **/img/**, **/logs/**, **/fonts/**, **/generated-sources/**, **/packages/**, **/docs/**, **/node_modules/**, **/bower_components/**,**/dist/**,**/unity.js,**/bootstrap.css, **/tools/**'
    for src in repo['src_list']:
        aggregated_src = src + "," + aggregated_src
    file_object = open(repo['root_dir']+"/sonar-project.properties", 'w')
    file_object.write("sonar.projectKey="+repo['project_name'])
    file_object.write("\n")
    file_object.write("sonar.projectName="+repo['project_name']+" of "+repo["org"])
    file_object.write("\n")
    file_object.write("sonar.projectVersion=1.0")
    file_object.write("\n")
    file_object.write("sonar.sources="+aggregated_src)
    file_object.write("\n")
    file_object.write("sonar.exclusions=file:"+exclusions)
    file_object.write("\n")
    file_object.write("sonar.sourceEncoding=UTF-8")

def run_sonar_script(repo_dir,runner_dir):
    curr_dir = os.getcwd()
    os.chdir(repo_dir)
    curr_sonar_dir = os.getcwd()
    call(["ls","-l"])
    call(runner_dir,shell=True)
    os.chdir(curr_dir)

def make_sonar_api_call(processed_repos,config):
    processed_repos['metrics'] = process_sonar_api_call(processed_repos,config)
    return processed_repos


def process_sonar_api_call(repo,config):
    configurations = config['config']
    metrics_list = configurations['sonar_health_metrics']
    health_metrics_map = {}

    res = '_response'
    for metric in metrics_list:
        print("In updating ptoblems....")
        print(repo['project_name'])
        returned_res = requests.get(configurations['sonar_api_local_base_url']+'?resource='+repo['project_name']+"&metrics="+metric)
        returned_json = {}
        print(returned_res)
        if(returned_res.status_code == 200):
            if(len(json.loads(returned_res.text)) > 0):
                if 'msr' in json.loads(returned_res.text)[0]:
                    returned_json = json.loads(returned_res.text)[0]['msr']
                    if len(returned_json) > 0:
                        health_metrics_map[metric] = returned_json[0]
                    else:
                        health_metrics_map[metric] = {}
            else:
                health_metrics_map[metric] = {}
    return health_metrics_map

def create_result_json(filtered_repos, config):
    configurations = config['config']
    sonar_result_path = os.getcwd()+"/sonar_health_metrics.json"
    collected_metrics = []
    for repo_metric in filtered_repos:
        collected_metrics.append(repo_metric)
    with open(sonar_result_path, 'a+') as outfile:
        for metrics in collected_metrics:
            json.dump(metrics, outfile, indent=4, sort_keys=True, separators=(',', ':'))
        outfile.write(',')
    return sonar_result_path

def read_cloned_projects(config):
    json_map = {}
    json_repos = []
    configurations = config['config']
    repos_json = os.getcwd()+"/cloned_repos_data.json"
    with open(repos_json) as data_file:
        try:
             for g in data_file:
                 json_repos.append(g)
        except ValueError:
             data = []
    return json_repos

def automate_processes(config,repo_json):
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    configurations = config['config']
    if bool(repo_json):
        if repo_json is not None:
            processed_repos = process_cloned_projects(repo_json)
            if bool(processed_repos):
                build_sonar_project_config(processed_repos,config)
                filtered_repos = make_sonar_api_call(processed_repos,config)
                return filtered_repos
