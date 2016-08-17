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


def _ingest_org_data(config):
    orgs = _get_orgs(config)
    repos_result = []

    for org in orgs:
        repos_response = requests.get(org['repos_url'] + '?' + _get_auth_http_params(config))
        repos = json.loads(repos_response.text)
        ingest_logger.info(repos)

        for repo in repos:
            repo_info = {}
            repo_name = None
            org_name = None
            proj_desc = None
            proj_lang = None
            num_stars = None
            num_watchers = None
            num_forks = None

            if repo['name'] is not None:
                repo_name = repo['name'].encode('utf-8')
            if repo['full_name'] is not None:
                org_name = repo['full_name'].encode('utf-8').split('/', 1)[0]
            if repo['description'] is not None:
                proj_desc = repo['description'].encode('utf-8')
            if repo['language'] is not None:
                proj_lang = repo['language'].encode('utf-8')
            if repo['stargazers_count'] is not None:
                num_stars = repo['stargazers_count']
            if repo['watchers_count'] is not None:
                num_watchers = repo['watchers_count']
            if repo['forks'] is not None:
                num_forks = repo['forks']

            contributors = _get_contributors_info(config, org, repo_name)
            num_releases = _count_releases(config, org, repo_name)
            readme_results = _get_readme_info(config, org, repo_name)

            repo_info['repository'] = repo_name
            repo_info['full_name'] = org_name + '/' + repo_name
            repo_info['project_name'] = repo_name
            repo_info['organization'] = org_name
            repo_info['project_description'] = proj_desc
            repo_info['language'] = proj_lang
            repo_info['stars'] = num_stars
            repo_info['watchers'] = num_watchers
            repo_info['contributors'] = contributors['num_contributors']
            repo_info['commits'] = contributors['num_commits']
            repo_info['releases'] = num_releases
            repo_info['forks'] = num_forks
            repo_info['rank'] = num_stars + num_watchers + contributors['num_contributors'] + contributors['num_commits'] + num_releases
            repo_info['content'] = readme_results['readme_contents']
            repo_info['readme_url'] = readme_results['readme_url']
            repo_info['contributors_list'] = contributors['contributors']
            repo_info['suggest'] = _get_suggest_info(repo_name, proj_desc)

            repos_result.append(repo_info)

    return repos_result

#
# The access method for github is different for each system.  Both modes should be accepted soon.
#
# If Enterprise then we use the Personal Access Token otherwise an OAuth token pair.
#


def _get_auth_http_params(config):
    if config['env'] == 'ENTERPRISE':
        return 'access_token=' + config['enterprise_github_access_token']
    else:
        return 'client_id=' + config['github_oauth_client_id'] +\
               '&client_secret=' + config['github_oauth_client_secret']

#
# The API URL for each system differs and this method returns the correct one as determined by the env property.
#


def _get_github_url(config):
    if config['env'] == 'ENTERPRISE':
        return config['enterprise_github_api_url']
    else:
        return config['public_github_api_url']


def _get_orgs(config):
    if config['env'] == 'ENTERPRISE':
        return _get_enterprise_orgs(config)
    else:
        return _get_public_orgs(config)


def _get_enterprise_orgs(config):
    orgs_response = requests.get(_get_github_url(config) + '/organizations?' + _get_auth_http_params(config))
    orgs = json.loads(orgs_response.text)
    ingest_logger.info(orgs)

    return orgs


def _get_public_orgs(config):
    orgs_json = []
    for org in config['public_orgs']:
        orgs_response = requests.get(_get_github_url(config) + '/orgs/' + org + '?' + _get_auth_http_params(config))
        orgs_json.append(json.loads(orgs_response.text))

    ingest_logger.info(orgs_json)
    return orgs_json


#
# Calculate:
#   Number of Commits by all Contributors
#   Number of Contributors
#   List of Contributors
#


def _get_contributors_info(config, org, repo_name):
    contribs_response = requests.get(_get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name + '/contributors?anon=true&' + _get_auth_http_params(config))

    num_contributors = 0
    num_commits = 0
    contributor_list = []
    if contribs_response.text != '':
        contributors = json.loads(contribs_response.text)

        for contributor in contributors:
            num_contributors += 1
            num_commits += contributor['contributions']
            contributor_info = {}
            # If user is anonymous, they do not have
            if contributor['type'] == 'User':
                contributor_info['username'] = contributor['login']
                contributor_info['profile_url'] = contributor['html_url']
            else:
                contributor_info['username'] = contributor['name']
                contributor_info['profile_url'] = None

            contributor_list.append(contributor_info)

    return {'num_commits': num_commits, 'num_contributors': num_contributors, 'contributors': contributor_list}


#
# Process README content and url
#


def _get_readme_info(config, org, repo_name):
    readme_response = requests.get(_get_github_url(config) + '/repos/' + org['login'] + '/' + repo_name +
                                   '/contents/README.md?' + _get_auth_http_params(config))
    readme_response = json.loads(readme_response.text)
    readme_results = {'readme_contents': '', 'readme_url': ''}

    if not readme_response.has_key('documentation_url'):
        readme_results['readme_contents'] = base64.b64decode(readme_response['content'])
        readme_results['readme_url'] = readme_response['download_url']

    return readme_results


def _get_suggest_info(repo_name, proj_desc):
    suggest = '{"input": ["' + sub("[^a-zA-Z0-9\s]", '', repo_name) + '", "' + \
              sub("[^a-zA-Z0-9\s]", '', proj_desc) + '"], "output": "' + \
              sub("[^a-zA-Z0-9-\s]", '', repo_name) + '"}'
    return json.loads(suggest)


def _count_releases(config, org, repo_name):
    releases = requests.get(_get_github_url(config) +
                            '/repos/' +
                            org['login'] + '/' + repo_name +
                            '/releases?' +
                            _get_auth_http_params(config))
    releases = json.loads(releases.text)

    num_releases = 0
    for release in releases:
        num_releases += 1

    return num_releases


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
        results = _ingest_org_data(config)
        ingest_logger.info('Done processing Enterprise GitHub systems')

        ingest_logger.info('Processing Public GitHub systems...')
        config['env'] = 'PUBLIC'
        results.append(_ingest_org_data(config))
        ingest_logger.info('Done processing Public GitHub systems')

        config['env'] = 'ALL'
    else:
        ingest_logger.info('Processing only %s GitHub system...', config['env'])
        results = _ingest_org_data(config)
        ingest_logger.info('Done processing only %s GitHub system', config['env'])

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
