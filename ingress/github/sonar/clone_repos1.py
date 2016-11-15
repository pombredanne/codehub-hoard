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
        repos = get_enterprise_repos(config)
    else:
        repos = get_public_repos(config) + get_enterprise_repos(config)
    collected_orgs_repos = customize_repo_attributes_mapping(repos)
    return collected_orgs_repos

def _process_enterprise_orgs_users(config):
    org_results = _get_enterprise_orgs(config)

    user_results = _get_enterprise_users(config)

    #ingest_logger.info('Total Orgs (Organizations and Users) Processed: %s', org_results['count'] + user_results['count'])
    #ingest_logger.info('Total Repos Processed: %s', len(org_results) + len(user_results))

    total_results = org_results['results']
    print(total_results)
    total_results.extend(user_results['results'])

    return total_results


def _get_enterprise_orgs(config):
    configurations = config['config']
    url = configurations['enterprise_github_api_url'] + '/organizations?access_token=' + configurations['enterprise_github_access_token'] + '&since=0&per_page=100'

    results = []
    orgs_count = 0
    while True:
        orgs_response = requests.get(url,verify=False)
        orgs = json.loads(orgs_response.text)
        if not orgs:
            break

        orgs_count += len(orgs)
        results.append(orgs)

        # is there another page to pull?
        if 'next' not in orgs_response.links:
            break

        url = orgs_response.links['next']['url']

    return {"results": results, "count": orgs_count}


def _get_enterprise_users(config):
    configurations = config['config']
    url = configurations['enterprise_github_api_url'] + '/users?access_token=' + configurations['enterprise_github_access_token'] + '&since=0&per_page=100'
    results = []
    users_count = 0

    while True:
        filtered_users = []
        users_response = requests.get(url,verify=False)
        users = json.loads(users_response.text)

        if not users:
            break

        # filter Organizations since we've already handled that elsewhere
        for user in users:
            if user['type'] == 'User':
                filtered_users.append(user)

        users_count += len(filtered_users)
        results.append(filtered_users)

        # is there another page to pull?
        if 'next' not in users_response.links:
            break

        url = users_response.links['next']['url']

    return {"results": results, "count": users_count}

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

def get_enterprise_repos(config):
    configurations = config['config']
    orgs_enterprise_reponsitories = []
    repos_url_list = []
    access_token = configurations['enterprise_github_access_token']
    res = requests.get(configurations['enterprise_github_api_url']+"?access_token="+access_token+'&since=0&per_page=1000',verify=False)
    res_list = json.loads(res.text)
    for repo_url in res_list:
        ret_list = requests.get(repo_url['repos_url']+"?access_token="+access_token,verify=False)
        orgs_enterprise_reponsitories = orgs_enterprise_reponsitories +  json.loads(ret_list.text)
    #print(orgs_enterprise_reponsitories[0])
    #print(len(orgs_enterprise_reponsitories))
    return orgs_enterprise_reponsitories

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
    #print(users_enterprise_reponsitories[0])
    #print(len(users_enterprise_reponsitories))
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
        #index = git_url.find("https://")
        #adjusted_url = git_url[:index]+"natesol-code21:"+configurations['enterprise_github_access_token']+'@'+git_url[index:]
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
            print(repo['clone_url'], clone_dir+"...buffering" + "--------------bufferring")
            delete_directory(clone_dir)
            Repo.clone_from(repo['clone_url'], clone_dir+"...buffering")
            print(env_home + env_home + '/cloned_projects/'+repo['org']+'/'+repo['project_name'] + "---------clonning perm")
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
    #repos = collect_repositries(config)
    #print(repos)
    #_process_enterprise_orgs_users(config)
    #len(_process_enterprise_orgs_users(config))
    #clone_public_projects(repos,config)
    #create_result_json(repos, config)
    orgs_users_ent = get_org_enterprise_repos(config) + get_users_enterprise_repos(config)
    customized = customize_ent_repo_attributes_mapping(orgs_users_ent)
    clone_ready = []
    for repo in customized:
        if repo['project_name'] in ['DCCPILOT','CMRA','attune','rapid-ios','Alter','Apple','CAC-P1-TEST','Catapult']:
            print(repo)
        else:
            clone_ready.append(repo)

    #clone_enterprise_projects(clone_ready, config)
    create_result_json(clone_ready, config)
    #print(customized)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
