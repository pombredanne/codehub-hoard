#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json
import xmltodict
import os
import shutil
import configparams,automate_sonar_dependencies
import time
import logging
from subprocess import call,check_output, run
import subprocess

def process_cloned_projects(repos):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repos_src = []
    for repo in repos:
        src_dir = repo['cloned_project_path']+'/*/'
        lists = glob2.glob(src_dir)
        repo_map = {}
        if(len(lists) > 0):
            repo_map['_id'] = repo['_id']
            repo_map['project_name'] = repo['project_name']
            repo_map['src_list'] = lists
            repo_map['org'] = repo['org']
            repo_map['language'] = repo['language']
            repo_map['root_dir'] = repo['cloned_project_path']
            repos_src.append(repo_map)
    return repos_src

def build_sonar_project_config(repos_src,config):
    runner_dir = automate_sonar_dependencies.install_sonar_runner_dependencies(config)
    for repo in repos_src:
        writeToConfigFile(repo)
        run_sonar_script(repo['root_dir'],runner_dir)


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

def install_sonar_runner_dependencies(config):
    configurations = config['config']
    runner_dir=''
    if(configurations['install_sonar_runner']):
        runner_dir=install_sonar_runner(config)
    return runner_dir

def install_sonar_runner(config):
    configurations = config['config']
    if not os.path.exists("sonar_runner_dir"):
        os.makedirs("sonar_runner_dir")
    os.chdir("sonar_runner_dir")
    if not os.path.exists("sonar-runner-2.4"):
        run(["wget", configurations['sonar_runner_url']],check=True)
        run(["unzip", "sonar-runner-dist-2.4.zip"],check=True)
    runner_dir = os.getcwd()+'/sonar-runner-2.4/bin/sonar-runner'
    return runner_dir


def make_sonar_api_call(processed_repos,config):
    filtered_repo = []
    for repo in processed_repos:
        repo['metrics'] = process_sonar_api_call(repo,config)
        filtered_repo.append(repo)
    return filtered_repo


def process_sonar_api_call(repo,config):
    configurations = config['config']
    metrics_list = configurations['sonar_health_metrics']
    health_metrics_map = {}

    res = '_response'
    for metric in metrics_list:
        returned_res = requests.get(configurations['sonar_api_local_base_url']+'?resource='+repo['project_name']+"&metrics="+metric)
        returned_json = {}
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
    sonar_result_path = configurations['cloned_projects_json_file_path']+"/sonar_health_metrics.json"
    with open(sonar_result_path, 'w') as outfile:
        json.dump(filtered_repos, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    return sonar_result_path

def read_cloned_projects(config):
    json_repos = []
    configurations = config['config']
    repos_json = configurations['cloned_projects_json_file_path']+"/cloned_repos.json"
    with open(repos_json) as data_file:
        try:
             data = json.load(data_file)
             json_repos = data
        except ValueError:
             data = []
    return json_repos

def automate_processes(config):
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    configurations = config['config']
    repos = read_cloned_projects(config)
    processed_repos = process_cloned_projects(repos)
    build_sonar_project_config(processed_repos,config)
    filtered_repos = make_sonar_api_call(processed_repos,config)
    create_result_json(filtered_repos,config)

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
