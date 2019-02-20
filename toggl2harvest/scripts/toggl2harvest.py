import logging
import os
from os.path import expanduser
from datetime import datetime, timedelta
from pathlib import Path

import click

# from toggl2harvest.harvest import HarvestCredentials, HarvestSession
from toggl2harvest import harvest
from toggl2harvest.utils import (
    calc_total_time,
    cred_file_path,
    data_file_path,
    delta_hours,
    fmt_timedelta,
    generate_selected_days,
    parse_start_end,
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


def get_toggl_cred(config):
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



@cli.command()
@click.option('--start', default=str(datetime.today()))
@click.option('--end', default=str(datetime.today()))
@pass_config
def download_toggl_data(config, start, end):
    start = dateutil_parser.parse(start)
    end = dateutil_parser.parse(end)

    cred_file_p = cred_file_path(config.config_dir)

    toggl_cred = get_toggl_cred(config)
    toggl_api = toggl.TogglSession(toggl_cred)

    with YAML() as yaml:
        cred_file = yaml.load(cred_file_p)
        print(cred_file)
        cred_file_toggl = cred_file['toggl']
        toggl_params = cred_file_toggl['params']

    toggl_time_entries = toggl_api.retrieve_time_entries(
        start,
        end,
        params=toggl_params)

    toggl_time_entries.sort(key=lambda x: x['start'])

    daily_time_entries = {}
    for toggl_entry in toggl_time_entries:
        start_date = toggl_entry['start'][:10]

        while True:
            try:
                days_entries = daily_time_entries[start_date]['entries']
                days_unqiue_map = daily_time_entries[start_date]['unique_map']
            except KeyError:
                daily_time_entries[start_date] = {
                    'entries': [],
                    'unique_map': {},
                }
                continue
            break

        toggl_key = (
            toggl_entry['project'],
            toggl_entry['task'],
            toggl_entry['description'],
            toggl_entry['is_billable'],
        )

        try:
            entry = days_unqiue_map[toggl_key]
            entry['time_entries'].append(
                {
                    's': toggl_entry['start'],
                    'e': toggl_entry['end'],
                }
            )
        except KeyError:
            entry = {
                'project_code': None,
                'harvest_task_name': None,
                'description': toggl_entry['description'],
                'is_billable': toggl_entry['is_billable'],
                'total_time': None,
                'time_entries': [
                    {
                        's': toggl_entry['start'],
                        'e': toggl_entry['end'],
                    }
                ],
                'toggl': {
                    'project': toggl_entry['project'],
                    'task': toggl_entry['task'],
                    'is_billable': toggl_entry['is_billable'],
                },
                'harvest': {
                    'project_id': None,
                    'task_id': None,
                }
            }
            days_unqiue_map[toggl_key] = entry
            days_entries.append(entry)
        # Always recalculate total time
        total_time = calc_total_time(entry['time_entries'])
        entry['total_time'] = fmt_timedelta(total_time)

    # Write out raw yaml for the dates
    for day, day_entries in daily_time_entries.items():
        # TODO: Check that date hasn't been opened before
        with YAML(output=data_file_path(config, day)) as yaml:
            for entry in day_entries['entries']:
                yaml.dump(entry)


@cli.command()
@click.option('--start', default=str(datetime.today()))
@click.option('--end', default=str(datetime.today()))
@pass_config
def validate_data(config, start, end):
    start_date, end_date = parse_start_end(start, end)
    selected_days = generate_selected_days(start_date, end_date)

    # Get project mapping
    project_file = os.path.join(config.config_dir, 'project_mapping.yml')
    with YAML() as yaml:
        PROJECT_MAPPING = yaml.load(Path(project_file))

    def get_harvest_project(project_code):
        return PROJECT_MAPPING[project_code]['harvest_project']

    # Get Harvest Cache
    HARVEST_CACHE = harvest.HarvestSession.read_project_cache(
        config.config_dir)

    for proj_id, proj in HARVEST_CACHE.items():
        proj['task_names'] = {}
        task_names = proj['task_names']

        for task_id, task_name in proj['tasks'].items():
            task_names[task_name] = task_id

    def get_harvest_task(proj_id, task_name):
        return HARVEST_CACHE[proj_id]['task_names'][task_name]

    # Loop through and recalculate total time, verify other things?
    for day in selected_days:
        day_file = data_file_path(config, day)
        tmp_file = day_file.with_suffix('.yml.tmp')

        # Run though and check file, re-edit until it's valid
        file_valid = False
        file_rounds = 0
        while not file_valid:
            # Check file
            file_errors = 0
            with YAML(output=tmp_file) as yaml:
                for i, data in enumerate(yaml.load_all(day_file)):
                    if data['time_entries'] is None:
                        log.debug(f'time entries is null for entry {i}')
                        continue  # If there are no time entries, move to next
                    total_time = calc_total_time(data['time_entries'])
                    data['total_time'] = fmt_timedelta(total_time)

                    # Only set these if they aren't already set

                    try:
                        if data['harvest']['project_id'] is None:
                            log.debug('harvest.project_id not found')
                            proj_code = data['project_code']
                            try:
                                harvest_proj = get_harvest_project(proj_code)
                            except KeyError as e:
                                file_errors += 1
                                if str(e) == 'None' and file_rounds != 0:
                                    log.info(f'Project missing for entry {i}')
                                elif file_rounds != 0:
                                    log.info(f'Project "{str(e)}" not found')
                                raise

                            data['harvest']['project_id'] = harvest_proj
                        else:
                            harvest_proj = data['harvest']['project_id']
                        if data['harvest']['task_id'] is None:
                            log.debug('harvest.task_id not found')
                            task_name = data['harvest_task_name']
                            try:
                                harvest_task = get_harvest_task(
                                    harvest_proj, task_name)
                            except KeyError as e:
                                file_errors += 1
                                if str(e) == 'None' and file_rounds != 0:
                                    log.info(f'Task missing for entry {i}')
                                elif file_rounds != 0:
                                    log.info(f'Task "{str(e)}" not found in project')
                                raise
                            data['harvest']['task_id'] = harvest_task
                    except KeyError:
                        pass

                    yaml.dump(data)
            day_file.unlink()
            tmp_file.rename(day_file)
            log.debug(f'file errors: {file_errors}')
            # Edit file to update
            file_valid = file_errors == 0
            file_rounds += 1
            if click.confirm(f'{day} is {"valid" if file_valid else "invalid"}'
                             f'. Edit file?'):
                click.edit(filename=day_file)


@cli.command()
@click.option('--start', default=str(datetime.today()))
@click.option('--end', default=str(datetime.today()))
@pass_config
def upload_to_harvest(config, start, end):
    start_date, end_date = parse_start_end(start, end)
    selected_days = generate_selected_days(start_date, end_date)

    harvest_cred = get_harvest_cred(config)
    config.harvest_api = harvest.HarvestSession(harvest_cred)

    entries = {}
    for day in selected_days:
        day_file = data_file_path(config, day)
        entries[day] = []
        with YAML() as yaml:
            for data in yaml.load_all(day_file):
                total_time = calc_total_time(data['time_entries'])
                entries[day].append({
                    'project_id': data['harvest']['project_id'],
                    'task_id': data['harvest']['task_id'],
                    'spent_date': day,
                    'hours': delta_hours(total_time),
                    'notes': data['description'],
                })

    for day in selected_days:
        for i, entry in enumerate(entries[day]):
            config.harvest_api.create_time_entry(
                **entry
            )
            log.info(f'Uploaded {day}#{i}')
