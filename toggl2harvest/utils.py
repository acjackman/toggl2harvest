# Standard Library
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

# Third Party Packages
from dateutil import parser as dateutil_parser
from ruamel.yaml import YAML


log = logging.getLogger(__name__)


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


def parse_start_end(start, end):
    start_date = dateutil_parser.parse(start)
    end_date = dateutil_parser.parse(end)
    return (start_date, end_date)


def generate_selected_days(start, end):
    selected_days = [start]
    while selected_days[-1].date() < end.date():
        selected_days.append(selected_days[-1] + timedelta(hours=24))
    selected_days = [d.strftime('%Y-%m-%d') for d in selected_days]
    return selected_days


def operate_on_day_data(day_file, operate, **kwargs):
    tmp_file = day_file.with_suffix('.yml.tmp')

    with YAML(output=tmp_file) as yaml:
        for i, data in enumerate(yaml.load_all(day_file)):
            data, ctx = operate(i, data, **kwargs)
            yaml.dump(data)

    day_file.unlink()
    tmp_file.rename(day_file)
    return ctx
