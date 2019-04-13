# Standard Library
import logging
from datetime import datetime

# Third Party Packages
import click
from dateutil.parser import parse as parse_date

from toggl2harvest.app import TogglHarvestApp
from toggl2harvest.exceptions import InvalidFileError
from toggl2harvest.utils import generate_selected_days


log = logging.getLogger(__name__)


def parse_start_end(start, end):
    try:
        start_date = parse_date(start)
    except ValueError:
        raise click.ClickException(f'"{start}" is not a valid start date')
    try:
        end_date = parse_date(end)
    except ValueError:
        raise click.ClickException(f'"{end}" is not a valid end date')
    return start_date, end_date


@click.group()
@click.option('--config-dir', type=click.Path(), envvar='TOGGL2HARVEST_CONFIG')
@click.version_option()
@click.pass_context
def cli(ctx, config_dir):
    ctx.obj = TogglHarvestApp(config_dir=config_dir)


@cli.command()
@click.pass_obj
def info(app):
    click.echo(f'Configuration Directory: "{app.config_dir}"')


@cli.command()
@click.pass_obj
def harvest_cache(app):
    app.cache_harvest_projects()
    click.echo('cached projects')


@cli.command()
@click.option('--start', default=f'{datetime.today():%Y-%m-%d}')
@click.option('--end', default=f'{datetime.today():%Y-%m-%d}')
@click.pass_obj
def download_toggl_data(app, start, end):
    start_date, end_date = parse_start_end(start, end)
    app.download_toggl_data(start_date, end_date)


@cli.command()
@click.option('--start', default=f'{datetime.today():%Y-%m-%d}')
@click.option('--end', default=f'{datetime.today():%Y-%m-%d}')
@click.pass_obj
def validate_time_logs(app, start, end):
    start_date, end_date = parse_start_end(start, end)
    selected_days = generate_selected_days(start_date, end_date)

    _validate_time_logs(app, selected_days)


def _validate_time_logs(app, selected_days):
    for day in selected_days:
        day_file = app.data_file(day)

        # Run though and check file, re-edit until it's valid
        file_valid = False
        while not file_valid:
            file_errors = app.validate_file(day_file)
            file_valid = file_errors == 0
            message = 'Is valid.' if file_valid else f'Has {file_errors} invalid entries.'
            click.echo(f'{day} | {message}', nl=file_valid)
            if not file_valid and click.confirm(' Edit file?'):
                click.edit(filename=day_file)


@cli.command()
@click.option('--start', default=f'{datetime.today():%Y-%m-%d}')
@click.option('--end', default=f'{datetime.today():%Y-%m-%d}')
@click.pass_obj
def upload_to_harvest(app, start, end):
    start_date, end_date = parse_start_end(start, end)
    selected_days = generate_selected_days(start_date, end_date)

    _upload_to_harvest(app, selected_days)


def _upload_to_harvest(app, selected_days):
    for day in selected_days:
        try:
            messages = app.upload_to_harvest(day)
            for i, message in enumerate(messages):
                click.echo(f'{day}#{i:02d}: {message}')
        except InvalidFileError as e:
            click.echo(f'{day}#{e.message}')


@cli.command()
@click.option('--start', default=f'{datetime.today():%Y-%m-%d}')
@click.option('--end', default=f'{datetime.today():%Y-%m-%d}')
@click.pass_obj
def timesheet(app, start, end):
    start_date, end_date = parse_start_end(start, end)
    selected_days = generate_selected_days(start_date, end_date)

    app.download_toggl_data(start_date, end_date)
    _validate_time_logs(app, selected_days)

    if click.confirm(f'Upload data for {start} though {end} to Harvest?'):
        _upload_to_harvest(app, selected_days)
