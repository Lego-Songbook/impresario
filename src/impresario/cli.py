"""
Command-line interface.

$ impresario
"""

import click

from impresario import song
from impresario.config import Config


@click.group()
def main():
    pass


@click.group()
@click.option("--site", prompt=True)
@click.option("--sheets", prompt=True)
def init(site, sheets):
    """Initialize impresario."""
    Config(site=site, sheets=sheets)
    click.echo("The app is properly configured.")


@click.group()
def songbook():
    # configs = Config.load()
    pass

@click.group()
def setlist():
    pass


@click.group()
def new():
    pass


@new.command("setlist")
def _new_setlist():
    pass


@new.command("song")
def _new_song():
    pass


@songbook.command("sync")
@click.option("--site", required=True)
@click.option("--sheet", required=True)
def _songbook_sync(site, sheet):
    click.echo(f"Site directory: {site}")
    click.echo(f"Sheet directory: {sheet}")
    if song.sync_songbook(site, sheet):
        click.echo("Successfully synced the songbooks!")
        return
    else:
        click.echo("Fail to sync the songbooks.")


@songbook.command("missing")
@click.option("--site", required=True)
@click.option("-c", "--column", required=True)
def _songbook_show_missing(site, column):
    click.echo(song.show_missing_songs(site, column))


main.add_command(songbook)
main.add_command(setlist)
main.add_command(new)
main.add_command(init)
