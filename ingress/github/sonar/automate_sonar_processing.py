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
            projects_name_git_url['language'] = org_repo['language']
            projects_name_git_url['org'] = org
            repos.append(projects_name_git_url)
    return repos

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def clone_projects(repos):
    clone_dir = os.getcwd() + '/cloned_projects/'
    logging.info(time.strftime("%c")+' removing repositories if already exists')
    #delete_directory(clone_dir)
    logging.info(time.strftime("%c")+' cloning respositories in ' + clone_dir)
    for repo in repos:
        logging.info(time.strftime("%c")+' cloning ' + repo['project_name'] + ' repo of '+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_dir):
            Repo.clone_from(repo['clone_url'], clone_dir)

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
    exclusions = 'system/**, test/**, /img/**, /logs/**, /fonts/**, **/generated-sources/**, **/packages/**, **/docs/**, **/node_modules/**, **/bower_components/**,**/dist/**,**/unity.js,**/bootstrap.css, **/*.rb'
    for src in repo['src_list']:
        aggregated_src = src + "," + aggregated_src
    file_object = open(repo['root_dir']+"/sonar-project.properties", 'w')
    file_object.write("sonar.projectKey="+repo['project_name'])
    file_object.write("\n")
    file_object.write("sonar.projectName="+repo['project_name']+" To be analyzed")
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
    call(["ls","-l"])
    run(runner_dir,check=True)
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
            collected_response['metrics'] = res['metrics']
            collected_response['returned_res'] = returned_res
            returned_responses_collection.append(collected_response)
    return returned_responses_collection

def makeEsUpdates(config,returned_responses):
    collected_ids = []
    collected_response = []
    configurations = config['config']
    for ret in returned_responses:
        project_id = ret['returned_res']['hits']['hits'][0]['_id']
        filtered_health_metrics = ret['metrics']

        if len(filtered_health_metrics) > 0:
            data_json = {"project_health_metrics": filtered_health_metrics}
            update_query = {
              "doc": data_json
            }
            ret_response = requests.post(configurations['stage_es_url']+'/projects/logs/'+project_id+'/_update', data=json.dumps(update_query))
            if project_id not in collected_ids:
                collected_ids.append(project_id)
                collected_response.append(json.loads(ret_response.text))
    return collected_response


def process_elasticSearch_update(results, config):
    if config['update'] == 'results.out':
        logging.info(time.strftime("%c")+' Writing the result data to a local file results.out')
        write_results(config['update'], results)
    else:
        logging.info(time.strftime("%c")+' talking to ES and adding project depedency attribute with processed data')
        res_arr = get_es_project(config,results)
        collected_response = makeEsUpdates(config,res_arr)
        display_stats(config, collected_response)

def write_results(resultfile,results):
    file_object = open(os.getcwd()+"/"+resultfile, 'w')
    file_object.write("\t******************** The following Projects have dependencies ********************************\n\n")
    for res in results:
        file_object.write(json.dumps(res))
        file_object.write("\n")

def display_stats(config, response_arr):
    logging.info(time.strftime("%c")+" ******The following "+str(len(response_arr)) + " projects have health metrics ******")
    repos_just_updated = []
    configurations = config['config']
    for repo in response_arr:
        response = requests.get(configurations['stage_es_url']+'/projects/logs/'+repo['_id'])
        logging.info(json.loads(response.text))
        if(repo['_shards']['successful'] == 1):
            repos_just_updated.append(json.loads(response.text))

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
    sonar_dir = os.getcwd()+"/**/sonar-runner"
    repos = collect_repositries(config)
    clone_projects(repos)
    processed_repos = process_cloned_projects(repos)
    build_sonar_project_config(processed_repos,config)

    filtered_repo = make_sonar_api_call(processed_repos,config)
    process_elasticSearch_update(filtered_repo, config)
    cleanup_after_update()

if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
