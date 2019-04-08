# Standard Library
import logging
from datetime import datetime

# Third Party Packages
import click
from dateutil.parser import parse as parse_date

from toggl2harvest.app import TogglHarvestApp


log = logging.getLogger(__name__)


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
@click.option('--start', default=lambda: f'{datetime.today():%Y-%m-%d}')
@click.option('--end', default=lambda: f'{datetime.today():%Y-%m-%d}')
@click.pass_obj
def download_toggl_data(app, start, end):
    try:
        start_date = parse_date(start)
    except ValueError:
        raise click.ClickException(f'"{start}" is not a valid start date')
    try:
        end_date = parse_date(end)
    except ValueError:
        raise click.ClickException(f'"{end}" is not a valid end date')
    app.download_toggl_data(start_date, end_date)
