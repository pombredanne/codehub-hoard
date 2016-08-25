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
        config['env'] = 'PUBLIC'

    _convert_public_orgs(config)

    return config

def _write_update(args):
    file_or_es = 'results.out'

    if args.update is not None:
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

    return parser.parse_args()


def _convert_public_orgs(config):
    orgs = []
    for org in config['public_orgs'].split(','):
        orgs.append(org.strip())
    config['public_orgs'] = orgs

def main(args):
    config_update = {}
    logging.basicConfig(filename='project_dependency.log', level=logging.INFO)
    config_update['config'] = _read_config(args)
    config_update['update'] = _write_update(args)
    return config_update
