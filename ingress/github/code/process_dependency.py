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

def process_java_projects(repos,config):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repos_pom = []
    configurations = config['config']
    for repo in repos:
        if('cloned_project_path' in repo):
            pom_dir = repo['cloned_project_path']+'/**/pom.xml'
            lists = glob2.glob(pom_dir)
            repo_map = {}
            repo_map['project_name'] = repo['project_name']
            repo_map['pom_list'] = lists
            repo_map['org'] = repo['org']
            repo_map['language'] = repo['language']
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


def parse_java_projects(repos_pom):
    logging.info(time.strftime("%c")+' traversing through projects')
    aggregate_results = []
    for repo in repos_pom:
        if('language' in repo):
            if(repo['language'] == 'Java'):
                pom_files_arr = repo['pom_list']
                dependency_content = []
                dependency_map = {}
                for pom in pom_files_arr:
                    parsed_json = read_pom_content(pom)
                    dependency_arr = parse_aggregate(parsed_json)
                    dependency_content = dependency_content + dependency_arr
                dependency_map['project_name'] = repo['project_name']
                dependency_map['language'] = repo['language']
                dependency_map['org'] = repo['org']
                dependency_map['dependency_content'] = dependency_content
                aggregate_results.append(dependency_map)
    return aggregate_results

def parse_js_projects(repos_js_dep):
    logging.info(time.strftime("%c")+' traversing through js projects')
    aggregate_results = []
    for repo in repos_js_dep:
        if('language' in repo):
            if(repo['language'] == 'JavaScript'):
                js_dep_files_arr = repo['dep_list']
                combined_content = []
                dependency_map = {}
                for dep in js_dep_files_arr:
                    parsed_json = read_js_dep_content(dep)
                    dependency_arr = parse_js_aggregate(parsed_json)
                    try:
                         combined_content = combined_content + dependency_arr
                    except ValueError:
                         combined_content = []
                    dependency_map['project_name'] = repo['project_name']
                    dependency_map['language'] = repo['language']
                    dependency_map['org'] = repo['org']
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
            repo_map['language'] = repo['language']
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
    if config['update'] == 'results.out':
        logging.info(time.strftime("%c")+' Writing the result data to a local file results.out')
        write_results(config['update'], results)
    else:
        logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
        res_arr = get_es_project(config,results)
        collected_response = _make_elasticsearch_updates(config, res_arr)
        display_stats(config, collected_response)


def write_results(resultfile,results):
    file_object = open(resultfile, 'w')
    file_object.write("\t******************** The following Projects have dependencies ********************************\n\n")
    for res in results:
        file_object.write(json.dumps(res))
        file_object.write("\n")


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


def cleanup_after_update():
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' cleaning up cloned projects after elasticsearch updates or written to a file')
    delete_directory(clone_dir)

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
def create_result_json(processed_repos, config):
    configurations = config['config']
    dependencies_result_path = configurations['cloned_projects_json_file_path']+"/project_dependencies.json"
    with open(dependencies_result_path, 'w') as outfile:
        json.dump(processed_repos, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    return dependencies_result_path

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
    repos = read_cloned_projects(config)
    processed_java_repos = process_java_projects(repos,config)
    java_dependency_res = parse_java_projects(processed_java_repos)
    processed_js_repos = process_js_projects(repos)
    js_dependency_res = parse_js_projects(processed_js_repos)
    combined_results = java_dependency_res + js_dependency_res
    create_result_json(combined_results, config)
    processed_combined_results = read_processed_projects(config)
    print(combined_results)
    #_process_elasticsearch_update(config,combined_results)
    #cleanup_after_update()


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
