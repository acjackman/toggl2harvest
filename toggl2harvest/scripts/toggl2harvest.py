import logging
import os
from os.path import expanduser
from datetime import datetime, timedelta
from pathlib import Path

import click

# from toggl2harvest.harvest import HarvestCredentials, HarvestSession
from toggl2harvest import harvest
from toggl2harvest.utils import (
    cred_file_path,
    fmt_timedelta,
    delta_hours,
    calc_total_time,
    data_file_path,
)

log = logging.getLogger(__name__)


class Config(object):

    def __init__(self):
        self.config_dir = None


pass_config = click.make_pass_decorator(Config, ensure=True)

def get_config_dir(config_dir):
    env_config = os.environ.get('TOGGL2HARVEST_CONFIG')
    log.debug(env_config)
    if config_dir is not None:
        log.debug('Set config_dir from option')
        return expanduser(config_dir)
    elif env_config is not None :
        log.debug('Set from env_config')
        return expanduser(env_config)

    log.debug('Default config dir used')
    return '.'


def get_harvest_cred(config):
    cred_file = cred_file_path(config.config_dir)
    if not cred_file.is_file():
        log.debug('Credentials file does not exist')
        raise ValueError('Credentials file does not exist')

    try:
        harvest_cred = harvest.HarvestCredentials.read_from_file(cred_file)
    except Exception as e:
        log.debug('exception caught.', exc_info=True)
        log_msg = 'Could not load Harvest credentials.'
        if isinstance(e, FileNotFoundError):
            cred_file_str = click.format_filename(cred_file)
            log_msg += (
                f' Does the "{cred_file_str}" file exist?'
            )
        if isinstance(e, TypeError) or isinstance(e, KeyError):
            cred_file_str = click.format_filename(cred_file)
            log_msg += (
                f' Credentials file structure does not look right.'
            )
        log.error(log_msg)
        raise  # re-raise the exception so we get a bad exit code



@click.group()
@click.option('--config-dir', type=click.Path())
@click.version_option()
@pass_config
def cli(config, config_dir):
    # Set the config directory
    config.config_dir = get_config_dir(config_dir)


@cli.command()
@pass_config
def info(config):
    click.echo(f'Configuration Directory: "{config.config_dir}"')


@cli.command()
@pass_config
def harvest_cache(config):
    harvest_cred = get_harvest_cred(config)
    harvest_api = harvest.HarvestSession(harvest_cred)
    try:
        harvest_api.update_project_cache(config.config_dir)
    except Exception as e:
        log.debug('exception caught.', exc_info=True)
        log_msg = 'Could not make connect to the Harvest API.'
        log.error(log_msg)
