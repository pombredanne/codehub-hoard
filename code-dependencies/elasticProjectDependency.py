from git import Repo
import glob2
import requests
import json
import xmltodict
import os
from collections import defaultdict
import shutil

def authenticate_github():
    print("...collecting github credentials")
    credentials = {}
    with open('github_auth.txt', 'r') as myfile:
        client_id=myfile.readline().replace('\n', '')
        client_secret=myfile.readline()
        credentials['client_id'] = client_id
        credentials['client_secret'] = client_secret
    return credentials


def collect_repositries(orgs):
    print("...collecting repositories name, clone_url")
    credentials = authenticate_github()
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    repos = []
    for org in orgs:
        r = requests.get('https://api.github.com/orgs/' + org + '/repos?client_id=' + client_id +'&client_secret=' + client_secret)
        orgs_reponsitories = json.loads(r.text)

        for org_repo in orgs_reponsitories:
            orgs_repos = {}
            projects_name_git_url = {}
            projects_name_git_url['project_name'] = org_repo['name']
            projects_name_git_url['clone_url'] = org_repo['clone_url']
            projects_name_git_url['org'] = org
            repos.append(projects_name_git_url)
    return repos

def deleteDirectory(path):
    print("...removing repositories if already exists")
    if os.path.exists(path):
        shutil.rmtree(path)

def clone_projects(repos):
    clone_dir = os.getcwd() + '/cloned_projects/'
    deleteDirectory(clone_dir)
    print("...cloning respositories in " + clone_dir)
    for repo in repos:
        print("...cloning " + repo['project_name'] + " repo of "+ repo['org'])
        clone_dir = os.getcwd() + '/cloned_projects/'+repo['org']+'/'+repo['project_name']
        if not os.path.exists(clone_dir):
            Repo.clone_from(repo['clone_url'], clone_dir)

def process_cloned_projects(repos):
    print("...collecting pom files recursively")
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
    print("...traversing through projects")
    aggregate_results = []
    for poms in repos_pom:
        pom_files_arr = poms['pom_list']
        dependency_content = []
        dependency_map = {}
        for pom in pom_files_arr:
            parsed_json = readPomFileContent(pom)
            dependency_arr = parseAndAggregate(parsed_json)
            dependency_content = dependency_content + dependency_arr
        dependency_map['project_name'] = poms['project_name']
        dependency_map['org'] = poms['org']
        dependency_map['dependency_content'] = dependency_content
        aggregate_results.append(dependency_map)
    return aggregate_results


def readPomFileContent(filePath):
    print("...reading pom files content")
    file_object = open(filePath, "r+")
    content = file_object.read()
    parsed = xmltodict.parse(content)
    parsed_json = json.loads(json.dumps(parsed))['project']
    return parsed_json

def parseAndAggregate(parsed_json):
    print("...parsing and aggregating pom files")
    content_array = []
    if('dependencies' in parsed_json):
        if('dependency' in parsed_json['dependencies']):
            result = parsed_json['dependencies']['dependency']
            if(type(result) is dict):
                content_array.append(result)
            if(type(result) is list):
                for res in result:
                    content_array.append(res)

    if('dependencyManagement' in parsed_json):
        if('dependency' in parsed_json['dependencyManagement']['dependencies']):
            result = parsed_json['dependencyManagement']['dependencies']['dependency']
            if(type(result) is dict):
                content_array.append(result)
            if(type(result) is list):
                for res in result:
                    content_array.append(res)

    if((parsed_json.get('dependencies') is None) or (parsed_json.get('dependencies') == "")):
        content = { "content": "NA"}
        content_array.append(content)
    return content_array

def updateElasticSearch(results):
    print("...talking to ES and adding project depedency attribute with processed data")
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
        response = requests.get('http://127.0.0.1:9200/projects/logs/_search', data=json.dumps(query_data))
        returned_res = json.loads(response.text)
        project_id = returned_res['hits']['hits'][0]['_id']
        if res['dependency_content'] is None:
            res['dependency_content'] = [{'dependency':'not available'}]
        if res['dependency_content'] is not None:
            data_json = {"project_dependency": res['dependency_content']}
            update_query = {
              "doc": data_json
            }
            ret_response = requests.post('http://127.0.0.1:9200/projects/logs/'+project_id+'/_update', data=json.dumps(update_query))
            if(json.loads(ret_response.text)['_shards']['successful'] == 1):
                print(json.loads(ret_response.text))


def automate_processes():
    print("...starting")
    orgs = ["boozallen", "booz-allen-hamilton", "netflix", "elastic", "nodejs", "durandalproject", "jquery", "spring-projects", "18F"]
    #orgs = ["boozallen","booz-allen-hamilton"]
    repos = collect_repositries(orgs)
    clone_projects(repos)
    poms = process_cloned_projects(repos)
    res = parse_projects(poms)
    updateElasticSearch(res)


if __name__ == "__main__":
    automate_processes()
