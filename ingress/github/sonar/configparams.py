import argparse
import json
import logging
from re import sub

def _read_config(args):
    config_filename = 'ingest.conf'
    config = {}

    if args.config is not None:
        config_filename = args.config

    logging.info('Reading configuration file (' + config_filename + ') ...')

    with open(config_filename, 'r') as config_file:
        for line in config_file.read().splitlines():
            if not line.startswith('#'):
                prop = line.split('=')
                if len(prop) == 2:
                    config[prop[0].strip()] = prop[1].strip()

    if ('env' in args) and (args.env is not None):
        config['env'] = args.env.upper()
    else:
        config['env'] = 'PUBLIC_AND_ENTERPRISE'

    if ('sonar_server' in args) and (args.sonar_server is not None):
        config['sonar_server'] = args.sonar_server
    if ('install_sonar_server' in args) and (args.install_sonar_server is not None):
        config['install_sonar_server'] = args.install_sonar_server
    if ('install_sonar_runner' in args) and (args.install_sonar_server is not None):
        config['install_sonar_runner'] = args.install_sonar_runner
    if ('install_plugins' in args) and (args.install_plugins is not None):
        config['install_plugins'] = args.install_plugins
    _convert_public_orgs(config)
    _convert_sonar_metrics(config)

    return config

def _write_update(args):

    if not args.update:
        file_or_es = 'results.out'
    else:
        file_or_es = args.update
    return file_or_es


def _parse_commandline():
    parser = argparse.ArgumentParser()

    parser.add_argument('-config', '--config',
                        help='the config file to use for the program [default: ingest.conf]')

    parser.add_argument('-env', '--env',
                        help='the config file to use for the program [default: ingest.conf]')

    parser.add_argument('-update', '--update',
                        help='dependencies result will either be written to a file or ES will be updated [default: results.out]',
                        action='store_true')
    parser.add_argument('-sonar_server', '--sonar_server',
                        help='determine to communicate either local or remote sonar server [default: local]',
                        action='store_true')
    parser.add_argument('-install_sonar_server', '--install_sonar_server',
                        help='determine to install sonar server [default: false]',
                        action='store_true')
    parser.add_argument('-install_sonar_runner', '--install_sonar_runner',
                        help='determine to install sonar runner [default: false]',
                        action='store_true')

    parser.add_argument('-install_plugins', '--install_plugins',
                        help='determine to install whether to install sonar plugins [default: false]',
                        action='store_true')
    return parser.parse_args()


def _convert_public_orgs(config):
    orgs = []
    for org in config['public_orgs'].split(','):
        orgs.append(org.strip())
    config['public_orgs'] = orgs

def _convert_sonar_metrics(config):
    metrics = []
    for metric in config['sonar_health_metrics'].split(','):
        metrics.append(metric.strip())
    config['sonar_health_metrics'] = metrics

def main(args):
    config_update = {}
    logging.basicConfig(filename='project_dependency.log', level=logging.INFO)
    config_update['config'] = _read_config(args)
    config_update['update'] = _write_update(args)
    return config_update
