import argparse
import json
import logging
from re import sub

log = logging.getLogger('github-data-ingestion')

def _read_config(args):
    config_filename = 'auth_config.conf'
    config = {}

    if args.config is not None:
        config_filename = args.config

    log.info('Reading configuration file (' + config_filename + ') ...')

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
        logging.basicConfig(filename='project_dependency.log', level=log_level)

    log.info('Logging Level set to: ' + log_level_name)

def main(args):
    _config_logger(args)
    config = _read_config(args)
    return config
