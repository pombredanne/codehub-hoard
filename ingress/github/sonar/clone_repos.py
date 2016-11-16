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
from os.path import expanduser

def collect_repositries(config):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    repos = []
    if configurations['env']  == 'PUBLIC':
        repos = get_public_repos(config)
    elif configurations['env']  == 'ENTERPRISE':
        orgs_users_ent = get_org_enterprise_repos(config) + get_users_enterprise_repos(config)
        repos = customize_ent_repo_attributes_mapping(orgs_users_ent)
    else:
        orgs_users_ent = get_org_enterprise_repos(config) + get_users_enterprise_repos(config)
        ent_repos = customize_ent_repo_attributes_mapping(orgs_users_ent)
        pub = get_public_repos(config) + get_enterprise_repos(config)
        pub_repos = customize_repo_attributes_mapping(pub)
    collected_orgs_repos = pub_repos + ent_repos
    return collected_orgs_repos

def get_public_repos(config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    orgs_public_repositories = []
    orgs = configurations['public_orgs']
    for org in orgs:
        res = requests.get(configurations['public_github_api_url']+'/orgs/' + org + '/repos?access_token='+access_token,verify=False)
        #print(configurations['public_github_api_url']+'/orgs/' + org + '/repos?access_token='+access_token)
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
    #print(orgs_enterprise_reponsitories[0])
    #print(len(orgs_enterprise_reponsitories))
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

def clone_public_projects(repos,config):
    configurations = config['config']
    access_token = configurations['public_github_access_token']
    env_home = expanduser("~")
    cloned_repos_dir = env_home + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(cloned_repos_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + cloned_repos_dir)

    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        clone_buffer = env_home + '/clonning/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_buffer):
            delete_directory(clone_dir)
            Repo.clone_from(repo['clone_url'], clone_dir+"...buffering")
            os.rename(clone_dir+"...buffering", clone_dir)

def clone_enterprise_projects(repos,config):
    configurations = config['config']
    access_token = configurations['enterprise_github_access_token']
    env_home = expanduser("~")
    cloned_repos_dir = env_home + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(cloned_repos_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + cloned_repos_dir)

    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        clone_buffer = env_home + '/clonning/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_buffer):
            print(repo['clone_url'], clone_dir+"...buffering" + "--------------bufferring")
            delete_directory(clone_dir)
            Repo.clone_from(repo['clone_url'], clone_dir+"...buffering")

            print(env_home + env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name'] + "---------clonning perm")
            os.rename(clone_dir+"...buffering", clone_dir)

def create_result_json(repos, config):
    configurations = config['config']
    #file_object = open(result_path, 'w')
    result_path = configurations['cloned_projects_json_file_path']
    result_json_dir = result_path+"/cloned_repos.json"
    with open(result_json_dir, 'w') as outfile:
        json.dump(repos, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    return result_path

def automate_processes(config):
    repos = collect_repositries(config)
    # for repo in customized:
    #     if repo['project_name'] in ['DCCPILOT','CMRA','attune','rapid-ios','Alter','Apple','CAC-P1-TEST','Catapult']:
    #         print(repo)
    #     else:
    #         clone_ready.append(repo)
    #
    # #clone_enterprise_projects(clone_ready, config)
    create_result_json(repos, config)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
