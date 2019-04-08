# Standard Library
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

# Third Party Packages
from dateutil import parser as dateutil_parser
from ruamel.yaml import YAML


log = logging.getLogger(__name__)


def iso_date(time_value):
    return time_value.strftime('%Y-%m-%d')


def iso_timestamp(time_value):
    return time_value.strftime('%Y-%m-%dT%H:%M:%S%z')


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


def operate_on_day_data(input, output, operate, **kwargs):
    ctx = {}
    with YAML(output=output) as yaml:
        for i, data in enumerate(yaml.load_all(input)):
            updated_data, ctx = operate(i, data, **kwargs)
            yaml.dump(updated_data)
    return ctx


class AtomicFileUpdate():

    def __init__(self, filename):
        self.filename = filename
        self._commit = False

    def __enter__(self):
        self.input = open(self.filename, 'r')
        if isinstance(self.filename, Path):
            self.tmp_filename = Path(
                self.filename.parent,
                self.filename.name + '.tmp')
        else:
            self.tmp_filename = self.filename + '.tmp'
        self.output = open(self.tmp_filename, 'w')
        return self

    def __exit__(self, *args):
        self.input.close()

        self.output.flush()
        os.fsync(self.output.fileno())
        self.output.close()

        if self._commit:
            os.rename(self.tmp_filename, self.filename)
        else:
            os.remove(self.tmp_filename)

    def commit(self):
        self._commit = True
