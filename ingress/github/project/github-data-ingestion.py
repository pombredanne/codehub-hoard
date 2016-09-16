import argparse
import base64
import json
import logging
from re import sub

import requests


ingest_logger = logging.getLogger('github-data-ingestion')

#
# The main workhorse that pulls the data and creates the data document from it.
#
#   Parameters
#   ----------
#   config : dictionary
#            Holds all the configurations for this program to run
#   orgs : list
#          Names of organizations or users which for Github are all Users by either of Type=User or Type=Organization
#
def _ingest_repo_data(config, orgs):
    repos_result = []
    # TODO: Repo level but until we address this correctly pulling it out
    num_releases = 0

    for org in orgs:
        repos_response = requests.get(org['repos_url'] + '?' + _get_auth_http_params(config))
        repos = json.loads(repos_response.text)
        ingest_logger.info(repos)

        org_name = org['login']
        org_url = org['html_url']
        org_type = org['type']
        org_avatar_url = org['avatar_url']

        for repo in repos:
            repo_info = {}

            contributors = _get_contributors_info(config, org, repo['name'])
            readme_results = _get_readme_info(config, org, repo['name'])
            watchers = _calculate_watchers(config, org, repo['name'])

            repo_info['origin'] = config['env']
            repo_info['repository'] = repo['name']
            repo_info['repository_url'] = repo['html_url']
            repo_info['full_name'] = repo['full_name']
            repo_info['project_name'] = repo['name']

            repo_info['organization'] = org_name
            repo_info['organization_url'] = org_url
            repo_info['org_avatar_url'] = org_avatar_url
            repo_info['org_type'] = org_type

            # x languages_url
            # x subscribers_url
            # org description # need to restructure code to go at Orgs and Users separately
            # x avatar_url for Org and Contributor
            # x use full_name instead of constructing it
            # x type
            # updated_at or created_at for org
            # x updated_at for repo
            # x remove duplicate entry for repository and project_name
            # x add repo origin (public or enterprise)

            repo_info['project_description'] = repo['description']
            repo_info['language'] = repo['language']
            repo_info['languages'] = _get_repo_languages(config, org, repo['name'])
            repo_info['stars'] = repo['stargazers_count']
            repo_info['watchers'] = watchers
            repo_info['contributors'] = contributors['num_contributors']
            repo_info['commits'] = contributors['num_commits']
            repo_info['releases'] = num_releases
            repo_info['forks'] = repo['forks']
            repo_info['rank'] = _calculate_popular_rank(repo, watchers, contributors)
            repo_info['content'] = readme_results['readme_contents']
            repo_info['readme_url'] = readme_results['readme_url']
            repo_info['contributors_list'] = contributors['contributors']
            repo_info['updated_at'] = repo['updated_at']
            repo_info['suggest'] = _get_suggest_info(repo['name'], repo['description'])

            repos_result.append(repo_info)

    return repos_result


def _calculate_popular_rank(repo, watchers, contributors):
    return (repo['stargazers_count']*3) + (watchers*4) + (contributors['num_contributors']*5) + (contributors['num_commits'])


def _process_enterprise_orgs_users(config):
    url = _get_github_url(config) + '/users?' + _get_auth_http_params(config) + '&since=0&per_page=100'

    results = []
    orgs_cnt = 0
    while True:
        orgs_response = requests.get(url)
        orgs = json.loads(orgs_response.text)
        if not orgs:
            break

        orgs_cnt += len(orgs)
        results.extend(_ingest_repo_data(config, orgs))

        # is there another page to pull?
        if 'next' not in orgs_response.links:
            break

        url = orgs_response.links['next']['url']

    ingest_logger.info('Total Orgs (Organizations and Users) Processed: %s', orgs_cnt)
    ingest_logger.info('Total Repos Processed: %s', len(results))

    return results


def _process_public_orgs(config):
    orgs = _get_public_orgs(config)

    results = _ingest_repo_data(config, orgs)

    ingest_logger.info('Total Orgs (Organizations and Users) Processed: %s', len(orgs))
    ingest_logger.info('Total Repos Processed: %s', len(results))

    return results


