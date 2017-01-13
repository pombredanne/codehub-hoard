#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json
import xmltodict
import shutil
import automate_sonar_dependencies
import time
import logging
from subprocess import call,check_output
import subprocess
import os, sys,signal
sys.path.append(os.path.abspath("../config"))
import configparams

def collect_repositries(config):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    repos = []
    if configurations['env']  == 'PUBLIC':
        repos = get_public_repos(config)
    elif configurations['env']  == 'ENTERPRISE':
        repos = get_enterprise_repos(config)
    else:
        repos = get_public_repos(config) + get_enterprise_repos(config)
    collected_orgs_repos = customize_repo_attributes_mapping(repos)
    return collected_orgs_repos

def get_public_repos(config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    orgs_public_repositories = []
    orgs = configurations['public_orgs']
    for org in orgs:
        res = requests.get(configurations['public_github_api_url']+'/orgs/' + org + '/repos?access_token='+access_token,verify=False)
        orgs_public_repositories = orgs_public_repositories + json.loads(res.text)
    return orgs_public_repositories

def get_enterprise_repos(config):
    configurations = config['config']
    orgs_enterprise_reponsitories = []
    repos_url_list = []
    access_token = configurations['enterprise_github_access_token']
    res = requests.get(configurations['enterprise_github_api_url']+"?access_token="+access_token,verify=False)
    res_list = json.loads(res.text)
    for repo_url in res_list:
        ret_list = requests.get(repo_url['repos_url']+"?access_token="+access_token,verify=False)
        orgs_enterprise_reponsitories = orgs_enterprise_reponsitories +  json.loads(ret_list.text)
    return orgs_enterprise_reponsitories

def customize_repo_attributes_mapping(orgs_reponsitories):
    repos = []
    for org_repo in orgs_reponsitories:
        orgs_repos = {}
        projects_name_git_url = {}
        projects_name_git_url['project_name'] = org_repo['name']
        projects_name_git_url['clone_url'] = org_repo['clone_url']
        projects_name_git_url['language'] = org_repo['language']
        projects_name_git_url['org'] = org_repo['owner']['login']
        repos.append(projects_name_git_url)
    return repos

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def clone_public_projects(repos,config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(clone_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + clone_dir)
    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_dir):
            Repo.clone_from(repo['clone_url'], clone_dir)

def clone_enterprise_projects(repos,config):
    configurations = config['config']
    access_token = configurations['enterprise_github_access_token']
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(clone_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + clone_dir)
    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_dir):
            Repo.clone_from(repo['clone_url'], clone_dir,env={'GIT_SSL_NO_VERIFY': '1'}, username='mohseni-yahya')
def process_cloned_projects(repos):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repos_src = []

    for repo in repos:
        src_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/*/'
        lists = glob2.glob(src_dir)
        repo_map = {}
        if(len(lists) > 0):
            repo_map['project_name'] = repo['project_name']
            repo_map['src_list'] = lists
            repo_map['org'] = repo['org']
            repo_map['language'] = repo['language']
            repo_map['root_dir'] = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
            repos_src.append(repo_map)
    return repos_src

def build_sonar_project_config(repos_src,config):
    unavailable_pligins = config['config']['unavailable_pligins']
    runner_dir = automate_sonar_dependencies.install_sonar_runner_dependencies(config)
    for repo in repos_src:
        if repo['language'] is not None:
            if repo['language'].lower() not in unavailable_pligins:
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
    file_object.write("sonar.language="+adjust_language_naming(repo['language']))
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


def adjust_language_naming(repo_language):
    lang = ''
    if repo_language:
        if(repo_language.lower() == 'javascript'):
            lang = 'js'
        elif(repo_language.lower() == 'java'):
            lang = 'java'
        elif(repo_language.lower() == 'css'):
            lang = 'css'
        elif(repo_language.lower() == 'python'):
            lang = 'py'
        elif(repo_language.lower() == 'coffeescript'):
            lang = 'js'
        elif(repo_language.lower() == 'html'):
            lang = 'web'
        elif(repo_language.lower() == 'groovy'):
            lang = 'grvy'
        elif(repo_language.lower() == 'c#'):
            lang = 'cs'
        elif(repo_language.lower() == 'objective-c'):
            lang = 'objc'
        elif(repo_language.lower() == 'c'):
            lang = 'c'
        elif(repo_language.lower() == 'php'):
            lang = 'php'
        elif(repo_language.lower() == 'c++'):
            lang = 'cxx'
        else:
            lang = repo_language.lower()
    return lang

def create_result_json(filtered_repo, result_path):
    file_object = open(result_path, 'w')
    with open(result_path, 'w') as outfile:
        json.dump(filtered_repo, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    return result_path

def handle_pub_ent_result_json(config,filtered_repo):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    repos = []
    if configurations['env']  == 'PUBLIC':
        res_pub_dir = os.getcwd()+"/metric_pub_result.json"
        create_result_json(filtered_repo,res_pub_dir)
    elif configurations['env']  == 'ENTERPRISE':
        res_ent_dir = os.getcwd()+"/metric_ent_result.json"
        create_result_json(filtered_repo,res_ent_dir)
    else:
        res_dir = os.getcwd()+"/metric_result.json"
        create_result_json(filtered_repo,res_dir)

def automate_processes(config):
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    repos = collect_repositries(config)
    clone_public_projects(repos,config)
    clone_enterprise_projects(repos,config)
    processed_repos = process_cloned_projects(repos)
    build_sonar_project_config(processed_repos,config)
    filtered_repo = make_sonar_api_call(processed_repos,config)
    os.chdir("..")
    handle_pub_ent_result_json(config,filtered_repo)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
