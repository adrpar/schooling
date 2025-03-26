import click
from cli.mathrally import mathrally
from cli.addsub import addsub

@click.group()
def cli():
    """CLI tool for math rally and add/sub operations."""
    pass

cli.add_command(mathrally)
cli.add_command(addsub)

if __name__ == "__main__":
    cli()
