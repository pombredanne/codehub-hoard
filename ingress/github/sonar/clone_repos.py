#!/usr/bin/env python

from git import Repo
import glob2
import requests
import json
import xmltodict
import os
import shutil,pickle
import configparams,automate_sonar_dependencies,kafkaProducer
import time
import logging
from subprocess import call,check_output, run
import subprocess
from os.path import expanduser
from kafka import KafkaConsumer
from kafka import KafkaProducer
from pykafka import KafkaClient

def collect_repositries(config):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    repos = []
    temp_filtered_repos = []
    if configurations['env']  == 'PUBLIC':
        pub_repos = get_public_repos(config)
        repos = customize_repo_attributes_mapping(pub_repos)
        clone_public_projects(repos,config)
    elif configurations['env']  == 'ENTERPRISE':
        orgs_users_ent = get_org_enterprise_repos(config) + get_users_enterprise_repos(config)
        repos = customize_ent_repo_attributes_mapping(orgs_users_ent)
        clone_enterprise_projects(repos,config)
    else:
        orgs_users_ent = get_org_enterprise_repos(config) + get_users_enterprise_repos(config)
        ent_repos_customized = customize_ent_repo_attributes_mapping(orgs_users_ent)
        for repo in ent_repos_customized:
            if repo['project_name'] not in ['DCCPILOT','CMRA','attune','rapid-ios','Alter','Apple','CAC-P1-TEST','Catapult']:
                temp_filtered_repos.append(repo)
        clone_enterprise_projects(temp_filtered_repos,config)
        pub_repos = get_public_repos(config)
        pub_repos_custmoized = customize_repo_attributes_mapping(pub_repos)
        clone_public_projects(pub_repos_custmoized,config)
        repos = pub_repos_custmoized + ent_repos_customized
    return repos

def get_public_repos(config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    orgs_public_repositories = []
    orgs = configurations['public_orgs']
    for org in orgs:
        res = requests.get(configurations['public_github_api_url']+'/orgs/' + org + '/repos?access_token='+access_token,verify=False)
        orgs_public_repositories = orgs_public_repositories + json.loads(res.text)
    return orgs_public_repositories

def get_org_enterprise_repos(config):
    configurations = config['config']
    orgs_enterprise_reponsitories = []
    repos_url_list = []
    access_token = configurations['enterprise_github_access_token']
    res = requests.get(configurations['enterprise_github_api_url']+"/organizations?access_token="+access_token+'&since=0&per_page=1000',verify=False)
    res_list = json.loads(res.text)
    for repo_url in res_list:
        ret_list = requests.get(repo_url['repos_url']+"?access_token="+access_token,verify=False)
        orgs_enterprise_reponsitories = orgs_enterprise_reponsitories +  json.loads(ret_list.text)
    return orgs_enterprise_reponsitories

def get_users_enterprise_repos(config):
    configurations = config['config']
    users_enterprise_reponsitories = []
    repos_url_list = []
    access_token = configurations['enterprise_github_access_token']
    res = requests.get(configurations['enterprise_github_api_url']+"/users?access_token="+access_token+'&since=0&per_page=1000',verify=False)
    res_list = json.loads(res.text)
    for repo_url in res_list:
        ret_list = requests.get(repo_url['repos_url']+"?access_token="+access_token,verify=False)
        users_enterprise_reponsitories = users_enterprise_reponsitories +  json.loads(ret_list.text)
    return users_enterprise_reponsitories

def customize_ent_repo_attributes_mapping(orgs_reponsitories):
    repos = []
    env_home = expanduser("~")
    configurations = config['config']
    for org_repo in orgs_reponsitories:
        orgs_repos = {}
        clone_dir = env_home + '/cloned_projects/'+org_repo['owner']['login']+'/'+org_repo['name']
        projects_name_git_url = {}
        git_url = org_repo['clone_url']
        adjusted_url = git_url.replace('https://','https://natesol-code21:'+configurations['enterprise_github_access_token']+'@')
        projects_name_git_url['project_name'] = org_repo['name']
        projects_name_git_url['clone_url'] = adjusted_url
        projects_name_git_url['language'] = org_repo['language']
        projects_name_git_url['org'] = org_repo['owner']['login']
        projects_name_git_url['cloned_project_path'] = clone_dir
        repos.append(projects_name_git_url)
    return repos

def customize_repo_attributes_mapping(orgs_reponsitories):
    repos = []
    env_home = expanduser("~")
    for org_repo in orgs_reponsitories:
        orgs_repos = {}
        clone_dir = env_home + '/cloned_projects/'+org_repo['owner']['login']+'/'+org_repo['name']
        projects_name_git_url = {}
        projects_name_git_url['_id'] = str(org_repo['owner']['id'])+'_'+str(org_repo['id'])
        projects_name_git_url['project_name'] = org_repo['name']
        projects_name_git_url['clone_url'] = org_repo['clone_url']
        projects_name_git_url['language'] = org_repo['language']
        projects_name_git_url['org'] = org_repo['owner']['login']
        projects_name_git_url['cloned_project_path'] = clone_dir
        repos.append(projects_name_git_url)
    return repos

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
def setup_cloning_dir(clone_org_repo,clone_org):
    if os.path.exists(clone_org_repo):
        shutil.rmtree(clone_org_repo)
    if os.path.exists(clone_org):
        os.chdir(clone_org)
    else:
        os.makedirs(clone_org)
        os.chdir(clone_org)

def clone_public_projects(repos,config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    env_home = expanduser("~")
    cloned_repos_dir = env_home + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    logging.info(time.strftime("%c")+' cloning respositories in ' + cloned_repos_dir)

    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_org_repo = env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        clone_org = env_home + '/cloned_projects/'+repo['org']
        clone_buffer = env_home + '/clonning/'+repo['org']+'/'+repo['project_name']
        curr_dir = os.getcwd()
        print(curr_dir)
        setup_cloning_dir(clone_org_repo,clone_org)
        run(["git","clone",repo['clone_url']])
        kafkaProducer.publish_kafka_message(repo,config)


def clone_enterprise_projects(repos,config):
    configurations = config['config']
    access_token = configurations['enterprise_github_access_token']
    env_home = expanduser("~")
    cloned_repos_dir = env_home + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    logging.info(time.strftime("%c")+' cloning respositories in ' + cloned_repos_dir)

    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_org_repo = env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        clone_org = env_home + '/cloned_projects/'+repo['org']
        curr_dir = os.getcwd()
        print(curr_dir)
        setup_cloning_dir(clone_org_repo,clone_org)
        run(["git","clone",repo['clone_url']])
        kafkaProducer.publish_kafka_message(repo,config)

def automate_processes(config):
    repos = collect_repositries(config)
    print("completing cloning repos....")
    print(repos)

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
