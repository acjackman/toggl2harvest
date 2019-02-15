import logging
import os

import click
import click_log

# from toggl2harvest.harvest import HarvestCredentials, HarvestSession
from toggl2harvest import harvest


log = logging.getLogger(__name__)
click_log.basic_config(log)


class Config(object):

    def __init__(self):
        self.verbose = False
        self.config_dir = '~/.toggl2harvest'


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-q', '--quiet', is_flag=True, help='overrides verbose.')
@click.option('--config-dir', type=click.Path())
@click.version_option()
@pass_config
def cli(config, verbose, quiet, config_dir):
    config.verbose = verbose

    if quiet:
        log.setLevel(logging.ERROR)
    elif verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # Set the config directory
    env_config = os.environ.get('TOGGL2HARVEST_CONFIG')
    if config_dir is not None:
        log.debug('Set config_dir from option')
        config.config_dir = config_dir
    elif env_config is not None and os.path.isdir(env_config):
        log.debug('Set config_dir from environment variable')
        config.config_dir = env_config
    else:
        log.debug('Set config_dir by default')


@cli.command()
@pass_config
def harvest_cache(config):
    cred_file = os.path.join(config.config_dir, 'credentials.yaml')
    try:
        credentials = harvest.HarvestCredentials.read_from_file(cred_file)
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
    harvest_api = harvest.HarvestSession(credentials)
    try:
        harvest_api.update_project_cache(config.config_dir)
    except Exception as e:
        log.debug('exception caught.', exc_info=True)
        log_msg = 'Could not make connect to the Harvest API.'
        log.error(log_msg)


@cli.command()
@pass_config
def info(config):
    config_file_str = click.format_filename(config.config_dir)
    log.info(f'Configuration Directory: "{config_file_str}"')