def _get_public_orgs(config):
    orgs_json = []
    for org in config['public_orgs']:
        orgs_response = requests.get(_get_github_url(config) + '/users/' + org + '?' + _get_auth_http_params(config))
        orgs_json.append(json.loads(orgs_response.text))

    ingest_logger.info(orgs_json)
    return orgs_json


#G
# The access method for github is different for each system.  Both modes should be accepted soon.
#
# If Enterprise then we use the Personal Access Token otherwise an OAuth token pair.
#
def _get_auth_http_params(config):
    if config['env'] == 'ENTERPRISE':
        return 'access_token=' + config['enterprise_github_access_token']
    else:
        return 'access_token=' + config['public_github_access_token']


#
# The API URL for each system differs and this method returns the correct one as determined by the env property.
#
def _get_github_url(config):
    if config['env'] == 'ENTERPRISE':
        return config['enterprise_github_api_url']
    else:
        return config['public_github_api_url']


def _get_repo_languages(config, org, repo_name):
    url = _get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name + '/languages?' +\
          _get_auth_http_params(config)

    languages_response = requests.get(url)
    if languages_response == '':
        return {}

    return json.loads(languages_response.text)

#
# Calculate:
#   Total Commits (summation from all contributors)
#   Total Contributors (including anonymous) see: https://developer.github.com/v3/repos/#list-contributors
#   List of Contributors
#
def _get_contributors_info(config, org, repo_name):
    url = _get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name +\
          '/contributors?since=0&per_page=100&anon=true&' + _get_auth_http_params(config)

    num_commits = 0
    contributor_list = []

    while True:
        contributors_response = requests.get(url)

        # Something is always returned. 'None' and 'not' pass through but
        # testing for empty prevents downstream errors.
        if contributors_response.text == '':
            break

        contributors = json.loads(contributors_response.text)

        if not contributors:
            break

        for contributor in contributors:
            num_commits += contributor['contributions']
            if contributor['type'] == 'User':
                contributor_list.append({'username': contributor['login'],
                                         'profile_url': contributor['html_url'],
                                         'avatar_url': contributor['avatar_url'],
                                         'user_type': contributor['type']})
            else:
                contributor_list.append({'username': contributor['name'],
                                         'profile_url': None,
                                         'avatar_url': None,
                                         'user_type': contributor['type']})

        # is there another page to pull?
        if 'next' not in contributors_response.links:
            break

        url = contributors_response.links['next']['url']

    return {'num_commits': num_commits, 'num_contributors': len(contributor_list), 'contributors': contributor_list}


#
# Calculate:
#   Total Subscribers = Total Watchers
#
def _calculate_watchers(config, org, repo_name):
    url = _get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name + \
          '/subscribers?since=0&per_page=100&' + _get_auth_http_params(config)

    total_watchers = 0

    while True:
        watchers_response = requests.get(url)

        # Something is always returned. 'None' and 'not' pass through but
        # testing for empty prevents downstream errors.
        if watchers_response.text == '':
            break

        watchers = json.loads(watchers_response.text)

        if not watchers:
            break

        total_watchers += len(watchers)

        # is there another page to pull?
        if 'next' not in watchers_response.links:
            break

        url = watchers_response.links['next']['url']

    return total_watchers

#
# Process README content and url
#
def _get_readme_info(config, org, repo_name):
    readme_response = requests.get(_get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name +
                                   '/contents/README.md?' + _get_auth_http_params(config))
    readme_response = json.loads(readme_response.text)
    readme_results = {'readme_contents': '', 'readme_url': ''}

    if 'documentation_url' not in readme_response:
        readme_results['readme_contents'] = base64.b64decode(readme_response['content'])
        readme_results['readme_url'] = readme_response['download_url']

    return readme_results


