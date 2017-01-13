#!/usr/bin/env python

import json
import logging
import shutil
import time

import glob2
import requests
import xmltodict
from git import Repo
import os, sys,signal
sys.path.append(os.path.abspath("../config"))
import configparams

def process_java_projects(repo,config):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repo_map = {}
    configurations = config['config']
    print(repo)
    if('cloned_project_path' in repo):
        pom_dir = repo['cloned_project_path']+'/**/pom.xml'
        lists = glob2.glob(pom_dir)
        repo_map['_id'] = repo['_id']
        repo_map['project_name'] = repo['project_name']
        repo_map['pom_list'] = lists
        repo_map['org'] = repo['org']
        repo_map['language'] = repo['language']
    return repo_map
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


def parse_java_projects(repo_pom):
    logging.info(time.strftime("%c")+' traversing through projects')
    aggregate_results = []
    if 'pom_list' in repo_pom:
        pom_files_arr = repo_pom['pom_list']
        dependency_content = []
        dependency_map = {}
        for pom in pom_files_arr:
            parsed_json = read_pom_content(pom)
            dependency_arr = parse_jave_aggregate(parsed_json)
            dependency_content = dependency_content + dependency_arr
            dependency_map['_id'] = repo_pom['_id']
            dependency_map['project_name'] = repo_pom['project_name']
            dependency_map['language'] = repo_pom['language']
            dependency_map['org'] = repo_pom['org']
            dependency_map['dependency_content'] = dependency_content
            aggregate_results.append(dependency_map)
    return aggregate_results

def parse_js_projects(repos_js_dep):
    logging.info(time.strftime("%c")+' traversing through js projects')
    aggregate_results = []
    if 'dep_list' in repos_js_dep:
        js_dep_files_arr = repos_js_dep['dep_list']
        combined_content = []
        dependency_map = {}
        for dep in js_dep_files_arr:
            parsed_json = read_js_dep_content(dep)
            dependency_arr = parse_js_aggregate(parsed_json)
            try:
                 combined_content = combined_content + dependency_arr
            except ValueError:
                 combined_content = []
            dependency_map['_id'] = repos_js_dep['_id']
            dependency_map['project_name'] = repos_js_dep['project_name']
            dependency_map['language'] = repos_js_dep['language']
            dependency_map['org'] = repos_js_dep['org']
            if len(combined_content) > 0:
                dependency_map['dependency_content'] = combined_content
                aggregate_results.append(dependency_map)
        return aggregate_results


def parse_js_aggregate(parsed_json):
    combined_result = []
    for dep in parsed_json:
        for keys in dep:
            data_map = {}
            data_map['groupId'] = keys
            data_map['artifactId'] = keys
            data_map['version'] = dep[keys]
            combined_result.append(data_map)
    print(combined_result)
    return combined_result


def process_gradle_projects(repo):
    repos_gradle = []
    gradle_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/**/build.gradle'
    lists = glob2.glob(gradle_dir)
    repo_map = {}
    if(len(lists) > 0):
        repo_map['project_name'] = repo['project_name']
        repo_map['gradle_list'] = lists
        repo_map['org'] = repo['org']
        repos_gradle.append(repo_map)
    return repos_gradle


def process_js_projects(repo,config):
    if('cloned_project_path' in repo):
        package_dir = repo['cloned_project_path']+'/package.json'
        bower_dir = repo['cloned_project_path']+'/bower.json'
        package_lists = glob2.glob(package_dir)
        bower_lists = glob2.glob(bower_dir)
        combined_list = list(set(package_lists).union(bower_lists))
        repo_map = {}
        if(len(combined_list) > 0):
            repo_map['_id'] = repo['_id']
            repo_map['project_name'] = repo['project_name']
            repo_map['dep_list'] = combined_list
            repo_map['org'] = repo['org']
            repo_map['language'] = repo['language']
        return repo_map


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


def parse_jave_aggregate(parsed_json):
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


def filter_dependencies(repo):
    filtered_dependency = []
    for filter in repo['dependency_content']:
        if not 'content' in filter:
            filtered_dependency.append(filter)
    return filtered_dependency

def automate_processes(config, repo):
    logging.info(time.strftime("%c")+' Started')
    combined_results = []
    if 'language' in repo:
        if repo['language'] == 'Java':
            processed_java_repo = process_java_projects(repo,config)
            print(processed_java_repo)
            if processed_java_repo is not None:
                java_dependency_res = parse_java_projects(processed_java_repo)
                if java_dependency_res is not None:
                    combined_results = combined_results + java_dependency_res
        if repo['language'] == 'JavaScript':
            processed_js_repo = process_js_projects(repo,config)
            print(processed_js_repo)
            if processed_js_repo is not None:
                js_dependency_res = parse_js_projects(processed_js_repo)
                if js_dependency_res is not None:
                    combined_results = combined_results + js_dependency_res
                    print(js_dependency_res)
        else:
            pass
    repo['dependency_content'] = combined_results
    return repo



if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config,repo)
