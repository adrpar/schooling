import click
from importlib import import_module
from pathlib import Path


@click.group()
def cli():
    """CLI tool for math rally and add/sub operations."""
    pass


# Dynamically load commands from the cli package
for file in Path("cli").glob("*.py"):
    if file.stem != "__init__":
        module = import_module(f"cli.{file.stem}")
        cli.add_command(getattr(module, file.stem))

if __name__ == "__main__":
    cli()