def _get_suggest_info(repo_name, repo_desc):
    _repo_name = repo_name if repo_name is not None else ''
    _repo_desc = repo_desc if repo_desc is not None else ''

    suggest = '{"input": ["' + sub("[^a-zA-Z0-9\s]", '', _repo_name) + '", "' + \
              sub("[^a-zA-Z0-9\s]", '', _repo_desc) + '"], "output": "' + \
              sub("[^a-zA-Z0-9-\s]", '', _repo_name) + '"}'
    return json.loads(suggest)


def _write_data_to_file(config, data):
    with open(config['data_output_file'], "w") as outfile:
        json.dump(data, outfile, indent=4)


#
# Process the commandline arguments and the configuration file to create a full configuration object for the program.
#
def _read_config(args):
    config_filename = 'ingest.conf'
    config = {}

    if args.config is not None:
        config_filename = args.config

    ingest_logger.info('Reading configuration file (' + config_filename + ') ...')

    with open(config_filename, 'r') as config_file:
        for line in config_file.read().splitlines():
            if not line.startswith('#'):
                prop = line.split('=')
                if len(prop) == 2:
                    config[prop[0].strip()] = prop[1].strip()

    if args.env is not None:
        config['env'] = args.env.upper()
    else:
        config['env'] = 'PUBLIC'

    _convert_public_orgs(config)

    return config


#
# Format org list by removing all whitespace and converting from a single string to a list of strings.
#
def _convert_public_orgs(config):
    orgs = []
    for org in config['public_orgs'].split(','):
        orgs.append(org.strip())
    config['public_orgs'] = orgs


def _config_logger(args):
    log_level = logging.WARNING
    log_level_name = 'WARNING'

    if args.log is not None:
        log_level = getattr(logging, args.log.upper())
        log_level_name = args.log.upper()

    if args.console:
        logging.basicConfig(level=log_level)
    else:
        logging.basicConfig(filename='output.log', level=log_level)

    ingest_logger.info('Logging Level set to: ' + log_level_name)


def main(args):
    _config_logger(args)
    config = _read_config(args)

    ingest_logger.info('Ingesting data using this configuration ==== %s', config)

    if config['env'] == 'ALL':
        ingest_logger.info('Processing Enterprise GitHub systems...')
        config['env'] = 'ENTERPRISE'
        results = _process_enterprise_orgs_users(config)
        ingest_logger.info('Done processing Enterprise GitHub systems')

        ingest_logger.info('Processing Public GitHub systems...')
        config['env'] = 'PUBLIC'
        results.extend(_process_public_orgs(config))
        ingest_logger.info('Done processing Public GitHub systems')

        config['env'] = 'ALL'
    elif config['env'] == 'ENTERPRISE':
        ingest_logger.info('Processing Enterprise GitHub systems...')
        results = _process_enterprise_orgs_users(config)
        ingest_logger.info('Done processing %s Enterprise GitHub systems', len(results))
    elif config['env'] == 'PUBLIC':
        ingest_logger.info('Processing Public GitHub systems...')
        results = _process_public_orgs(config)
        ingest_logger.info('Done processing Public GitHub systems')
    else:
        raise ValueError('Unrecognized Environment for Excecution [%s]', config['env'])

    ingest_logger.info('Writing to file: %s', config['data_output_file'])
    _write_data_to_file(config, results)
    ingest_logger.info('Finished writing file.  Processing complete!')


def _parse_commandline():
    parser = argparse.ArgumentParser()

    parser.add_argument('-log', '--log',
                        help='set the LOG_LEVEL [default: WARNING]',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    parser.add_argument('-console', '--console',
                        help='write logs to console. Omit if you want logs written to "output.log"',
                        action='store_true')

    parser.add_argument('-env', '--env',
                        help='the environment to ingest data from [default: ENTERPRISE]',
                        choices=['ALL', 'PUBLIC', 'ENTERPRISE'])

    parser.add_argument('-config', '--config',
                        help='the config file to use for the program [default: ingest.conf]')

    return parser.parse_args()


if __name__ == '__main__':
    main(_parse_commandline())
