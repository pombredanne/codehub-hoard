import json
import logging
import os
import shutil
import time

import glob2
import requests
import xmltodict
from git import Repo
import configparams,process_dependencies
from os.path import expanduser


def collect_repositories(config):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    github_access_token = configurations['public_github_access_token']
    repos = []
    orgs = configurations['public_orgs']
    for org in orgs:
        r = requests.get(configurations['public_github_api_url']+'/orgs/' + org + '/repos?access_token=' + github_access_token)
        orgs_reponsitories = json.loads(r.text)

        for org_repo in orgs_reponsitories:
            projects_name_git_url = {}
            projects_name_git_url['project_name'] = org_repo['name']
            projects_name_git_url['clone_url'] = org_repo['clone_url']
            projects_name_git_url['org'] = org
            repos.append(projects_name_git_url)
    return repos


def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def clone_projects(config, repos):
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(clone_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + clone_dir)

    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']

        if not os.path.exists(clone_dir):
            Repo.clone_from(_calculate_clone_url(config, repo['clone_url']), clone_dir)


def process_cloned_projects(repos):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repos_pom = []

    for repo in repos:
        pom_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/**/pom.xml'
        lists = glob2.glob(pom_dir)
        repo_map = {}

        if len(lists) > 0:
            repo_map['project_name'] = repo['project_name']
            repo_map['pom_list'] = lists
            repo_map['org'] = repo['org']
            repos_pom.append(repo_map)

    return repos_pom


#
# Private repos must have a username in the URL to authenticate.  We'll have this authentication in place for
# non-private repositories too so it is consistent and we can have a getting bandwidth for API calls.
#
# This method expects a URL of the form 'http://host/path' or 'https://host/path' and injects the configured
# Github Access Token like such 'http://<token>@host/path' or 'https://<token>@host/path'
#
def _calculate_clone_url(config, url):
    http_url = 'http://'
    https_url = 'https://'

    if url.find(https_url) == 0:
        return url.replace(https_url, https_url + config['config']['public_github_access_token'] + '@')
    elif url.find(http_url) == 0:
        return url.replace(http_url, http_url + config['config']['public_github_access_token'] + '@')
    else:
        raise ValueError("Unrecognized URL Protocol: %s" + url)


def parse_projects(repos_pom):
    logging.info(time.strftime("%c")+' traversing through projects')
    aggregate_results = []
    for poms in repos_pom:
        pom_files_arr = poms['pom_list']
        dependency_content = []
        dependency_map = {}
        for pom in pom_files_arr:
            parsed_json = read_pom_content(pom)
            dependency_arr = parse_aggregate(parsed_json)
            dependency_content = dependency_content + dependency_arr
        dependency_map['project_name'] = poms['project_name']
        dependency_map['org'] = poms['org']
        dependency_map['dependency_content'] = dependency_content
        aggregate_results.append(dependency_map)
    return aggregate_results

def parse_js_projects(repos_js_dep):
    logging.info(time.strftime("%c")+' traversing through js projects')
    aggregate_results = []
    for js_dep in repos_js_dep:
        js_dep_files_arr = js_dep['dep_list']
        combined_content = []
        dependency_map = {}
        for dep in js_dep_files_arr:
            parsed_json = read_js_dep_content(dep)
            dependency_arr = parse_js_aggregate(parsed_json)
            try:
                 combined_content = combined_content + dependency_arr
            except ValueError:
                 combined_content = []
            dependency_map['project_name'] = js_dep['project_name']
            dependency_map['org'] = js_dep['org']
            if len(combined_content) > 0:
                dependency_map['dependency_content'] = combined_content
                aggregate_results.append(dependency_map)
    return aggregate_results


def parse_js_aggregate(parsed_json):
    combined_result = []
    for res in parsed_json:
        for keys in res:
            data_map = {}
            data_map['groupId'] = keys
            data_map['artifactId'] = keys
            data_map['version'] = res[keys]
            combined_result.append(data_map)
    return combined_result


def process_gradle_projects(repos):
    repos_gradle = []
    for repo in repos:
        gradle_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/**/build.gradle'
        lists = glob2.glob(gradle_dir)
        repo_map = {}
        if(len(lists) > 0):
            repo_map['project_name'] = repo['project_name']
            repo_map['gradle_list'] = lists
            repo_map['org'] = repo['org']
            repos_gradle.append(repo_map)
    return repos_gradle


def process_js_projects(repos):
    repos_js = []
    for repo in repos:
        package_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/package.json'
        bower_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/bower.json'
        package_lists = glob2.glob(package_dir)
        bower_lists = glob2.glob(bower_dir)
        combined_list = list(set(package_lists).union(bower_lists))
        repo_map = {}
        if(len(combined_list) > 0):
            repo_map['project_name'] = repo['project_name']
            repo_map['dep_list'] = combined_list
            repo_map['org'] = repo['org']
            repos_js.append(repo_map)
    return repos_js


def read_js_dep_content(file_path):
    logging.info(time.strftime("%c")+' reading js dependency files content')
    json_res = []
    with open(file_path) as data_file:
        try:
             data = json.load(data_file)
             if('devDependencies' in data):
                 json_res.append(data['devDependencies'])
        except ValueError:
             data = []
    return json_res


def read_pom_content(file_path):
    logging.info(time.strftime("%c")+' reading pom files content')
    file_object = open(file_path, "r+")
    content = file_object.read()
    parsed = xmltodict.parse(content)
    parsed_json = json.loads(json.dumps(parsed))['project']
    return parsed_json


def parse_aggregate(parsed_json):
    logging.info(time.strftime("%c")+ ' parsing and aggregating pom files')
    content_array = []
    if('dependencies' in parsed_json):
        if('dependency' in parsed_json['dependencies']):
            result = parsed_json['dependencies']['dependency']
            if(type(result) is dict):
                content_array.append(result)
            elif(type(result) is list):
                for res in result:
                    content_array.append(res)

    elif('dependencyManagement' in parsed_json):
        if('dependency' in parsed_json['dependencyManagement']['dependencies']):
            result = parsed_json['dependencyManagement']['dependencies']['dependency']
            if(type(result) is dict):
                content_array.append(result)
            elif(type(result) is list):
                for res in result:
                    content_array.append(res)

    elif((parsed_json.get('dependencies') is None) or (parsed_json.get('dependencies') == "")):
        content = { "content": "NA"}
        content_array.append(content)
    return content_array

def create_result_json(results, result_path):
    file_object = open(result_path, 'w')
    with open(result_path, 'w') as outfile:
        json.dump(results, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    return result_path

def cleanup_after_update():
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' cleaning up cloned projects after elasticsearch updates or written to a file')
    delete_directory(clone_dir)

def get_final_results(config):
    configurations = config['config']
    repos = collect_repositories(config)
    if(configurations['clone']):
        cleanup_after_update()
        clone_projects(config, repos)
    poms = process_cloned_projects(repos)
    res = parse_projects(poms)
    js_res = process_js_projects(repos)
    js_ret_res = parse_js_projects(js_res)
    combined_results = res + js_ret_res
    print(combined_results)
    return combined_results

def automate_processes(config):
    logging.info(time.strftime("%c")+' Started')
    home_dir = expanduser("~")
    res_dir = home_dir+"/analysis_outputs/dependency_results.out"
    combined_results = determine_results(config)
    create_result_json(combined_results,res_dir)
    #process_dependencies._process_elasticsearch_update(config,combined_results)
    #cleanup_after_update()


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    get_final_results(config)
