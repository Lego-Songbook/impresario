import click

from impresario import song


@click.group()
def main():
    pass


@click.group()
def songbook():
    pass


@click.group()
def setlist():
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
