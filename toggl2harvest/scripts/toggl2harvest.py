# Standard Library
import logging

# Third Party Packages
import click

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
