from git import Repo
import glob2
import requests
import json
import xmltodict
import os
import shutil
import configparams
import time
import logging

def collect_repositries(config):
    logging.info(time.strftime("%c")+' collecting repositories name, clone_url')
    configurations = config['config']
    client_id = configurations['github_oauth_client_id']
    client_secret = configurations['github_oauth_client_secret']
    repos = []
    orgs = configurations['public_orgs']
    for org in orgs:
        r = requests.get(configurations['public_github_api_url']+'/orgs/' + org + '/repos?client_id=' + client_id +'&client_secret=' + client_secret)
        orgs_reponsitories = json.loads(r.text)

        for org_repo in orgs_reponsitories:
            orgs_repos = {}
            projects_name_git_url = {}
            projects_name_git_url['project_name'] = org_repo['name']
            projects_name_git_url['clone_url'] = org_repo['clone_url']
            projects_name_git_url['org'] = org
            repos.append(projects_name_git_url)
    return repos

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def clone_projects(repos):
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    delete_directory(clone_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + clone_dir)
    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_dir):
            Repo.clone_from(repo['clone_url'], clone_dir)

def process_cloned_projects(repos):
    logging.info(time.strftime("%c")+' collecting pom files recursively')
    repos_pom = []
    for repo in repos:
        pom_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']+'/**/pom.xml'
        lists = glob2.glob(pom_dir)
        repo_map = {}
        if(len(lists) > 0):
            repo_map['project_name'] = repo['project_name']
            repo_map['pom_list'] = lists
            repo_map['org'] = repo['org']
            repos_pom.append(repo_map)
    return repos_pom

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

def makeEsUpdates(config,returned_responses):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    for ret in returned_responses:
        project_id = ret['returned_res']['hits']['hits'][0]['_id']
        filtered_repo_dependencies = ret['filtered']

        if 'project_dependency' in ret['returned_res']['hits']['hits'][0]['_source']:
            data_json = {"project_dependency": filtered_repo_dependencies}
            update_query = {
              "doc": data_json
            }
            ret_response = requests.post(configurations['stage_es_url']+'/projects/logs/'+project_id+'/_update', data=json.dumps(update_query))
            if project_id not in collected_ids:
                collected_ids.append(project_id)
                collected_response.append(json.loads(ret_response.text))
        else:
            ret['returned_res']['project_dependency'] = [{'dependency':'not available'}]
    return collected_response

def process_elasticSearch_update(config,results):
    logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
    if config['update'] == 'results.out':
        write_results(config['update'], results)
    else:
        res_arr = get_es_project(config,results)
        collected_response = makeEsUpdates(config,res_arr)
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
        logging.info(json.loads(response.text)['_source']['project_name'])
        if(repo['_shards']['successful'] == 1):
            repos_just_updated.append(json.loads(response.text)['_source']['project_name'])

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

def automate_processes(config):
    logging.info(time.strftime("%c")+' Started')
    repos = collect_repositries(config)
    clone_projects(repos)
    poms = process_cloned_projects(repos)
    res = parse_projects(poms)
    process_elasticSearch_update(config,res)
    cleanup_after_update()

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
