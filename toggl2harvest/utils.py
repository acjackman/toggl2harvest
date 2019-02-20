import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

import click
from dateutil import parser as dateutil_parser


log = logging.getLogger(__name__)


def cred_file_path(config_dir):
    return Path(os.path.join(config_dir, 'credentials.yaml'))


def strp_iso8601(datetime_str):
    correct_format = datetime_str[:22] + datetime_str[23:]
    return datetime.strptime(correct_format, '%Y-%m-%dT%H:%M:%S%z')


HOUR_IN_SECONDS = 3600
MINUTE_IN_SECONDS = 60


def fmt_timedelta(delta):
    # click.echo(f'seconds: {delta.seconds}')
    hours = delta.days * 24 + (delta.seconds // HOUR_IN_SECONDS)
    minutes = (delta.seconds % HOUR_IN_SECONDS) // MINUTE_IN_SECONDS
    # seconds = delta.seconds % MINUTE_IN_SECONDS
    formatted = f'{hours}:{minutes:02}'
    # click.echo(formatted)
    return formatted


def delta_hours(delta):
    return delta.days * 24 + (delta.seconds / HOUR_IN_SECONDS)


def calc_total_time(time_entries):
    total_time = timedelta()
    for entry in time_entries:
        start = strp_iso8601(entry['s'])
        end = strp_iso8601(entry['e'])
        # TODO if start > end
        total_time += end - start
    return total_time


def data_file_path(config, date_str):
    return Path(os.path.join(config.config_dir, 'data', f'{date_str}.yml'))


def parse_start_end(start, end):
    start_date = dateutil_parser.parse(start)
    end_date = dateutil_parser.parse(end)
    return (start_date, end_date)


def generate_selected_days(start, end):
    selected_days = [start]
    while selected_days[-1] < end:
        selected_days.append(selected_days[-1] + timedelta(hours=24))
    selected_days = [d.strftime('%Y-%m-%d') for d in selected_days]
    return selected_days
